---
name: loki-generate-action-plan
description: Run the Loki `loki:generate-action-plan` command workflow in Codex. Use when creating phased executable action plans, `tasks.md`, `task-N.M.md`, phase folders, dependencies, validators, human loops, stop conditions, and resume-ready Loki plan artifacts.
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
