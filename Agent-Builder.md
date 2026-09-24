# Agent Skill Engineering Framework

## Goal

Build skills that are:

* discoverable,
* composable,
* context-efficient,
* deterministic where appropriate,
* testable,
* maintainable,
* and minimal without sacrificing reliability.

A skill should behave like a small software package, not a long prompt.

Use seven concerns:

1. **Discovery**
2. **Composition**
3. **Packaging**
4. **Execution**
5. **Context**
6. **Validation**
7. **Maintenance & Pruning**

---

# 1. Discovery

Discovery determines whether the skill should participate in a request.

A strong skill description defines **when to use the skill**, not merely what the skill contains.

Example:

Weak:

> Helps with presentations.

Better:

> Use when creating, editing, restructuring, reviewing, or transforming slide presentations, pitch decks, or `.pptx` artifacts.

## Define

For each skill specify:

* positive triggers,
* common synonyms,
* artifact/file types,
* negative triggers where confusion is likely,
* neighboring skills,
* requests where the skill should compose with another skill.

Optimize against two failures:

### False negative

The skill should participate but does not.

### False positive

The skill participates when it should not.

---

## Discovery Feedback Loop

Trigger design is never finished at authoring time.

Real requests will expose phrases and intent patterns that were not anticipated.

Continuously collect:

* missed activations,
* incorrect activations,
* ambiguous activations,
* requests that required manual routing.

For each failure:

1. Capture the original request.
2. Determine the expected participating skill or skills.
3. Classify the error as false positive, false negative, ambiguity, or composition failure.
4. Identify the smallest trigger-description change that fixes it.
5. Add the request to the regression test set.
6. Rerun nearby trigger tests.

Do not rewrite the entire description to fix one rare miss unless the description itself is structurally wrong.

Production failures should become permanent routing tests.

---

# 2. Skill Composition

Skills are not always mutually exclusive.

A request may require:

* one skill,
* one primary skill plus supporting skills,
* or multiple complementary skills.

Example:

> Create a legal analysis as a DOCX file.

This may require:

**Legal-analysis skill**
→ determines domain reasoning and structure.

**DOCX skill**
→ determines artifact generation and file handling.

Neither replaces the other.

---

## Interaction Types

For each skill relationship classify it as:

### Exclusive

Only one skill should own the request.

Example:

PDF creation vs spreadsheet creation when only one artifact was requested.

### Composable

Both skills contribute different capabilities.

Example:

financial-analysis skill + spreadsheet skill.

### Dependency

One skill requires another capability.

Example:

report-generation skill → document-rendering skill.

### Optional enhancement

Another skill can improve the result but is not required.

---

## Responsibility Boundaries

When skills compose, each should own a distinct responsibility.

Prefer:

```text
Domain skill
→ determines what the artifact should contain.

Artifact skill
→ determines how the artifact should be constructed.

Validation skill
→ verifies the resulting artifact.
```

Avoid duplicated ownership.

If two skills contain the same rule, move that rule to one canonical owner or a shared reference.

---

## Conflict Resolution

When two participating skills issue incompatible instructions, resolve them using explicit priority:

1. safety and system constraints,
2. user requirements,
3. artifact or environment constraints,
4. domain-specific requirements,
5. skill defaults,
6. optional preferences.

Skill authors should document known conflicts instead of relying on accidental prompt order.

---

# 3. Packaging

Separate different capability types.

Typical structure:

```text
skill-name/
├── SKILL.md
├── references/
│   ├── domain-rules.md
│   └── edge-cases.md
├── scripts/
│   ├── validate.py
│   └── transform.py
├── tests/
│   └── cases.yaml
└── assets/
    └── template.ext
```

Not every skill needs every directory.

---

## SKILL.md

Keep only what is needed for routing and execution:

* description,
* core procedure,
* decision rules,
* resource pointers,
* critical constraints,
* validation requirements.

---

## References

Use for supporting knowledge:

* documentation,
* schemas,
* domain rules,
* examples,
* specialized workflows,
* edge cases.

---

## Scripts

Use code when deterministic execution is more reliable than prose.

Examples:

* parsing,
* validation,
* transformation,
* calculations,
* metadata inspection,
* format conversion.

Use agent instructions for judgment.

Use scripts for repeatable mechanics.

### Decision rule

Ask:

> Could ordinary code perform this operation more reliably than natural-language reasoning?

If yes, prefer code.

---

## Assets

Use for reusable non-instruction resources:

* templates,
* schemas,
* configuration,
* sample artifacts,
* static resources.

---

# 4. Execution

Define the smallest reliable path from request to result.

