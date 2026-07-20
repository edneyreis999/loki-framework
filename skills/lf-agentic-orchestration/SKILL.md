---
name: lf-agentic-orchestration
description: "Coordinate Loki agentic development: preflight, selected fan-out, XML state, gates, autonomous checkpoints, completion/evidence, non-blocking execution-knowledge capture, liveness, digest and backlog."
when_to_use:
  - "Use when a Loki workflow needs agentic analysis before planning or autonomous phase execution with resumable state."
  - "Use when coordinating selected agents, XML run state, decision gates, completion reports, execution-knowledge capture, digest, backlog, or per-agent retrospectives."
argument-hint: "[run directory, demand, optional scope]"
arguments:
  required: []
  optional:
    - run_directory
    - demand
    - scope
disable-model-invocation: false
user-invocable: false
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - multi-agent analysis with material conflicts
  - unresolved decision gates before action planning
  - target file conflicts between agent runs
  - autonomous execution across multiple planned phases
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-agentic-orchestration/SKILL.md"
shell: bash
type: skill
status: draft
used_by:
  - loki-agentic-development
---

# lf-agentic-orchestration

## Purpose

Provide the reusable orchestration rules behind an agentic Loki run. The
invoking command owns the public workflow, user-facing gates and allowed writes;
this skill defines how to select agents, keep XML state resumable, avoid unsafe
parallel writes, hand off to planning and execution, and record completion.

## Procedure

1. Read the orchestration contract:
   [agentic-orchestration-contract.md](references/agentic-orchestration-contract.md).
2. Confirm the active run directory, demand, requested scope, allowed writes,
   forbidden writes, validators and human gates.
3. Build an agent preflight from the active agent catalog. Select only agents
   with a concrete `selection_reason`; record skipped agents when the reason is
   useful for later review.
4. Create or update split XML state for the run: run manifest, analysis
   manifest, agent POVs, reviews, synthesis, agent run reports and digest.
5. Stop before action planning if any unresolved `must_ask_now` gate remains.
6. Treat specialist delegation as required for material work: nontrivial
   multi-source reading, technology-specific execution, sensitive/runtime
   writes, material validation, or work that would consume substantial main
   thread context. Fan-out only when selected agents have disjoint read context
   or disjoint write targets. Shared `target_files` require serialized
   ownership. Keep trivial, single-source, low-risk work local only with a
   recorded exception.
7. Run one cross-review round when material conflict or risk is present. Convert
   unresolved material conflict into a gate, targeted read or stop condition.
8. Hand off to action planning only after analysis state is complete enough to
   generate executable phases without new human questions.
9. During autonomous execution, propagate the requested Write Test review
   frequency unchanged when supplied and preserve its absence otherwise, then
   invoke `loki-run-plan` once with
   `EXECUTION_SCOPE=plano`. The executor alone derives effective policy,
   validates/applies enum/default, and owns materiality and checkpoints. Record blockers or post-execution items instead
   of asking new human questions mid-run.
10. Require a compact completion record for every agent handoff. The
    orchestrator captures a validated evidence manifest after completion or
    records an explicit `partial`, `unavailable` or `unsupported` gap. A
    retrospective is human- or explicitly-command-invoked; never auto-invoke
    one as a fallback for absent evidence.
11. Persist completion/evidence before dispatching any knowledge enrichment.
    Apply `lf-execution-knowledge-capture`, use a unique entry target per
    material handoff, continue without waiting, and reconcile capture state
    serially at existing checkpoints. At final completion interrupt/cancel a
    non-terminal cataloger and record `partial`; capture failure never blocks a
    validated implementation or promotes policy.
11. Validate state with the available agentic run-state validator before
    treating the run as resumable or fixture-ready.

## Inputs

- Demand text or demand file.
- Active run directory.
- Agent catalog with capability, mode, write and risk metadata.
- Template set for agentic XML and backlog artifacts.
- Human decision records, if any.
- Allowed writes, forbidden writes, validators and gates from the invoking
  command or active plan.

## Outputs

- Selected and skipped agent records with `selection_reason`.
- XML run state and analysis state.
- Agent POVs, optional reviews and synthesis.
- Plan handoff state.
- Agent run reports with `agent_run_id`, `handoff_id`, owner, target files,
  validators, gates, evidence, completion status and blockers.
- Digest and backlog records.
- Execution-knowledge entry references or explicit degraded capture states.
- Explicit retrospective eligibility for material agent work; no automatic run.

## Limits

- Do not invoke every available agent by default.
- Do not let the main thread absorb material analysis, writing or validation
  when an applicable agent exists, unless the invoking workflow records a
  concrete exception, scope, risk and validation owner.
- Do not treat file existence as a valid skip signal without freshness data.
- Do not allow parallel agent runs to share `target_files` unless ownership is
  serialized before writing.
- Do not mark runtime behavior, integrations, persisted state or perceptible
  output as validated without the relevant human gate.
- Do not replace `loki-run-plan` or call it once per phase; use one resumable
  plan-scope invocation as the executor when the invoking workflow reaches
  planned execution.
- Do not promote learnings into durable rules automatically. Record digest and
  backlog items for a later improvement workflow.
- Do not let a cataloger write shared run state, manifest, digest or backlog,
  and do not make its availability, latency or validator a completion gate.

## Required Gates

- `interview` before planning when the demand or material requirement is
  ambiguous and no local source resolves it.
- `approval` for installation, policy changes, sensitive writes or durable
  promotion.
- `technical-review` for command, skill, agent, template, validator or
  consolidated documentation changes.
- `<human_validation_gate>` for behavior on `<consumer_runtime_surfaces>`.

## Validation

- XML state parses.
- Every selected agent has `selection_reason`.
- Every agent run has unique `agent_run_id` and `handoff_id`.
- Writers declare owner, `target_files`, `allowed_writes`, validators and
  gates.
- Material work declares an agent owner or an explicit orchestrator exception
  with reason, scope, risk and validation owner.
- No unresolved `must_ask_now` gate exists before plan generation.
- Parallel groups have no target-file conflict.
- Completed agent runs include status, report path and evidence.
- Every knowledge capture has a unique target and one typed state; only a valid
  entry may be `captured`, and degraded states preserve reason/next path.
