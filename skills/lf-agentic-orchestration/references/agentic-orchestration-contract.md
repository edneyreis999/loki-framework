# Agentic Orchestration Contract

Use this reference when an invoking Loki workflow needs reusable rules for
agentic analysis, unified implementation handoff, autonomous checkpoints and
resumable XML state.

## Run Stages

1. Demand intake: capture the user's demand, requested scope, known constraints
   and forbidden writes.
2. Agent preflight: inspect the active agent catalog and select the minimum
   useful set of agents required by the work. Each selected agent needs a
   concrete `selection_reason`.
3. Analysis fan-out: create agent POV outputs only for selected agents. Fan-out
   is required for material work when perspectives are independent,
   domain-specific or risk-bearing, and it is allowed only when context or write
   targets are safe to split.
4. Cross-review: run a first review round when outputs conflict materially or
   the risk profile justifies a second perspective.
5. Synthesis: consolidate facts, conflicts, gates and plan handoff inputs.
6. Post-MVP wave checkpoint: record whether material gaps remain after the MVP
   synthesis. When gaps exist, compose additional read-only/proposal-only waves
   from the smallest useful set of agents selected by the current demand's
   gaps, surfaces and risks. Do not use a fixed agent list.
7. Decision preflight: stop before unified implementation while unresolved
   `must_ask_now` gates remain.
8. Analysis handoff: materialize a readable, decision-complete Markdown
   analysis from the current POV/review/synthesis state.
9. Execution: call `loki-implement-feature` exactly once with the original
   validated demand and that Markdown `analysis_file`. The unified command owns
   plan/DAG creation, target decisions, scoped writes, AC validation, retry,
   resume and terminal dashboard.
10. Completion: collect a compact completion record, validated evidence or an
   explicit gap, blockers, digest and backlog. Retrospective execution is an
   explicit human or command action, never an automatic fallback.

## Agent Selection

Selection should be auditable and small. Use capability tags, phase roles,
agentic modes, write classes, risk tags, project tags, parallel-safety metadata
and technology routes from the active catalog.

Record this for every selected agent:

- `agent_name`
- `selection_reason`
- `capability_tags`
- `phase_role`
- `agentic_mode`
- `write_class`
- `risk_tags`
- `parallel_safe`
- planned handoff scope

Record skipped agents only when the skip affects review, traceability or later
debugging.

## Main Thread Boundary

The main thread orchestrates intake, preflight, routing, compact synthesis,
state, gate handling and final reporting. It should not perform material
specialist work when an applicable agent exists.

Delegate material work when at least one trigger applies:

- nontrivial multi-source reading or noisy research;
- technology-specific interpretation, implementation or validation;
- sensitive or runtime-facing writes;
- material validation, QA, review or independent reproduction;
- broad file inspection that would consume substantial main-thread context;
- conflicting evidence that needs an isolated second judgment.

The orchestrator may keep work local only when it is trivial, single-source,
low-risk, and cheaper than a handoff. Record that exception with reason, scope,
risk accepted and validation owner. If the exception cannot be stated clearly,
delegate.

For additional waves after synthesis, record this for each wave:

- `wave_id`
- `selection_reason`
- analysis question
- affected surface
- selected agents
- `agentic_mode`
- risk
- expected validator
- stop criterion

## Fan-Out Rules

Fan-out is required for material work and allowed when:

- agents answer independent questions;
- target files are absent, read-only or disjoint;
- the active state has a unique owner for each planned write;
- validators and gates are known before write execution.

Fan-out should be avoided, with the exception recorded when work stays local,
when:

- the demand is trivial;
- every useful answer depends on a single source;
- multiple agents would write the same target file;
- a material gate blocks analysis or planning.

When fan-out is avoided for material work, the state must still record why the
orchestrator kept the work and who validates the result.

## XML State Shape

Use split state to keep files reviewable and resumable:

- `agentic-run-manifest.xml` (schema 4): run-level demand, phase, selected
  agents, handoffs, gates, invalidation, validators and next action.
- `analise/manifest.xml`: analysis-stage selected agents, skipped agents, POVs,
  reviews, synthesis and decision gates.
- `analise/agentes/<agent-name>.xml`: POV from one selected agent.
- `analise/agentes/<agent-name>-review.xml`: optional cross-review result.
- `analise/sintese.xml`: orchestrator synthesis, post-MVP wave checkpoint and
  Markdown analysis handoff source.
- `analise/technical-analysis.md`: readable decision-complete input for the
  single unified implementation handoff.
- `agent-runs/faseN/<agent-run-id>.xml` (report schema 6): execution handoff,
  owner, writes, validators, gates, evidence, completion and blockers.
- `digest.xml` (schema 4): integrated run summary for review.
- `backlog.md`: postponed or non-blocking items for later handling.

Manifest, agent-run report and digest projections use exactly one current
handoff shape after the Markdown analysis is validated:

```xml
<implementation_handoff schema_version="1">
  <handoff_id>implementation-handoff-v1:&lt;stable-id&gt;</handoff_id>
  <command>loki-implement-feature</command>
  <demand_ref>&lt;validated-demand-locator&gt;</demand_ref>
  <demand_digest>sha256:&lt;64-lowercase-hex&gt;</demand_digest>
  <analysis_file>&lt;run-directory&gt;/analise/technical-analysis.md</analysis_file>
  <analysis_digest>sha256:&lt;64-lowercase-hex&gt;</analysis_digest>
  <plan_directory>&lt;run-directory&gt;/implementation</plan_directory>
  <status>scheduled|dispatched|completed|partial|blocked|failed|cancelled</status>
  <execution_state_ref>&lt;loki-run-state-locator-or-null&gt;</execution_state_ref>
  <execution_state_digest>sha256:&lt;64-lowercase-hex-or-null&gt;</execution_state_digest>
  <result_ref>&lt;execution-result-locator-or-null&gt;</result_ref>
  <dashboard_ref>&lt;dashboard-locator-or-null&gt;</dashboard_ref>
  <next_action>&lt;non-empty&gt;</next_action>
</implementation_handoff>
```

