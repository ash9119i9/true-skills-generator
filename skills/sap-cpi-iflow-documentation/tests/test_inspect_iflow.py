"""Synthetic structural tests. These do not validate SAP runtime behavior."""

import importlib.util
import json
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_iflow.py"
SPEC = importlib.util.spec_from_file_location("inspect_iflow", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FIXTURE = ROOT / "tests" / "fixtures" / "sample.iflw"


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, members):
        path = self.root / "export.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in members:
                archive.writestr(name, data)
        return path

    def test_graph_uses_explicit_edges_and_preserves_scopes(self):
        model = MODULE.inventory(FIXTURE)["models"][0]
        edges = {edge["id"]: edge for edge in model["edges"]}
        nodes = {node["id"]: node for node in model["elements"]}
        self.assertEqual((edges["first"]["source"], edges["first"]["target"]), ("start", "route"))
        self.assertEqual(edges["handler-edge"]["scope"], "exception")
        self.assertEqual(nodes["local-start"]["scope"], "local")
        self.assertEqual(nodes["call"]["calledElement"], "local")
        self.assertEqual(nodes["route"]["default"], "default-route")
        self.assertEqual(edges["channel"]["type"], "messageFlow")
        self.assertTrue(edges["selected"]["has_condition"])
        self.assertEqual(model["warnings"], [])  # Diagram's reused ID is not a model duplicate.

    def test_property_keys_retained_without_values(self):
        result = MODULE.inventory(FIXTURE)
        serialized = json.dumps(result)
        self.assertNotIn("SECRET_FIXTURE_VALUE", serialized)
        self.assertNotIn("transform.groovy", serialized)
        node = next(n for n in result["models"][0]["elements"] if n["id"] == "transform")
        self.assertEqual(node["property_keys"], ["password", "script"])

    def test_zip_directory_parity_hashes_and_no_source_changes(self):
        data = FIXTURE.read_bytes()
        directory = self.root / "extracted"
        directory.mkdir()
        (directory / "sample.iflw").write_bytes(data)
        script = b"throw new RuntimeException('MUST NOT EXECUTE')"
        (directory / "script.groovy").write_bytes(script)
        archive = self.archive([("sample.iflw", data), ("script.groovy", script)])
        before = archive.read_bytes()
        result = MODULE.inventory(archive)
        self.assertEqual(result, MODULE.inventory(directory))
        self.assertEqual(len(result["files"][0]["sha256"]), 64)
        self.assertEqual(archive.read_bytes(), before)
        self.assertEqual((directory / "sample.iflw").read_bytes(), data)

    def test_multiple_models_stay_separate(self):
        archive = self.archive([("one.iflw", FIXTURE.read_bytes()), ("two.iflw", FIXTURE.read_bytes())])
        result = MODULE.inventory(archive)
        self.assertEqual([m["path"] for m in result["models"]], ["one.iflw", "two.iflw"])
        self.assertTrue(all(not m["warnings"] for m in result["models"]))

    def test_traversal_and_absolute_paths_rejected(self):
        for name in ("../escape.iflw", "/escape.iflw", "C:/escape.iflw", "dir\\escape.iflw"):
            with self.subTest(name=name):
                with self.assertRaises(MODULE.InventoryError):
                    MODULE.inventory(self.archive([(name, FIXTURE.read_bytes())]))
        self.assertFalse((self.root.parent / "escape.iflw").exists())

    def test_symlinks_rejected_in_archive_and_directory(self):
        entry = zipfile.ZipInfo("link.iflw")
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaises(MODULE.InventoryError):
            MODULE.inventory(self.archive([(entry, b"target")]))
        directory = self.root / "input"
        directory.mkdir()
        (directory / "link.iflw").symlink_to(FIXTURE)
        with self.assertRaises(MODULE.InventoryError):
            MODULE.inventory(directory)

    def test_duplicate_archive_paths_rejected(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            path = self.archive([("same.iflw", FIXTURE.read_bytes()), ("same.iflw", FIXTURE.read_bytes())])
        with self.assertRaises(MODULE.InventoryError):
            MODULE.inventory(path)

    def test_malformed_and_entity_xml_rejected(self):
        samples = [b"<broken>", b'<!DOCTYPE x [<!ENTITY y "value">]><x>&y;</x>',
                   '<!DOCTYPE x [<!ENTITY y "value">]><x>&y;</x>'.encode("utf-16")]
        for data in samples:
            with self.subTest(data=data):
                with self.assertRaises(MODULE.InventoryError):
                    MODULE.inspect_model("invalid.iflw", data)

    def test_unknown_namespace_and_dangling_edge_warn(self):
        self.assertTrue(MODULE.inspect_model("unknown.iflw", b"<unknown/>")["warnings"])
        data = FIXTURE.read_bytes().replace(b'targetRef="route"', b'targetRef="missing"')
        model = MODULE.inspect_model("dangling.iflw", data)
        self.assertIn("Unresolved target on edge first", model["warnings"])

    def test_duplicate_model_ids_warn(self):
        data = FIXTURE.read_bytes().replace(b'id="transform"', b'id="start"')
        self.assertIn("Duplicate BPMN ID: start", MODULE.inspect_model("duplicate.iflw", data)["warnings"])

    def test_nested_archives_are_not_silently_opened(self):
        with self.assertRaisesRegex(MODULE.InventoryError, "nested ZIPs"):
            MODULE.inventory(self.archive([("nested.zip", b"not traversed")]))
        path = self.archive([("sample.iflw", FIXTURE.read_bytes()), ("nested.zip", b"not traversed")])
        self.assertIn("Nested archive not inspected: nested.zip", MODULE.inventory(path)["warnings"])

    def test_file_total_and_member_limits(self):
        path = self.archive([("sample.iflw", FIXTURE.read_bytes())])
        with patch.object(MODULE, "MAX_FILE_BYTES", 8):
            with self.assertRaises(MODULE.InventoryError):
                MODULE.inventory(path)
            with self.assertRaises(MODULE.InventoryError):
                MODULE.inventory(FIXTURE)
        with patch.object(MODULE, "MAX_TOTAL_BYTES", 8):
            with self.assertRaises(MODULE.InventoryError):
                MODULE.inventory(path)
        with patch.object(MODULE, "MAX_FILES", 0):
            with self.assertRaises(MODULE.InventoryError):
                MODULE.inventory(path)

    def test_cli_success_and_failure_contract(self):
        success = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURE)], capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(json.loads(success.stdout)["schema_version"], 1)
        self.assertEqual(success.stderr, "")
        missing = subprocess.run([sys.executable, str(SCRIPT), str(self.root / "missing.zip")],
                                 capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, "")
        self.assertIn("Inventory failed", missing.stderr)


if __name__ == "__main__":
    unittest.main()
