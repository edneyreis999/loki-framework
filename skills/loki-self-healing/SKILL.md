---
name: loki-self-healing
description: Run the Loki `loki:self-healing` command workflow in Codex. Use when auditing and automatically correcting internal Loki package artifacts from a specific file, directory, workflow, or staged-file set; it understands the package, analyzes files individually, applies scoped fixes to the working tree, and never stages or commits changes.
when_to_use:
  - "Use when the user asks Loki to self-heal, audit, or automatically correct internal Loki package artifacts."
  - "Use when the input is a file, directory, workflow name, or staged files that should be checked against Loki package standards."
  - "Use when corrections should be applied directly to the working tree without git add or commit."
argument-hint: "[file path, directory path, workflow name, staged]"
arguments:
  required: []
  optional:
    - file_path
    - directory_path
    - workflow_name
    - staged
    - scope
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
  - broad package scope
  - staged-file input with working tree divergence
  - corrections affecting commands, skills, agents, templates, docs, scripts, or manifest
  - conflicting package rules or incomplete operational inventory
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-self-healing/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:self-healing
---

# loki-self-healing

## Procedure

1. Read the installed command contract:
   [loki-self-healing.md](references/command.md).
2. Read the self-healing contract:
   [self-healing-contract.md](references/self-healing-contract.md).
3. Resolve the requested scope: file, directory, workflow, or staged files.
4. Load `install-scopes.json` before any write to `commands/` or `skills/`.
   Classify every selected command or skill file as `internal-only`, `both`,
   `consumer-only`, or `unclassified-blocker`.
5. Read global package context first: `docs/operational-inventory.md`,
   `manifest.yaml`, `docs/package-authoring-guardrails.md`, and any command,
   skill, template, doc, script, or agent contract required by the scope.
6. Build a source map before writing: selected files, install scope, related
   package metadata,
   expected relationships, applicable instruction-quality checklist items,
   validators, and forbidden writes.
7. Analyze files individually against the audit lenses and internal instruction
   quality checklist. Use parallel read-only handoffs when available; otherwise
   keep a separate subsection per file in the main context. For `both`
   artifacts, apply the shared-artifact neutrality checklist in the self-healing
   contract before proposing or applying any correction.
8. Consolidate findings and apply only clear, scoped corrections. Write
   serially.
9. Do not run `git add`, `git commit`, `git reset`, `git checkout`, or any
   command that changes the git index.
10. After any command or skill change, run
    `python3 scripts/validate-install-scopes.py`.
11. Run package validators proportional to the touched surfaces.
12. Report changed files, validators, skipped findings, residual risks, and the
    required user action: review the diff and stage manually.

## Inputs

- A package file path.
- A package directory path.
- A Loki workflow name.
- The keyword or instruction for staged files.
- Optional exclusions or constraints.

## Outputs

- Corrections applied to the working tree.
- A concise self-healing report with scope, files analyzed, fixes applied,
  validators run, failures, skipped items, and residual risks.
- No staged files and no commits.

## Limits

- Do not apply changes outside the package root.
- Do not edit `.claude/**`, `.codex/**`, or `.agents/**`.
- Do not change consumer runtime surfaces.
- Do not apply speculative rewrites. Leave unclear findings as `investigar` or
  `bloqueado`.
- Do not edit an unclassified command or skill file. Register it as
  `unclassified-blocker` until `install-scopes.json` is updated by an approved
  package decision.
- Do not add Loki-only rules to `both` artifacts. Use the checklist in the
  self-healing contract instead of relying on inferred "neutral mode".
- Do not silently broaden scope beyond required metadata consistency files.

## Required Gates

- No pre-write approval is required for clear corrections inside the user
  requested scope.
- Human review is required after the run through ordinary git diff/staging.
