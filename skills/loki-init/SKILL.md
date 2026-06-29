---
name: loki-init
description: Run the Loki `loki:init` command workflow in Codex to bootstrap consumer documentation under `docs/**` and operational state under `planos/000-init-loki/**`, using controlled discovery, agent envelopes, output contracts, validators, human gates, and resumable state.
when_to_use:
  - "Use when the user invokes `loki:init` or `init-loki` after installing Loki in a consumer project."
  - "Use when bootstrapping consumer docs and `planos/000-init-loki` without touching runtime, mirrors, AGENTS.md, or CLAUDE.md."
argument-hint: "[consumer_project_root, docs_root, plan_root, mode, engine_hint]"
arguments:
  required: []
  optional:
    - consumer_project_root
    - docs_root
    - plan_root
    - mode
    - engine_hint
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
  - consumer documentation bootstrap
  - multi-agent fan-out and serial consolidation
  - consumer write boundary ambiguity
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-init/SKILL.md"
  command_contract: "commands/loki-init.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:init
---

# loki-init

## Procedure

1. Read the installed command contract for `loki:init`.
2. Confirm `consumer_project_root`, `docs_root`, `plan_root`, mode and optional
   hints. Default to current directory, `docs` and `planos/000-init-loki`.
3. Declare allowed writes before writing: only `docs/**` and
   `planos/000-init-loki/**` in the consumer project.
4. Preserve forbidden writes: runtime, engine, assets, generated data,
   `.agents/**`, `.codex/**`, `.claude/**`, `AGENTS.md` and `CLAUDE.md`.
5. Produce or audit the common inventory and technology context before any
   agent fan-out.
6. Build an `agent_init_envelope` for each selected agent, including
   `target_document`, `target_inventory`, `target_retrospective`,
   `allowed_sources`, `forbidden_writes`, `context_budget` and `write_mode`.
7. Keep current agents read-only or proposal-only. If an agent cannot write,
   have it return structured content and write the allowed files from the
   orchestrator.
8. Require document, inventory and retrospective per selected agent, or a
   structured failure artifact.
9. Consolidate serially: conflicts, open questions, docs index, init README,
   task state and next recommended Loki command.
10. Run validators from the command contract and record evidence in
    `planos/000-init-loki/builds/fase1/` when executing in a consumer project.

## Limits

- Do not write outside `docs/**` and `planos/000-init-loki/**`.
- Do not edit `.agents/**`, `.codex/**`, `.claude/**`, `AGENTS.md` or
  `CLAUDE.md` during init.
- Do not hardcode RPG Maker, Visual Novel, Unity, Unreal, Godot, Ren'Py or
  another engine into the core workflow.
- Do not declare runtime, UI, gameplay, audio, build, save/load, integration or
  persisted state validated without a later human-validation gate.
