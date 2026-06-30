---
name: loki-init
description: Run the Loki `loki:init` command workflow in Codex to bootstrap consumer documentation under `docs/**` and operational state under `planos/000-init-loki/**`, using controlled discovery, agent envelopes, per-agent technical retrospectives, output contracts, validators, human gates, and resumable state.
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
   For `init_context_scoped_writer` agents, declare that each agent writes its
   own exact `target_document`; do not ask the orchestrator to write the
   document as a substitute handoff.
   For every invoked agent, declare that the agent must run
   `loki:retrospectiva-tecnica` before completion and write only its own exact
   `target_retrospective` under `planos/000-init-loki/retrospetivas/fase1/`.
   Verify the adapter can grant scoped write access to each invoked agent's own
   `target_retrospective`; if not, record the agent as `blocked` or `skipped`
   with a concrete reason before fan-out.
7. Before selecting agents, run an explicit agent catalog preflight for the
   active adapter. Prefer the installed `manifest.yaml` as the structured
   catalog for `supported_project_types`, `agent_project_tag_policy` and
   `agents[].project_tags`. Read approved adapter surfaces when present, such
   as `.codex/agents`, `.agents/agents`, `agents/`, `codex/agents` or an
   equivalent adapter role list only as availability/capability evidence.
   Record the catalog source, supported project types, base tag, project tags,
   available agents and discovery limits; reading install mirrors does not
   permit writing them.
8. Pass detected technology and candidate technology-specific skills into the
   selected agent envelopes without executing engine-specific rules in the core
   init workflow. Specialist agents decide whether a technology skill is needed.
9. Classify the project into exactly one `selected_project_type` from
   `supported_project_types`; `core` is not classifiable, it is the base tag
   that is always included. If `project_type_hint` is outside the supported
   list, record a conflict/open question before fan-out.
10. Build `inventory_required` from the ordered union of agents tagged with the
   base tag `core` plus agents tagged with `selected_project_type`, with no
   duplicates. Record `inventory_required_reasons` by agent. For
   `software-development`, selecting only `core` agents is valid until
   specialized agents receive that tag.
11. Classify selected agents into `init_context_scoped_writer` and
   `init_support_only` using the command contract.
12. Build an `agent_init_envelope` for each selected
   `init_context_scoped_writer`, including `project_tags`, `selection_reason`,
   `target_document`, exact `allowed_writes`, `allowed_sources`,
   `forbidden_writes`, `target_retrospective`,
   `completion_retrospective` and `write_mode`.
13. Require each `init_context_scoped_writer` to write only its own exact
   `target_document` under `docs/loki-init/`. If there is no useful content,
   the agent writes a structured failure in that same `target_document`.
14. Invoke `init_support_only` agents only when their read-only or proposal
   result is needed. They do not receive a default `<perspective>-context.md`,
   but they do receive `target_retrospective`, `completion_retrospective` and
   allowed write only for their own retrospective.
15. Require every invoked agent to execute `loki:retrospectiva-tecnica` after
   its assigned work and before agent completion, writing
   `planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md`
   with its own material execution frictions, validations, blockers, useful and
   bad inferences, residual risks and minimum next path.
16. For Codex subagent fan-out, use conservative batches, prefer the configured
    `agents.max_threads` when known, otherwise use the documented default of 6
    as an initial ceiling, record observed limits and close completed agents
    before opening a later batch.
17. Require a materialized `target_document` per selected
   `init_context_scoped_writer`.
18. Require a materialized `target_retrospective` per invoked agent.
19. Record `available`, `inventory_required`, `init_context_scoped_writers`,
    `init_support_only_agents`, `selected`, `planned`, `invoked`, `blocked`
    and `skipped` agents with reasons, plus `target_retrospectives`, before
    consolidation.
20. Consolidate serially: conflicts, open questions, docs index, init README,
    task state and next recommended Loki command.
21. Run validators from the command contract and record evidence in
    `planos/000-init-loki/builds/fase1/` when executing in a consumer project.

## Limits

- Do not write outside `docs/**` and `planos/000-init-loki/**`.
- Do not edit `.agents/**`, `.codex/**`, `.claude/**`, `AGENTS.md` or
  `CLAUDE.md` during init.
- Do not infer subagent capability absence from the initial tool surface alone;
  run adapter-aware discovery before choosing serial fallback.
- Do not infer a sufficient agent set from memory or from obvious role names;
  classify the project against `supported_project_types`, derive required
  agents from `manifest.yaml` project tags, and justify every required skipped
  agent.
- Do not let agents write outside the exact `target_document` and
  `target_retrospective` granted by `loki:init`; do not let
  `init_support_only` agents write final docs, runtime, assets, code or config.
- Do not use orchestrator handoff as a substitute for a per-agent retrospective
  when the invoked agent has a `target_retrospective`.
- Do not hardcode RPG Maker, Visual Novel, Unity, Unreal, Godot, Ren'Py or
  another engine into the core workflow.
- Do not declare runtime, UI, gameplay, audio, build, save/load, integration or
  persisted state validated without a later human-validation gate.
