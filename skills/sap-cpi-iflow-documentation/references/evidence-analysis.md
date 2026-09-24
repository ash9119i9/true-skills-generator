# Evidence analysis

Use this guide to inspect the supplied source after identifying the input type. It defines the evidence labels and CPI interpretation checks; the document template defines presentation.

## Evidence states and locators

| State | Use |
| --- | --- |
| Observed | Directly supported by a supplied artifact or captured tenant evidence. State whether this is design-time, configured, or runtime evidence. |
| Inferred | A plausible interpretation of observed evidence. Include the reasoning and what would confirm it. |
| Unknown | Missing, unreadable, unresolved, or contradictory evidence. State the specific gap and its impact. |
| Not applicable | The feature is not relevant to the verified scope. Give the reason; absence from a cropped screenshot is insufficient. |

Assign evidence IDs such as E01. Record relative source path, SHA-256 when available, source version/environment, and locator. Use XML element IDs/property keys, script line ranges, mapping node IDs, screenshot filename plus visible panel/step, or timestamped runtime record IDs. File hashes establish identity, not correctness. Preserve separate evidence records for different versions and environments. Do not infer an export date from a file's modification time.

## ZIP, directory, and XML path

1. Run the inventory helper. Review every warning. Locate each `.iflw` and its associated manifest, configuration, scripts, mappings, and schemas; paths vary across exports.
2. Inspect available metadata, including `META-INF/MANIFEST.MF` when present. Unfold manifest continuation lines before interpreting values. Keep artifact technical ID, display name, package ID, and bundle version distinct; do not substitute a filename for an authoritative ID.
3. For each flow, resolve process and collaboration IDs, participants, sequence flows, and message flows. Preserve nested scopes and process references. Traverse source/target edges with a visited set so loops do not cause an infinite walk. Disconnected elements may be exception handlers or unused elements; classify from evidence.
4. Inspect SAP extension properties on nodes and channels. BPMN tags describe structure, while SAP properties carry component-specific behavior. Unknown extension types remain visible as unknown components; never guess a transformation from its display name alone.
5. Build a resource-use map from step references to concrete files. Read linked resources when needed. Missing shared scripts, value mappings, ProcessDirect callees, or external schemas become dependencies and gaps, not fabricated implementations.

Read ZIP members without extracting whenever possible. If manual extraction is necessary, use a fresh working directory and reject traversal paths, absolute paths, symlinks, and excessive expansion before writing. Never overwrite the original export. Inspect source as text; do not execute Groovy, JavaScript, XSLT extension code, or bundled binaries.

## Component checklist

Apply rows only to components present or required by the documentation scope. Unsupported or inaccessible details are Unknown.

| Component | Inspect and document |
| --- | --- |
| Business context | Stated purpose, trigger, business object, source/target roles, and scope. Label purpose inferred from code/names as Inferred. |
| Sender/receiver channel | Direction from message-flow evidence, adapter type/version, protocol, address or expression, operation/resource, authentication method and safe alias, proxy/location reference, timeout, and relevant adapter-specific settings. Do not infer these from system names. |
| Trigger/schedule | Timer or message trigger, schedule expression, timezone if specified, and source of configuration. No frequency claim when the expression remains unresolved. |
| Content modifier | Body, header, and exchange-property writes/deletes; value source and expression type; downstream consumers. Distinguish headers from exchange properties. |
| Router/filter | Every outgoing route, condition expression/type, default route, ordering if defined, and no-match behavior only when supported. Preserve condition meaning while redacting sensitive literals. |
| Splitter/multicast/gather/aggregator | Branch or split criterion, sequential/parallel configuration if present, correlation/completion conditions, combination strategy, and exception implications. A graph alone does not establish concurrency. |
| Process call / ProcessDirect | Resolve local target IDs or configured address expressions. Document call boundaries; identify unavailable called iFlows and do not invent their internals. |
| Script | File, entry function where specified, inputs, body/header/property reads and writes, external calls, error behavior, dependencies, logging/redaction implications, and evidence lines. Static inspection does not prove every runtime path executes. |
| Mapping / transformation | Mapping/XSLT resource, source and target schemas, verified field rules, constants/defaults, lookup/value-mapping dependencies, conditions, cardinality, and custom functions. Do not invent a field-level map from resource names or schemas alone. |
| Converter/validator | Conversion direction, relevant options, schema reference, and observable failure handling. |
| Persistence/JMS/idempotency | Observed store/queue/key expressions, retention/expiry and transaction/retry settings when supplied, and lookup/delete lifecycle. Do not infer delivery guarantees from the component's presence. |
| Exception handling | Owning process scope, error start/end type, handler steps, notifications, payload changes, rethrow/escalation behavior, and caller-visible effect where evidenced. Main-process handling does not establish local-process handling. |
| Operations | Available MPL/runtime evidence with time window and version, correlation fields, configured logging, observed errors, and documented recovery procedure. Separate recommended checks from verified operating procedures. |