Typical flow:

1. Inspect the request.
2. Determine the required outcome.
3. Determine participating skills.
4. Select the applicable execution path.
5. Load required resources.
6. Execute judgment-based steps.
7. Run deterministic scripts where appropriate.
8. Validate.
9. Return the result.

Each step should have a clear purpose.

Do not mix large amounts of supporting knowledge into procedural instructions.

---

## Branch Only When Behavior Changes

Use:

**Condition → Action → Resource**

Example:

```text
If authentication is involved:
→ load references/authentication.md

If the request contains a spreadsheet:
→ use spreadsheet workflow

Otherwise:
→ continue with the default path
```

Do not create branches for trivial differences.

---

# 5. Context Architecture

Optimize for **hot-path context**, not total package size.

The core skill should know where information exists without loading everything.

Use three levels.

## Core

Always loaded:

* routing logic,
* core procedure,
* critical constraints,
* validation rules.

## Conditional resources

Loaded only when a defined condition is satisfied.

Example:

> If OAuth is required, load `references/oauth.md`.

## Deep resources

Loaded only when the conditional resource cannot provide enough information.

Examples:

* full API specifications,
* large schema collections,
* extensive examples.

---

## Context Rule

Every optional resource should answer:

1. **When should this be loaded?**
2. **Why is it needed?**

If neither is clear, it probably does not belong in the skill.

---

## Context Efficiency

Measure:

### Package size

Total available instructions, code, references, and assets.

### Hot-path size

Context normally required for a typical execution.

Optimize the second aggressively.

A 20,000-token package that normally loads 1,000 tokens can be better than a 4,000-token skill that always loads all 4,000.

---

# 6. Steering

Use consistent operational language.

Prefer verbs such as:

* Inspect
* Determine
* Select
* Load
* Execute
* Compare
* Validate
* Reject
* Revise
* Return
* Stop

Use one term consistently for one operation.

Do not alternate between five synonyms unless they mean different things.

---

## Strength

Use:

**MUST / NEVER / ONLY**
for critical behavior.

**Prefer / By default**
for normal behavior.

**If / When / Unless**
for conditional behavior.

**May / Consider**
for optional behavior.

Reserve strong language for genuinely important constraints.

If everything says MUST, nothing is meaningfully prioritized.

---

## Make Behavior Observable

Weak:

> Make the result high quality.

Better:

> Verify that every requested section exists and that no unsupported claims were introduced.

Instructions should describe behavior that tests can evaluate.

---

# 7. Validation & Testing

Every skill needs explicit success conditions.

Before returning, verify:

* correct skill or skills participated,
* correct execution path was selected,
* required resources were loaded,
* unnecessary resources were avoided,
* deterministic operations succeeded,
* required output was produced,
* constraints were satisfied,
* unsupported assumptions were not introduced.

---

## Failure Policy

Define what happens when:

* a resource is unavailable,
* a script fails,
* an input is unsupported,
* information is ambiguous,
* participating skills conflict.

General pattern:

1. Determine whether execution can continue correctly.
2. Use a documented fallback when available.
3. State meaningful limitations.
4. Never fabricate missing information.
5. Stop the affected operation when correctness cannot be preserved.

---

## Ambiguity

### Non-material ambiguity

If interpretations lead to substantially the same outcome:

→ choose a reasonable interpretation and continue.

### Material ambiguity

If interpretations materially change the artifact, tool, branch, or result:

→ resolve using available context, a documented default, or necessary user input.

Do not silently invent consequential assumptions.

---

## Test Matrix

Every important skill should include:

| Test               | Checks                              |
| ------------------ | ----------------------------------- |
| Trigger positive   | Expected activation                 |
| Trigger negative   | No incorrect activation             |
| Trigger regression | Previously observed production miss |
| Composition        | Correct multi-skill participation   |
| Conflict           | Correct priority resolution         |
| Happy path         | Normal execution                    |
| Branch             | Correct conditional path            |
| Ambiguity          | Correct ambiguity handling          |
| Failure            | Correct fallback                    |
| Edge case          | Unusual valid input                 |
| Adversarial        | Critical constraints remain intact  |

---

## Test Specification

Every test should define:

```text
Input:
Expected participating skills:
Expected path:
Expected resources:
Expected output properties:
Pass condition:
Failure condition:
```

A test without a measurable pass condition is not a useful test.

---

# 8. Maintenance

Skills decay.

APIs change.
Schemas change.
Templates change.
Domain rules change.
Neighboring skills change.

Maintenance must therefore be designed into the skill.

---

## Canonical Ownership

Every rule, schema, or fact should have one canonical location.

