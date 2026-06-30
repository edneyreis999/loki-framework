---
name: loki-action-plan-authoring
description: Create or review executable Loki action plans from technical analysis, briefs, feedback, or approved objectives. Use when generating `tasks.md`, `task-N.M.md`, phase folders, dependencies, human loops, concrete references, observable validation, or when improving `loki:generate-action-plan` outputs.
when_to_use:
  - "Use when creating or reviewing executable Loki action plans from analysis, briefs, feedback, or approved objectives."
  - "Use when generating tasks.md, task-N.M.md, phase folders, dependencies, human loops, references, or observable validation."
  - "Use when improving outputs from loki:generate-action-plan."
argument-hint: "[analysis path, scope, plan directory, gates]"
arguments:
  required: []
  optional:
    - analysis_path
    - scope
    - plan_directory
    - gates
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
  package_skill: "skills/loki-action-plan-authoring/SKILL.md"
shell: {}
---

# loki-action-plan-authoring

## Procedure

1. Confirm the planning input: technical analysis, brief, feedback, approved
   objective, scope boundaries, forbidden surfaces, and known human decisions.
2. Read only the sources required to plan safely. Use `loki-index-navigator`
   when durable consumer documentation in `/docs` is relevant.
3. Build the phase model before writing files:
   - phases are sequential and independently checkable;
   - every phase has an observable validation;
   - every task is concrete, dependency-aware, and sized for one focused
     implementation pass;
   - every task declares write owner, `target_files`, `allowed_writes` and
     `scoped_write_domains` when a specialist agent may execute as
     `task_scoped_writer`;
   - future sensitive writes are represented as gates, not hidden permission.
4. Propose the plan directory name and wait for explicit approval before
   creating files.
5. Generate `tasks.md`, one `task-N.M.md` per task, and phase subfolders under
   `interaction/`, `builds/`, and `retrospetivas/`.
6. Run the structural checks from
   [action-plan-contract.md](references/action-plan-contract.md) before
   declaring the plan ready.

## Non-Negotiables

- Do not invent references. Use `TODO: localizar` when a source is needed but
  not found.
- Do not create generic tasks such as "implement feature". Split work into
  concrete actions with an expected 2-4 hour implementation range.
- Do not skip phases. If phase N is required before phase N+1, declare the
  dependency explicitly.
- Do not write outside the approved plan directory.
- Do not declare runtime, integration, UI, data persistence, or generated output
  validated without the required human or automated gate.

## Required Contract

Read [action-plan-contract.md](references/action-plan-contract.md) when creating
or reviewing a plan. It defines the directory shape, `tasks.md` fields,
`task-N.M.md` fields, validators, stop conditions, and resume expectations.

Use these package-root templates when writing artifacts:

- `templates/tasks-template.md`
- `templates/task-template.md`

## Output Standard

The final plan must let `loki:run-plan` or another agent resume from disk
without conversation memory. Include the next action, blocked decisions, human
loops, write owner, target files, validators, and expected observable result in
the files themselves.
