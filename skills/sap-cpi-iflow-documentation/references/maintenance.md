# Maintenance and validation

Load this file when changing or evaluating the skill, updating a dependency, or recording a real documentation/routing failure. The skill version is canonical in `SKILL.md` metadata.

## Canonical ownership and dependencies

| Owner / dependency | Contract | Recheck when changed |
| --- | --- | --- |
| `SKILL.md` | Discovery, responsibility boundaries, execution, completion criteria, version | Routing, composition, conflict, and behavioral cases |
| `evidence-analysis.md` | Evidence vocabulary and CPI interpretation checks | Affected SAP component and evidence cases |
| `assets/documentation-template.md` | Default document structure | Output coverage and requested-template cases |
| `scripts/inspect_iflow.py` | Inventory schema and local processing limits | Automated parser/CLI tests; inspect a representative sanitized export |
| Python 3.9+ standard library | Offline ZIP, XML, hashing, JSON, unit tests | Parser and CLI tests on supported Python |
| SAP export structure / BPMN model namespace | Observed source format; no claim of complete or stable SAP schema support | New-format fixture, namespace and reference checks |
| Official SAP documentation below | Current platform semantics, not facts about a particular tenant | Applicable interpretation cases and source links |
| Optional artifact skill / SAP read capability | Requested format generation / authorized tenant retrieval | Composition, unavailable-capability, scope cases |

No SAP SDK, credentials, network connection, or third-party Python package is required for the helper. Word/PDF creation and tenant retrieval depend on the target environment and are not bundled capabilities.

## Official reference sources

Checked 2026-09-23. Read the relevant source only when its semantics are needed or being refreshed; do not load all SAP documentation for each iFlow. These pages establish platform behavior, not a tenant's actual configuration.

- [Integration flow example requests](https://help.sap.com/docs/integration-suite/sap-integration-suite/integration-flow-example-requests): design-time artifact/resource read and download capabilities. Consult current details before tenant API access.
- [Externalize parameters of an integration flow](https://help.sap.com/docs/cloud-integration/sap-cloud-integration/externalize-parameters-of-integration-flow): parameter references and the distinction between default and configured values.
- [Configure externalized parameters](https://help.sap.com/docs/integration-suite/sap-integration-suite/configure-externalized-parameters-of-integration-flow): environment/runtime-profile configuration and overrides.
- [Define exception subprocess](https://help.sap.com/docs/cloud-integration/sap-cloud-integration/define-exception-subprocess): handler scope and error/end-event behavior; inspect the actual process and handler before describing its effects.
- [Configure integration flow components](https://help.sap.com/docs/integration-suite/sap-integration-suite/configure-integration-flow-components): component-specific reference entry point when source settings require explanation.

## Run validation

From this skill directory:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The tests exercise the inventory helper using synthetic fixtures; they do not certify SAP export compatibility, deployment, or agent behavior. `tests/cases.json` specifies separate behavioral acceptance scenarios with measurable outcomes. Evaluate those with the skill and suitable sanitized evidence, recording observed outputs, loaded resources, pass/fail, and limitations. A scenario definition is not an executed test. No production regressions have yet been collected. See [validation.md](../tests/validation.md) for the initial checks actually performed and remaining limits.

For a changed script, run automated tests and inspect its output on available representative exports. For changed discovery/behavior, evaluate affected scenarios, including neighboring negative triggers and composition. Validate frontmatter and local resource links with the host's available skill validation tools. Do not require the author's local tools at runtime.

## Observe, improve, and version

The package is ready for a supported skill host; installation/publication and production observation are separate actions requested by the user. After actual use, capture a sanitized failing request and evidence, expected participating skills, observed outcome, and classification: false positive, false negative, ambiguity, composition, or execution failure. Add a permanent measurable regression case; never label a hypothetical scenario as a production miss.

Update the canonical owner of the failing rule, fix the smallest relevant behavior, rerun affected tests and nearby routing/composition cases, and remove obsolete guidance. Use a patch version for equivalent wording or bug fixes, minor for compatible new inputs/branches, and major for changed routing semantics, responsibilities, or inventory interfaces. Record the reason and verification in the change history below. Apply deletion, duplication, and placement tests to each change; keep detailed sources/tests outside ordinary execution context.

## Change history

- 1.0.0 (2026-09-23): Initial offline evidence-based documentation workflow, conditional tenant/partial-input paths, document template, structural inventory helper, and synthetic tests. Runtime compatibility and production behavior require real export/tenant evidence.