Other files should point to it rather than copying it.

Example:

Bad:

```text
SKILL.md
→ contains API limits

references/api.md
→ repeats API limits

scripts/client.py
→ hardcodes API limits
```

Better:

```text
references/api-config.yaml
→ canonical limits

SKILL.md
→ points to config

scripts/client.py
→ reads config
```

Update once.

Propagate everywhere.

---

## Versioning

Track meaningful changes to:

* trigger descriptions,
* execution behavior,
* reference schemas,
* scripts,
* interfaces between skills.

Prefer semantic intent:

### Patch

Fix without changing intended behavior.

Examples:

* typo,
* improved wording,
* additional equivalent trigger phrasing.

### Minor

Adds behavior while remaining backward compatible.

Examples:

* new branch,
* new supported input format,
* new optional composed skill.

### Major

Changes expected behavior or interfaces.

Examples:

* routing semantics change,
* reference structure changes,
* script interface changes,
* skill responsibility moves elsewhere.

---

## Dependency Awareness

When a skill depends on:

* another skill,
* API,
* schema,
* script,
* template,
* reference,

record that dependency explicitly.

When the dependency changes, rerun affected tests.

---

## Maintenance Procedure

When an external dependency changes:

1. Identify affected canonical resources.
2. Update the canonical source.
3. Update scripts or instructions only where interfaces changed.
4. Run dependency-specific tests.
5. Run routing and composition regressions.
6. Update the skill version when behavior changed.
7. Remove obsolete compatibility instructions when no longer needed.

Do not accumulate permanent patches for old behavior unless backward compatibility is intentionally required.

---

# 9. Pruning

The goal is not the fewest words.

The goal is:

> The smallest context that reliably produces correct behavior.

Use three tests.

---

## Deletion Test

For every sentence ask:

> If I remove this, does failure become materially more likely?

If no, delete it.

---

## Duplication Test

Ask:

> Does this rule already exist elsewhere?

If yes:

* keep one canonical version,
* replace copies with references where needed.

---

## Placement Test

Ask:

> Does this information need to be on the normal execution path?

If no:

* move it to a conditional reference,
* deep reference,
* script,
* asset,
* or test fixture.

---

# 10. Size Budgets

Use size targets as warning signals, not rigid limits.

Suggested calibration:

| Component            |                             Guideline |
| -------------------- | ------------------------------------: |
| Description          |                 1–4 concise sentences |
| Core workflow        |                      5–15 major steps |
| Core SKILL.md        |              Preferably ~50–150 lines |
| Individual reference |             Preferably <300–500 lines |
| Trigger examples     | Enough to cover meaningful boundaries |
| Tests                |           Grow with observed failures |
| Deep resources       |         Large if conditionally loaded |

If SKILL.md keeps growing, first ask whether content belongs in a reference, script, test, or another skill.

---

# 11. Skill Development Loop

Build skills using this sequence:

### 1. Define outcome

What must the skill reliably produce?

### 2. Define discovery

When should it participate?

When should it not?

What other skills may participate?

### 3. Define responsibilities

What does this skill own?

What belongs to other skills?

### 4. Define execution

Write the smallest reliable procedure.

### 5. Package resources

Separate:

* instructions,
* references,
* scripts,
* assets,
* tests.

### 6. Design context loading

Keep optional information outside the hot path.

### 7. Define failure behavior

Specify important fallbacks.

### 8. Define validation

Make success observable.

### 9. Build tests

Cover routing, execution, composition, ambiguity, and failure.

### 10. Prune

Apply:

* Deletion Test,
* Duplication Test,
* Placement Test.

### 11. Deploy and observe

Collect real trigger and execution failures.

### 12. Convert failures into regressions

Every meaningful production failure should become a test.

### 13. Maintain

Update canonical sources, dependencies, and versions without duplicating knowledge.

---

# Core Architecture

A production skill system should behave like this:

```text
Request
   ↓
Discovery
   ↓
Participating Skill Set
   ↓
Responsibility / Composition Resolution
   ↓
Execution Path
   ↓
Selective Context Loading
   ↓
Judgment + Deterministic Tools
   ↓
Validation
   ↓
Output
   ↓
Observed Failures
   ↓
Regression Tests
   ↓
Skill Improvement
```

---

# Core Principle

Optimize for:

**Correct discovery
→ correct composition
→ minimal execution
→ selective context
→ strong steering
→ deterministic mechanics
→ measurable validation
→ continuous maintenance
→ aggressive pruning**

A skill is complete only when it can be discovered correctly, cooperate with other skills, execute reliably, survive change, and improve from real failures.
