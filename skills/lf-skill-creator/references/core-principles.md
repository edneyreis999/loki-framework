# Core Principles

Use this reference when deciding how much content a skill should include and how strict its workflow should be.

## Concision

Treat context as shared budget. Add only information another agent would not already infer reliably.

Prefer concise examples over broad explanation. Challenge each paragraph:

- Does the agent need this to execute the workflow?
- Does this belong in `SKILL.md`, or should it live in a reference?
- Does this duplicate a source already linked elsewhere?

## Degrees of Freedom

Match specificity to operational risk:

- **High freedom**: textual heuristics for work where multiple approaches are valid.
- **Medium freedom**: pseudocode, templates, or parameterized steps where a preferred pattern exists.
- **Low freedom**: scripts or exact procedures for fragile, repetitive, or high-risk work.

## Validation Integrity

Forward-test complex skills with clean context when feasible. Pass the skill and a realistic task, not your diagnosis or expected answer.

Use raw artifacts for validation: prompts, outputs, diffs, logs, traces, or generated files.

Avoid leaking conclusions into validation prompts. The test should reveal whether the skill generalizes.

## Capability Boundary And Freedom

Declare one specialized reusable capability with included scope, non-scope,
observable triggers and exclusions. A skill can be invoked inside a workflow,
but never coordinates the workflow's agents, global handoffs or resume state.
Use high freedom only for low-risk judgment; use templates or exact procedures
for fragile/repeated work. Stop for missing required input, permission, source,
validator or gate, and report success, failure or partial completion honestly.
