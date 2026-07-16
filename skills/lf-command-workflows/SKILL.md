---
name: lf-command-workflows
description: Route shared Loki command bundles from Codex. Trigger when the user invokes a public `loki-*` workflow; resolve the matching `skills/loki-<stem>/SKILL.md` bundle directly and load its routed references, assets and dependencies.
when_to_use:
  - "Use when routing one of the 15 public Loki command bundles available to consumer and package profiles."
  - "Use when a caller needs a catalog of public loki-* identities, not a duplicate command contract."
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
used_by: [loki-init, loki-catalogar-docs, loki-criar-branch, loki-commit, loki-abrir-pr, loki-continuous-improvement, loki-enrich-tasks, loki-feedback, loki-generate-action-plan, loki-human-decision-preflight, loki-agentic-development, loki-deep-research, loki-retrospectiva-tecnica, loki-run-plan, loki-tech-analysis]
---

# lf-command-workflows

## Purpose

Catalog public Loki command identities without duplicating their execution
contracts. The command bundle is always the primary authority.

## Routing

Read [references/command-routing.md](references/command-routing.md), match one
exact `loki-*` identity and then read that bundle's `SKILL.md`, routed execution
and response references, and response asset. Load its `required_skills` and
`required_commands` separately.

## Limits

- Never read legacy command-contract locations or compatibility projections.
- Never reinterpret a `type: command` bundle as a knowledge skill.
- Do not route internal-only workflows from this router.
- Do not edit installed mirrors during ordinary execution.
