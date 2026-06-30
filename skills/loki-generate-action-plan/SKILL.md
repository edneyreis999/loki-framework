---
name: loki-generate-action-plan
description: Run the Loki `loki:generate-action-plan` command workflow in Codex. Use when creating phased executable action plans, `tasks.md`, `task-N.M.md`, phase folders, dependencies, scoped write owners, validators, human loops, stop conditions, and resume-ready Loki plan artifacts.
when_to_use:
  - "Use when running loki:generate-action-plan to create phased executable Loki plans."
  - "Use when creating tasks.md, task-N.M.md, phase folders, dependencies, scoped write owners, validators, human loops, stop conditions, and resumable state."
argument-hint: "[analysis path, objective, plan directory]"
arguments:
  required: []
  optional:
    - analysis_path
    - objective
    - plan_directory
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
  - large multi-phase plan
  - complex dependencies or human gates
  - sensitive writes modeled for future execution
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-generate-action-plan/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:generate-action-plan
---

# loki-generate-action-plan

## Procedure

1. Read the installed command contract:
   [loki-generate-action-plan.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load `loki-action-plan-authoring` before creating or reviewing plan files.
4. Use `loki-template-library` when writing `tasks.md` or `task-N.M.md`.
5. Treat this skill as the Codex entrypoint for the command name
   `loki:generate-action-plan`.

## Limits

- Do not create plan files outside the approved plan directory.
- Do not invent references, approvals, validators, or human decisions.
