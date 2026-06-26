---
name: loki-command-workflows
description: Use Loki command workflows from Codex. Trigger when the user invokes `loki:feedback`, `loki:tech-analysis`, `loki:generate-action-plan`, `loki:enrich-tasks`, `loki:run-plan`, `loki:retrospectiva-tecnica`, or `loki:continuous-improvement`; read the matching command contract and load the required Loki skills.
when_to_use:
  - "Use when the user invokes a Loki command workflow from Codex."
  - "Use when routing loki:feedback, loki:tech-analysis, loki:generate-action-plan, loki:enrich-tasks, loki:run-plan, loki:retrospectiva-tecnica, or loki:continuous-improvement."
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
  - loki:feedback
  - loki:tech-analysis
  - loki:generate-action-plan
  - loki:enrich-tasks
  - loki:run-plan
  - loki:retrospectiva-tecnica
  - loki:continuous-improvement
---

# loki-command-workflows

## Purpose

Expose Loki command contracts to Codex as a skill-based workflow surface.
Codex does not treat installed `.agents/commands/` mirrors as a primary command
runtime. Use this skill when the user invokes a conceptual Loki command or asks
for the command behavior by name.

## Command Map

- `loki:feedback`: read
  [loki-feedback.md](references/commands/loki-feedback.md), then use
  `loki-feedback`.
- `loki:tech-analysis`: read
  [loki-tech-analysis.md](references/commands/loki-tech-analysis.md), then use
  `loki-tech-analysis-authoring`.
- `loki:generate-action-plan`: read
  [loki-generate-action-plan.md](references/commands/loki-generate-action-plan.md),
  then use `loki-action-plan-authoring`.
- `loki:enrich-tasks`: read
  [loki-enrich-tasks.md](references/commands/loki-enrich-tasks.md), then use
  `loki-enrich-tasks`.
- `loki:run-plan`: read
  [loki-run-plan.md](references/commands/loki-run-plan.md), then use
  `loki-run-plan-execution`.
- `loki:retrospectiva-tecnica`: read
  [loki-retrospectiva-tecnica.md](references/commands/loki-retrospectiva-tecnica.md),
  then use `loki-retrospectiva-tecnica`.
- `loki:continuous-improvement`: read
  [loki-continuous-improvement.md](references/commands/loki-continuous-improvement.md),
  then use the creator or retrospective skills named by the contract.

## Procedure

1. Match the user request to one command in the command map.
2. Read only the matching command contract from `references/commands/`.
3. Load the command's required Loki skill or skills by name from the installed
   skill set. The package source remains `skills/`.
4. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   validators, gates, stop conditions, and handoffs.
5. Treat installed `.agents/commands/loki/*.md` files as a mirror, not as the
   authoritative package source. The package source remains `commands/*.md`.

## Limits

- Do not use deprecated Codex custom prompts as the canonical workflow surface.
- Do not edit `.agents/**` or `.codex/**` during ordinary Loki workflow
  execution unless the user explicitly asks for installation or synchronization.
- Do not promote project-specific context into the Loki package.
