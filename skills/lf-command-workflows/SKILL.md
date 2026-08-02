---
name: lf-command-workflows
description: Route general-purpose Loki command bundles from Codex. Trigger when the user invokes one of the 18 general `loki-*` workflows; resolve the matching `skills/loki-<stem>/SKILL.md` bundle directly and load its routed references, assets and dependencies.
when_to_use:
  - "Use when routing one of the 18 current general-purpose Loki command bundles available to consumer and package profiles."
  - "Use when a caller needs the catalog of 18 general loki-* identities, not a duplicate command contract."
argument-hint: "[loki-* command name, arguments]"
arguments:
  required: []
  optional: [command_name, command_arguments]
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals: [ambiguous command routing, high-effort downstream workflow]
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-command-workflows/SKILL.md"
shell: bash
type: skill
status: draft
used_by: [loki-init, loki-catalogar-docs, loki-criar-branch, loki-commit, loki-abrir-pr, loki-continuous-improvement, loki-enrich-tasks, loki-feedback, loki-implement-feature, loki-manual-qa, loki-generate-inferences, loki-human-decision-preflight, loki-agentic-development, loki-deep-analysis, loki-deep-research, loki-retrospectiva-tecnica, loki-demand-text-improver, loki-tech-analysis]
---

# lf-command-workflows

## Purpose

Catalog general-purpose Loki command identities without duplicating their execution
contracts. The command bundle is always the primary authority.

## Routing

Read [references/command-routing.md](references/command-routing.md), match one
exact `loki-*` identity and then read that bundle's `SKILL.md`, routed execution
and response references, and response asset. Load its `required_skills` and
`required_commands` separately.

## Limits

- Never read legacy command-contract locations or compatibility projections.
- Never reinterpret a `type: command` bundle as a knowledge skill.
- Route package-maintenance workflows through
  `lf-internal-command-workflows`, even though both routers are installable in
  consumer and package profiles.
- Do not edit installed mirrors during ordinary execution.
- Route ordinary demand-plus-analysis implementation directly to
  `loki-implement-feature`. Never route it through `loki-agentic-development`,
  whose distinct contract adds POV/synthesis/digest/backlog before one unified
  handoff and is not an alias or wrapper.
