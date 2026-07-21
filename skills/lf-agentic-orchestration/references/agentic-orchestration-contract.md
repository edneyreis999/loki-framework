# Agentic Orchestration Contract

Use this reference when an invoking Loki workflow needs reusable rules for
agentic analysis, planning handoff, autonomous execution checkpoints and
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
7. Decision preflight: stop before action planning while unresolved
   `must_ask_now` gates remain.
8. Planning handoff: generate an executable plan only after analysis state is
   complete enough for autonomous execution.
9. Execution: propagate the requested Write Test review frequency unchanged
   when supplied and preserve absence otherwise, then call the active plan
   executor exactly once with terminal scope `plano`; that executor alone
   validates/applies enum/default and owns the DAG, clamp, materiality, review
   checkpoints, serialized writes and validators.
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
  plan handoff.
- `agent-runs/faseN/<agent-run-id>.xml` (report schema 5): execution handoff,
  owner, writes, validators, gates, evidence, completion and blockers.
- `digest.xml` (schema 4): integrated run summary for review.
- `backlog.md`: postponed or non-blocking items for later handling.

The integrated parent records input presence before dispatch, then persists the
requested review frequency/provenance returned by the executor and the single
plan-scope handoff identity. It never persists a parent-derived
effective frequency. After the executor returns, state references the canonical
policy/checkpoints and reconciliation result that `loki-run-plan` owns.

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

Each agent run report should include:

- current status;
- report path;
- evidence;
- blockers;
- next action;
- whether retrospective is required.

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
validator accepts only manifest schema 4, agent-run report schema 5 and digest
schema 4; reader and schema 1/2 root compatibility are not current contracts.
Write-test-review remains schema 1 within those canonical roots. Retrospectives
remain an explicit evidence input. Durable promotion is a separate improvement
workflow with its own gate.

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
- Unresolved `must_ask_now` gate before action planning.
- Selected agent without `selection_reason`.
- Duplicate `agent_run_id` or `handoff_id`.
- Writer without owner, target files, allowed writes, validators or gates.
- Parallel runs sharing target files without serialization.
- Validator failure that affects resumability or write safety.
- Autonomous execution would need a new human question mid-run.
- Material analysis, writing or validation remains in the main thread without a
  recorded exception and validation owner.
- Requested review frequency conflicts with persisted state, a parent attempts
  to derive effective policy, or integrated execution would dispatch more than
  one plan-scope `loki-run-plan` handoff.

Cataloger availability/failure/timeout/handoff/validator is explicitly excluded
from these stop conditions. A final interrupted cataloger reconciled as
`partial` with reason and `minimum_next_path` is terminal for generic handoff
completion.
