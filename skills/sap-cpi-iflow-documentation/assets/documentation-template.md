# Integration flow documentation: <verified display name or source filename>

> Authoring template: replace instructions and placeholders with evidence-backed content. Keep relevant sections; mark unsupported coverage Unknown and irrelevant features Not applicable with a reason. Follow a requested user template while preserving this coverage. Use the evidence states defined in the analysis guide. Do not present an empty template as completed documentation.

## 1. Document scope and evidence baseline

Record documentation date, requested audience, scope/completeness, source artifact ID/name, package, version, and environment when known. List source exports and hashes. State explicitly whether runtime/configuration evidence was supplied. Identify exclusions and conflicting versions.

## 2. Purpose and integration overview

Describe business purpose, sender and receiver roles, business object, trigger, and expected inputs/outputs. Distinguish user-reported context and inferred intent from observed implementation.

## 3. Flow diagram and process walkthrough

Include a Mermaid diagram with labels tied to stable step IDs. Separate process scopes and exception paths; show conditional/default routes and external call boundaries. Use generated safe diagram IDs and escaped labels rather than inserting arbitrary source strings into Mermaid syntax. If rendering cannot be checked, disclose that limit.

| Step ID / scope | Component and role | Predecessors / successors | Behavior and conditions | Resource | State / evidence |
| --- | --- | --- | --- | --- | --- |

## 4. Interfaces and connectivity

| Channel / direction | Source or target | Adapter / protocol | Address or expression | Operation / format | Authentication reference | Relevant settings | State / evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |

Record required contracts, schema references, trigger/schedule, and timezone where supported. Redact secrets and sensitive URL values.

## 5. Message processing, mappings, and scripts

Document body/header/property changes and each referenced script, mapping, converter, validator, or lookup. Include verified field-level transformation rules when source mappings are available; otherwise state the gap.

| Resource / step | Input | Transformation / side effects | Output | Dependencies | State / evidence |
| --- | --- | --- | --- | --- | --- |

## 6. Configuration and externalized parameters

| Key / consumer | Purpose | Declared default (safe) | Configured value (safe) | Environment / profile | Resolution status | State / evidence |
| --- | --- | --- | --- | --- | --- | --- |

Keep unresolved dynamic expressions intact. Distinguish design configuration from observed runtime values.

## 7. Error handling and reliability

Describe exception handlers by owning scope, end behavior, notifications, timeout/retry settings, persistence, duplicate handling, and caller-visible outcome when supported. Explicitly identify missing evidence for delivery guarantees or recovery procedures.

## 8. Security and external dependencies

List authentication mechanisms and permitted aliases, called iFlows, shared scripts, schemas, value mappings, queues/stores, certificates, and external systems. Indicate whether each dependency's implementation/configuration was inspected or only referenced. Do not reproduce secret contents or real personal payload data.

## 9. Operations and support handover

Describe supported correlation/logging, deployment/runtime evidence, observation time window, known failure symptoms, and documented recovery steps. Label proposed checks as recommendations. Record owners and SLAs only if supplied; no runtime evidence means no claim of successful execution.

## 10. Gaps, contradictions, and assumptions

| Item | State | Missing or conflicting evidence | Documentation impact | Evidence needed to resolve |
| --- | --- | --- | --- | --- |

## 11. Evidence register and validation

| Evidence ID | Source path / record | Hash or version | Locator | Environment / capture time | Evidence kind |
| --- | --- | --- | --- | --- | --- |

Summarize coverage reconciliation: source process/channel/resource counts where known, documented coverage, and unresolved items. Record checks actually performed and results; list unavailable checks separately. Distinguish inventory parsing, manual source review, diagram/document rendering, and actual runtime observations.
