#!/usr/bin/env python3
"""Read-only iFlow structural inventory. SAP extension values need manual review."""

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

BPMN = "http://www.omg.org/spec/BPMN/20100524/MODEL"
MAX_FILES = 2000
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
SCHEMA_VERSION = 1


class InventoryError(ValueError):
    """Input cannot be inventoried completely within supported boundaries."""


def safe_name(name):
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or ".." in path.parts
            or "\\" in name or ":" in name
            or any(ord(c) < 32 for c in name)):
        raise InventoryError("Unsafe archive member path")
    return path.as_posix()


def read_bounded(stream):
    data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise InventoryError("File exceeds local size limit")
    return data


def source_members(source):
    """Yield relative path and bytes, never extracting or executing inputs."""
    source = Path(source)
    if source.is_symlink():
        raise InventoryError("Symlink inputs are unsupported")
    if source.is_dir():
        count = 0
        for member in sorted(source.rglob("*")):
            if member.is_symlink():
                raise InventoryError("Symlink members are unsupported")
            if member.is_dir():
                continue
            if not member.is_file():
                raise InventoryError("Non-regular members are unsupported")
            count += 1
            if count > MAX_FILES:
                raise InventoryError("Too many files")
            with member.open("rb") as stream:
                yield member.relative_to(source).as_posix(), read_bounded(stream)
    elif source.is_file() and source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_FILES:
                raise InventoryError("Too many archive members")
            if sum(item.file_size for item in entries) > MAX_TOTAL_BYTES:
                raise InventoryError("Archive exceeds total size limit")
            seen = set()
            for item in sorted(entries, key=lambda entry: entry.filename):
                name = safe_name(item.filename)
                if name in seen:
                    raise InventoryError("Duplicate archive member path")
                seen.add(name)
                mode = stat.S_IFMT(item.external_attr >> 16)
                if mode not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise InventoryError("Non-regular archive member")
                if item.flag_bits & 1:
                    raise InventoryError("Encrypted archive members are unsupported")
                if item.file_size > MAX_FILE_BYTES:
                    raise InventoryError("Archive member exceeds local size limit")
                if not item.is_dir():
                    with archive.open(item) as stream:
                        yield name, read_bounded(stream)
    elif source.is_file() and source.suffix.lower() == ".iflw":
        with source.open("rb") as stream:
            yield source.name, read_bounded(stream)
    else:
        raise InventoryError("Expected a ZIP, extracted directory, or .iflw file")


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def property_keys(element):
    keys = set()
    for child in element:
        if child.tag == "{" + BPMN + "}extensionElements":
            for prop in child.iter():
                if local_name(prop.tag) == "property":
                    for key in prop:
                        if local_name(key.tag) == "key" and key.text:
                            keys.add(key.text.strip())
    return sorted(keys)


def inspect_model(path, data):
    # Removing NULs also detects declarations in UTF-16/32 inputs.
    if re.search(br"<!\s*(DOCTYPE|ENTITY)\b", data.replace(b"\x00", b""), re.I):
        raise InventoryError("DTD/entity declarations are unsupported")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise InventoryError("Malformed iFlow XML: " + str(exc)) from exc
    model = {"path": path, "elements": [], "edges": [], "warnings": []}
    ids = set()
    stack = [(root, None)]
    model_elements = 0
    while stack:
        element, scope = stack.pop()
        next_scope = scope
        if element.tag.startswith("{" + BPMN + "}"):
            model_elements += 1
            kind = local_name(element.tag)
            identifier = element.get("id")
            if identifier:
                if identifier in ids:
                    model["warnings"].append("Duplicate BPMN ID: " + identifier)
                ids.add(identifier)
                record = {"id": identifier, "type": kind, "scope": scope,
                          "name": element.get("name"),
                          "property_keys": property_keys(element)}
                if kind in ("sequenceFlow", "messageFlow"):
                    record.update(source=element.get("sourceRef"),
                                  target=element.get("targetRef"),
                                  has_condition=any(local_name(c.tag) == "conditionExpression"
                                                    for c in element))
                    model["edges"].append(record)
                else:
                    for key in ("processRef", "calledElement", "attachedToRef", "default"):
                        if key in element.attrib:
                            record[key] = element.attrib[key]
                    model["elements"].append(record)
                if kind in ("process", "subProcess"):
                    next_scope = identifier
        stack.extend((child, next_scope) for child in reversed(list(element)))
    if not model_elements:
        model["warnings"].append("No recognized BPMN model namespace; manual review required")
    elif not ids:
        model["warnings"].append("No ID-bearing BPMN elements; manual review required")
    for edge in model["edges"]:
        for side in ("source", "target"):
            if edge[side] not in ids:
                model["warnings"].append("Unresolved " + side + " on edge " + edge["id"])
    for element in model["elements"]:
        for key in ("processRef", "attachedToRef", "default", "calledElement"):
            if key in element and element[key] not in ids:
                model["warnings"].append("Unresolved " + key + " on " + element["id"]
                                         + "; may reference an external resource")
    return model


def inventory(source):
    result = {"schema_version": SCHEMA_VERSION, "files": [], "models": [], "warnings": []}
    total = 0
    for path, data in source_members(source):
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise InventoryError("Input exceeds total size limit")
        result["files"].append({"path": path, "bytes": len(data),
                                "sha256": hashlib.sha256(data).hexdigest()})
        if path.lower().endswith(".iflw"):
            result["models"].append(inspect_model(path, data))
        if path.lower().endswith(".zip"):
            result["warnings"].append("Nested archive not inspected: " + path)
    if not result["models"]:
        raise InventoryError("No .iflw models found; nested ZIPs are not inspected")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="iFlow ZIP, extracted folder, or .iflw")
    args = parser.parse_args()
    try:
        result = inventory(args.source)
    except (InventoryError, OSError, zipfile.BadZipFile, RuntimeError,
            NotImplementedError, EOFError) as exc:
        print("Inventory failed: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
