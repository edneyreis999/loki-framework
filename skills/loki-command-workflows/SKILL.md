---
name: loki-command-workflows
description: Use shared Loki command workflows from Codex. Trigger when the user invokes `loki:init`, `init-loki`, `loki:feedback`, `loki:tech-analysis`, `loki:generate-action-plan`, `loki:enrich-tasks`, `loki:run-plan`, or `loki:retrospectiva-tecnica`; read the matching installed command contract and load the required Loki skills.
when_to_use:
  - "Use when the user invokes a shared Loki command workflow from Codex."
  - "Use when routing loki:init, init-loki, loki:feedback, loki:tech-analysis, loki:generate-action-plan, loki:enrich-tasks, loki:run-plan, or loki:retrospectiva-tecnica."
argument-hint: "[loki command name, command arguments]"
arguments:
  required: []
  optional:
    - command_name
    - command_arguments
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
escalation_signals:
  - ambiguous command routing
  - command contract requires high-effort downstream workflow
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-command-workflows/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:init
  - loki:feedback
  - loki:tech-analysis
  - loki:generate-action-plan
  - loki:enrich-tasks
  - loki:run-plan
  - loki:retrospectiva-tecnica
---

# loki-command-workflows

## Purpose

Expose shared Loki command contracts to Codex as a skill-based workflow surface.
Use this skill when the user invokes a command that is available in the active
installation profile.

## Command Map

- `loki:init` or `init-loki`: read
  `.agents/commands/loki/loki-init.md`, then use `loki-init`.
- `loki:feedback`: read
  `.agents/commands/loki/loki-feedback.md`, then use `loki-feedback`.
- `loki:tech-analysis`: read
  `.agents/commands/loki/loki-tech-analysis.md`, then use
  `loki-tech-analysis-authoring`.
- `loki:generate-action-plan`: read
  `.agents/commands/loki/loki-generate-action-plan.md`,
  then use `loki-action-plan-authoring`.
- `loki:enrich-tasks`: read
  `.agents/commands/loki/loki-enrich-tasks.md`, then use
  `loki-enrich-tasks`.
- `loki:run-plan`: read
  `.agents/commands/loki/loki-run-plan.md`, then use
  `loki-run-plan-execution`.
- `loki:retrospectiva-tecnica`: read
  `.agents/commands/loki/loki-retrospectiva-tecnica.md`,
  then use `loki-retrospectiva-tecnica`.

## Procedure

1. Match the user request to one command in the command map.
2. Read only the matching installed command contract from
   `.agents/commands/loki/`, as listed in the command map.
3. Load the command's required Loki skill or skills by name from the installed
   skill set.
4. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   validators, gates, stop conditions, and handoffs.
5. If the command contract is not present in `.agents/commands/loki/`, stop and
   report that the active installation profile does not expose that command.

## Limits

- Do not use deprecated Codex custom prompts as the canonical workflow surface.
- Do not edit `.agents/**` or `.codex/**` during ordinary Loki workflow
  execution unless the user explicitly asks for installation or synchronization.
- Do not promote project-specific context into the Loki package.
