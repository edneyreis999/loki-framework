---
name: loki-run-plan
description: Run the Loki `loki:run-plan` command workflow in Codex. Use when executing an approved Loki plan phase from `tasks.md` and `task-N.M.md`, producing execution briefs, serialized writes, validation evidence, task status updates, and resumable state.
type: skill
status: draft
used_by:
  - loki:run-plan
---

# loki-run-plan

## Procedure

1. Read the installed command contract:
   [loki-run-plan.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load `loki-run-plan-execution` before planning or applying phase execution.
4. Use Codex custom agents from `.codex/agents/*.toml` only when the user asks
   for subagent delegation or parallel agent work.
5. Treat this skill as the Codex entrypoint for the command name
   `loki:run-plan`.

## Limits

- Do not write outside the active task scope.
- Do not declare runtime, UI, integration, persistence, or generated output
  validated without the required validator or human gate.