## Parameters and security

Find externalized references, parameter definitions/defaults, and any separately supplied configuration snapshot. Record key, purpose, consuming step, declared default, configured value, environment/runtime profile, evidence, and unresolved status. Show only audience-appropriate, non-secret values. Some parameters contain partial addresses or multiple expressions; preserve their structure.

A configured value can override a default, and configurations can differ by runtime profile. An export alone does not prove which value the deployed flow used. A credential alias proves a reference, not the existence, validity, permission set, or content of security material. Record certificate/key aliases and authentication mechanisms only as evidenced, never private values.

## Partial-evidence path

For screenshots, read visible step labels, connections, and configuration panels. Cite each screenshot and visible location. Do not infer off-screen branches, script contents, hidden adapter tabs, or configured parameters. For pasted code, document that code's behavior but mark its attachment to a particular iFlow as unverified unless supplied. Notes may establish user-reported context; label them as such rather than as inspected implementation.

Produce useful partial documentation and a targeted request list for missing export/configuration/runtime evidence. If two candidate iFlows or versions could materially change the result, ask which is in scope; continue inventorying them separately while awaiting clarification. Never merge their graphs.

## Tenant path

Use only available authorized read tools and the tenant/artifact scope the user supplies. If access is unavailable, request an export or connection details without asking for secrets in chat. Do not assume a SAP connector exists.

Design-time artifact downloads, configuration reads, runtime artifact status, and message processing logs are different evidence sources. Record the tenant/environment, requested version, capture time, and read source. Check current official SAP API documentation and the connector's capabilities before selecting read operations. Do not infer API URLs, roles, or deployment status from this guide. Avoid retrieving payload attachments unless required and authorized.

## Inventory limitations

The helper's schema is an internal inventory, not a SAP-supported iFlow schema. It recognizes the standard BPMN model namespace and records ID-bearing elements, scopes, edges, and extension-property keys. It deliberately omits property values, condition text, script contents, and manifest values; inspect these selectively in the source. Names, IDs, keys, and filenames are not automatically redacted.

The helper supports a single iFlow ZIP, an extracted directory containing iFlows, or a standalone `.iflw`. Nested archives are inventoried but not opened. A package containing only nested iFlow ZIPs is not a directly supported input: obtain individual exports or inspect each nested archive separately with the same safety checks. An unknown BPMN namespace, duplicate IDs, or unresolved references needs manual review; inventory success is not semantic validation.

The helper enforces local processing limits defined in its script. If a limit is exceeded, do not silently skip members or raise limits blindly; request a smaller export or review a bounded subset and label reduced coverage. For malformed XML, unreadable/encrypted archives, unsafe paths, or missing flow models, stop the affected inventory and report the specific problem. Manually inspect trustworthy available evidence or request a fresh export. If Python is unavailable, use equivalent read-only archive/XML tooling and record that the bundled checks were not run.