Require every field exactly once. Before dispatch, returned-state/result fields
are null; after terminal return they reconcile to the command result. A second
handoff, another command identity, missing Markdown analysis, changed input
digest, or parent-created execution state is invalid.

The integrated parent records demand and analysis locators/digests before
dispatch, plus exactly one typed `implementation_handoff` identity. After the
unified command returns, state references its current execution result, state
digest, completion/evidence and dashboard locators. The parent never creates a
parallel plan, DAG, validation cycle, retry ledger or terminal status.

## Freshness and Invalidation

Do not skip work because an output file exists. Each output should carry a
freshness signature with:

- input paths or demand identifiers;
- optional hash or mtime;
- upstream output dependencies;
- decision gate IDs that affected the output;
- validator names and relevant versions when known.

When a gate changes, invalidate only the affected analysis outputs, tasks or
agent runs.

## Liveness

Treat timeout as an operational checkpoint. Mark it as failure only when there
is no status or output, ownership was violated, a blocking gate exists, or the
agent report declares an error.

Immediately before any silence-based abort, interrupt, or cancel, invoke the
adapter-observed liveness probe and persist its timestamp, adapter/source,
outcome and reason in report schema `6` and the correlated metrics span. An
observed `running` or `progress` outcome forbids that stop. `unsupported` or
`unavailable` creates no heartbeat and must be recorded with a reason before
another declared policy stop is evaluated. Explicit user cancellation is a
separate correlated event and is not rewritten as silence.

Each agent run report should include:

- current status;
- report path;
- evidence;
- blockers;
- next action;
- whether retrospective is required.
- timing/clock provenance and execution-metrics ref/digest/status;
- exact/estimated/unavailable usage category without mixed totals;
- replay/validator and materiality-precheck correlation;
- liveness-probe outcome when a silence stop was considered.

Treat main-thread context pressure as a liveness signal. When the next step
requires loading broad raw sources, long data files, multiple retrospectives or
large diffs, prefer read-only digests or isolated agent handoffs. Do not wait
for context exhaustion before delegating.

## Completion, evidence and retrospective eligibility

Use compact completion reports for read-only lookups, trivial proposals or
skipped agents.

Require a technical retrospective when an agent:

- wrote a file;
- produced substantial analysis;
- performed material validation;
- found a blocker;
- resolved a real difficulty;
- generated a reusable lesson that may later be promoted.

Every canonical manifest handoff carries `agent_run_id`, `handoff_id`, an
`evidence_id` and evidence-manifest path. Handoff dependencies, when present,
use `depends_on_handoff_id` and must be acyclic. The agentic run-state
validator accepts only manifest schema 4, agent-run report schema 6 and digest
schema 4; reader and schema 1/2 root compatibility are not current contracts.
Report schema 5 is also superseded and rejected without migration or fallback.
Retrospectives remain an explicit evidence input. Durable promotion is a
separate improvement workflow with its own gate.

## Execution knowledge capture and liveness

Evidence and execution knowledge are separate. At each material handoff or task
checkpoint, the orchestrator first persists the minimal sanitized completion
and evidence envelope. It may then dispatch `execution-knowledge-cataloger` in
parallel with a unique immutable target under
`<run>/execution-knowledge/entries/<capture-id>.xml`. The cataloger reads only
the supplied persisted sources and never writes a shared manifest, run state,
digest, backlog, plan, runtime or normative surface.

The implementation path never waits for enrichment. At normal checkpoints the
orchestrator serially reconciles `captured`, `partial`, `failed`, `unsupported`
or `skipped-nonmaterial`. At the final checkpoint, interrupt or cancel a
non-terminal cataloger and record `partial`, reason and `minimum_next_path`.
Knowledge validation failure degrades capture only. Only
`loki-continuous-improvement` may later deduplicate lineage and promote through
its normal root-cause and human gates.

## Stop Conditions

- Missing run directory or impossible-to-resolve state path.
- Unresolved `must_ask_now` gate before unified implementation.
- Selected agent without `selection_reason`.
- Duplicate `agent_run_id` or `handoff_id`.
- Writer without owner, target files, allowed writes, validators or gates.
- Parallel runs sharing target files without serialization.
- Validator failure that affects resumability or write safety.
- Autonomous execution would need a new human question mid-run.
- Material analysis, writing or validation remains in the main thread without a
  recorded exception and validation owner.
- Missing/invalid Markdown analysis, divergent demand/analysis identity, more
  than one `loki-implement-feature` handoff, or any parent-owned duplicate plan,
  DAG, target decision, validation cycle, retry or terminal projection.

Cataloger availability/failure/timeout/handoff/validator is explicitly excluded
from these stop conditions. A final interrupted cataloger reconciled as
`partial` with reason and `minimum_next_path` is terminal for generic handoff
completion.

Timing and usage are measurement-only. Exact usage requires a verified
run-scoped adapter counter; estimates are low-confidence partial
`utf8-byte-estimate-v1`; cumulative/account-window is never per-agent;
unavailable carries a reason. There are no token/cost budgets or automatic cost
stops, and telemetry degradation never changes functional status.
