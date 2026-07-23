---
name: lf-agentic-orchestration
description: "Coordinate Loki agentic development: selected POV fan-out, synthesis, decision-complete Markdown analysis, one unified implementation handoff, completion/evidence, non-blocking execution-knowledge capture, digest and backlog."
when_to_use:
  - "Use when a Loki workflow needs agentic analysis before one unified implementation handoff with resumable state."
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
  - unresolved decision gates before unified implementation
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
parallel writes, make one unified implementation handoff, and record completion.

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
5. Stop before unified implementation if any unresolved `must_ask_now` gate remains.
6. Treat specialist delegation as required for material work: nontrivial
   multi-source reading, technology-specific execution, sensitive/runtime
   writes, material validation, or work that would consume substantial main
   thread context. Fan-out only when selected agents have disjoint read context
   or disjoint write targets. Shared `target_files` require serialized
   ownership. Keep trivial, single-source, low-risk work local only with a
   recorded exception.
7. Run one cross-review round when material conflict or risk is present. Convert
   unresolved material conflict into a gate, targeted read or stop condition.
8. Materialize one decision-complete Markdown analysis from the validated POV,
   review and synthesis state. Preserve its locator and evidence; do not use XML
   synthesis alone as the public command input.
9. Invoke `loki-implement-feature` exactly once with the original validated
   demand and that readable Markdown `analysis_file`. The unified command owns
   plan creation, DAG execution, target decisions, AC validation, retry, resume
   and dashboard. Record blockers or post-execution items instead of asking new
   human questions mid-run.
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
- XML run state and analysis state. Canonical run artifacts use manifest schema
  4, agent-run report schema 5 and digest schema 4; older or unknown root
  schemas are rejected.
- Agent POVs, optional reviews and synthesis.
- One Markdown-analysis-to-implementation handoff state.
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
- Do not expose `loki-agentic-development` as an alias, wrapper or replacement
  for `loki-implement-feature`. This orchestration adds selected POVs,
  cross-review, synthesis, digest and backlog before exactly one unified call;
  ordinary unified feature demands route directly to the public command.
- Do not promote learnings into durable rules automatically. Record digest and
  backlog items for a later improvement workflow.
- Do not let a cataloger write shared run state, manifest, digest or backlog,
  and do not make its availability, latency or validator a completion gate.

## Required Gates

- `interview` before planning when the demand or material requirement is
  ambiguous and no local source resolves it.
- `approval` for installation, policy changes, sensitive writes or durable
  promotion.
- A package candidate is recorded for a later
  `loki-continuous-improvement` execution with `destination_scope: package`;
  this orchestration does not invoke package Writer or Auditor.
- `<human_validation_gate>` for behavior on `<consumer_runtime_surfaces>`.

## Validation

- XML state parses.
- Every selected agent has `selection_reason`.
- Every agent run has unique `agent_run_id` and `handoff_id`.
- Writers declare owner, `target_files`, `allowed_writes`, validators and
  gates.
- Material work declares an agent owner or an explicit orchestrator exception
  with reason, scope, risk and validation owner.
- No unresolved `must_ask_now` gate exists before the Markdown analysis and
  unified implementation handoff.
- Exactly one handoff calls `loki-implement-feature` with demand and
  `analysis_file`; no phase loop or alternate executor exists.
- Parallel groups have no target-file conflict.
- Completed agent runs include status, report path and evidence.
- Every knowledge capture has a unique target and one typed state; only a valid
  entry may be `captured`, and degraded states preserve reason/next path.
