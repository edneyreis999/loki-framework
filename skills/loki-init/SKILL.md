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
6. Before falling back from agent fan-out, run an explicit capability preflight
   for the active adapter. In Codex, explicitly request subagent/delegation
   capability and use directed tool discovery for multi-agent/subagent tools.
   Treat discovered tool namespaces as adapter/session evidence, not universal
   Loki package contracts.
7. Build an `agent_init_envelope` for each selected agent, including
   `target_document`, `target_inventory`, `target_retrospective`,
   `allowed_sources`, `forbidden_writes`, `context_budget` and `write_mode`.
8. Keep current agents read-only or proposal-only. Prefer structured handoffs
   from specialist agents and serial materialization by the orchestrator for
   final documents and inventories.
9. When per-agent technical retrospectives are required, the selected agent may
   write only its exact `target_retrospective` under the active phase
   retrospective directory. If the runtime cannot support that file-specific
   exception, require `retrospective_handoff` and record the limitation.
10. For Codex subagent fan-out, use conservative batches, prefer the configured
    `agents.max_threads` when known, otherwise use the documented default of 6
    as an initial ceiling, record observed limits and close completed agents
    before opening a later batch.
11. Require document, inventory and retrospective per selected agent, or a
   structured failure artifact.
12. Record planned, invoked, blocked and skipped agents with reasons before
    consolidation.
13. Consolidate serially: conflicts, open questions, docs index, init README,
    task state and next recommended Loki command.
14. Run validators from the command contract and record evidence in
    `planos/000-init-loki/builds/fase1/` when executing in a consumer project.

## Limits

- Do not write outside `docs/**` and `planos/000-init-loki/**`.
- Do not edit `.agents/**`, `.codex/**`, `.claude/**`, `AGENTS.md` or
  `CLAUDE.md` during init.
- Do not infer subagent capability absence from the initial tool surface alone;
  run adapter-aware discovery before choosing serial fallback.
- Do not let proposal-only agents write final docs, inventories, runtime,
  assets, code or config. The only default write exception is the selected
  agent's own exact technical retrospective path when the workflow requires it.
- Do not hardcode RPG Maker, Visual Novel, Unity, Unreal, Godot, Ren'Py or
  another engine into the core workflow.
- Do not declare runtime, UI, gameplay, audio, build, save/load, integration or
  persisted state validated without a later human-validation gate.
