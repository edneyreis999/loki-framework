---
name: loki-catalogar-docs
description: Run the Loki `loki:catalogar-docs` command workflow in Codex. Use when cataloging durable consumer documentation under `/docs`, validating directory paths, applying recursion limits, coordinating safe bottom-up fan-out, invoking `catalogador` with explicit scoped-write envelopes, and producing a summarized catalog update.
when_to_use:
  - "Use when running loki:catalogar-docs to catalog durable consumer documentation under /docs."
  - "Use when a user asks to catalog docs, refresh docs/index.xml, validate documentation directory scope, or run bottom-up cataloging with catalogador."
  - "Use when safe fan-out, recursion limits, target_files ownership, approval gates, validators, and resumable catalog state are required."
argument-hint: "[docs directory, recursive flag, approval context]"
arguments:
  required:
    - docs_directory
  optional:
    - recursive
    - large_tree_confirmation
    - out_of_docs_approval
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - ambiguous documentation target or ownership
  - recursive tree near command limits
  - conflicting target_files or shared index writes
  - durable consumer documentation changes without recorded approval
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-catalogar-docs/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:catalogar-docs
---

# loki-catalogar-docs

## Procedure

1. Read the installed command contract:
   [loki-catalogar-docs.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, human gates, stop conditions,
   packaging checks and resume contract.
3. Validate `DOCS_DIR` before discovery: it must exist, be a directory, stay
   inside the workspace and belong to durable consumer documentation unless an
   explicit out-of-`/docs` approval is already recorded.
4. Apply the command's deterministic exclusions and recursion limits before
   invoking `catalogador`.
5. Build bottom-up batches and allow fan-out only when `target_files` are
   provably disjoint. Serialize every write to `docs/index.xml` or a parent
   index.
6. Invoke `catalogador` only through the explicit scoped-write envelope declared
   by the command contract.
7. Treat this skill as the Codex entrypoint for the command name
   `loki:catalogar-docs`.

## Limits

- Do not write outside the active command envelope.
- Do not use this command for generic source-code, runtime, build, generated
  artifact, engine, data, asset or configuration directories.
- Do not create per-directory `index.md` files by default; the first supported
  catalog target is `docs/index.xml`.
- Do not treat `.claude/**`, `.agents/**` or `.codex/**` as normative sources
  or write targets without later explicit installation approval.
- Do not mark approval, technical review or human validation as satisfied unless
  the decision is present in the current command context, an approved plan, or a
  recorded human interaction.
