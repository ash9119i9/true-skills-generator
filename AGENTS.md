# Repository purpose

This repository builds reusable agent skills from a user's problem statement or use case.

## Canonical framework

Before creating, updating, or reviewing a skill, read [Agent-Builder.md](Agent-Builder.md) in full. It is the canonical skill engineering framework for this repository. Follow it exactly, including its distinction between requirements, conditional guidance, examples, and suggested size targets.

Do not modify, rename, reformat, or replace `Agent-Builder.md` as part of skill generation. Do not substitute a generic skill template or another authoring guide for this framework. Refer to the framework instead of duplicating it in generated skills.

## Handling skill requests

Treat requests such as “I need a skill for <use case>”, “Build a skill for <problem statement>”, and equivalent wording as instructions to create a complete skill package, not merely to explain how to create one.

1. Inspect the request and existing repository content. Read the canonical framework before designing the skill.
2. Determine the intended outcome, inputs, outputs, and constraints from the problem statement. Resolve ambiguity using the framework's ambiguity policy; ask only for missing information that materially affects the result and cannot be resolved from context or a documented default.
3. Follow the **Skill Development Loop** in section 11, in its stated sequence. Apply the other framework sections as the detailed requirements for each step. Do not stop at a plan or an unfinished scaffold.
4. Create the package at `skills/<skill-name>/` unless the user specifies another location. Use a descriptive lowercase, hyphenated name. If that location already exists, inspect it and determine whether the request calls for an update or a distinct skill; do not overwrite unrelated work.
5. Provide a usable `SKILL.md` with YAML frontmatter containing `name` and `description`. Add supporting resources only when the framework and the use case call for them. Its example directory tree is not a requirement to create empty directories.
6. Build measurable test cases using the framework's **Test Specification**. Cover routing, execution, composition, ambiguity, and failure as required by the development loop, and apply the **Test Matrix** to the skill's important behaviors. Distinguish real observed regressions from hypothetical cases; never invent production history.
7. Validate the package against the full framework, run applicable available checks, and fix failures before returning it. Verify resource links, required output, and any scripts added. Distinguish authored test cases, structural checks, and behavioral tests actually executed; report any checks that could not run and why.
8. Apply the framework's pruning tests before delivery. Record meaningful version and dependency information in the package so its maintenance procedure can be followed.
9. Return the created package path, a concise description of its behavior, validation results, and any material limitations.

## Delivery boundaries

Keep generated skills self-contained: do not require this repository's authoring framework at runtime unless the requested skill itself is a skill-authoring tool.

Preserve existing unrelated files. Creating a skill here does not by itself request global installation, publication, deployment, or changes to external systems. For the framework's deploy-and-observe stage, make the package ready for its intended environment and document how actual failures become regression tests. Perform installation or deployment when requested, and report accurately whether deployment and real-world observation have occurred.

If a required capability or resource is unavailable, apply the framework's failure policy. Never fabricate dependencies, successful execution, validation evidence, or missing domain facts.
