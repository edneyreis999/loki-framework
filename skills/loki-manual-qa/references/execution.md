---
doc_id: "loki-manual-qa-execution"
version: "2.0.0"
status: active
last_updated: "2026-08-01"
scope: "Exhaustive manual-QA source catalog, interaction, and restricted awaiting-manual-qa terminal promotion"
not_scope: "Runtime observation by Loki, per-test human evidence, production repair, or mutation outside terminal QA state"
authority: "skills/loki-manual-qa/SKILL.md"
canonical_source: "skills/loki-manual-qa/references/execution.md"
intended_llm_task: "routing"
source_priority: ["approved human decisions", "command entrypoint and this reference", "validated current run", "current referenced bytes"]
confidence: high
known_conflicts: []
replaced_by: null
---

# loki-manual-qa — Execution

## Purpose, boundaries and observable completion

Purpose: transform one validated `awaiting-manual-qa` plan into a complete,
human-usable dashboard and, only after an aggregate human statement that every
applicable item was tested, atomically promote the restricted human-validation
state to `completed`.

Start only with normalized Input, one current correlated LokiRunState v3 in
`awaiting-manual-qa`, one byte-equal `ready-for-manual-qa` handoff v2, and all
automatic validators/audits/gates terminal. Completion means every catalog
candidate is classified, every applicable source is covered by the attestation,
all referenced human-validation gates v2 are passed with its exact ref/digest,
task/AC/plan projections are promoted, canonical state/result/dashboard are
byte-consistent, consistency is published last, and transaction phase is
`committed` with no residue. Outputs are source catalog, complete dashboard,
interaction/attestation/report current views, transaction, manual result,
manual consistency, restricted canonical promotions and terminal response.

The main agent is orchestrator and managed-state owner. It validates Input,
builds the dependency plan, dispatches proposal-only `runtime-qa`, validates
every proposal, persists current views, interprets aggregate human language,
and owns the cross-record terminal commit. There is no applicable Write Agent
for an atomic promotion spanning gate records and canonical run
records; direct orchestration is the bounded exception. It never writes
production/runtime targets. Record this rationale, exact targets, owner,
validators, gates, success/failure and the future opportunity for a dedicated
manual-QA transaction writer in the completion record.

## Execution plan, dependencies and replanning

Execute in this dependency order:

1. Validate the complete upstream tree and freeze its refs/digests.
2. Enumerate the exhaustive candidate set from the handoff v2 arrays.
3. Dispatch one or more `runtime-qa` proposal envelopes; wait for every handoff
   to finish as `completed`, `failed`, `blocked` or `stopped`.
4. Validate proposals, derive the complete target set, and persist the
   transaction journal as the first manual-QA write. Only then publish the
   proposals, source catalog, dashboard and initial interaction/result.
5. Render every applicable step at once; help/pause/resume never mutates it.
6. Persist an issue transition or dispatch the independent
   `manual-qa-attestation-auditor`; persist its review through the journal and
   create aggregate attestation only after an approved correlated review.
7. Fresh-read all bytes; prepare and perform restricted canonical promotion;
   publish consistency last; validate the whole tree; commit transaction.
8. Render terminal Response only from the validated committed state.

Catalog depends on all proposal completions. Dashboard depends on catalog.
Attestation depends on the complete dashboard presentation. Promotion depends
on attestation, no open report, fresh upstream parity and a prepared
transaction. Consistency depends on every prior final write. If a proposal
changes applicability or guide content, discard dependent catalog/dashboard
views and rebuild. If issue resolution produces a new technical projection,
invalidate all dependent manual views, re-enumerate, redispatch and present the
whole dashboard again. Any other invalidated dependency blocks; never patch a
downstream digest to hide drift.

## Runtime-QA proposal handoff

Only `loki-manual-qa` may dispatch `runtime-qa` for manual-source work. Send a
self-contained envelope with plan/run/execution identity, candidate refs and
exact-byte digests, source kinds, statements/provenance, target surface facts,
automatic evidence, environment constraints, `allowed_writes: []`, all manual
and production paths forbidden, validators, stop conditions and this schema:

```yaml
runtime_qa_source_proposal:
  schema_version: 1
  run_id: "loki-run-v2:<64 lowercase hex>"
  execution_id: "loki-execution-v2:<64 lowercase hex>"
  caller: "loki-manual-qa"
  agent: "runtime-qa"
  allowed_writes: []
  candidate_ref: "one exact handoff candidate ref"
  candidate_digest: "sha256:<current source bytes or canonical fragment>"
  source_kind: "acceptance-criterion | human-gate | changed-surface"
  applicability: "applicable | not-applicable"
  not_applicable_reason: "non-empty only for not-applicable, otherwise null"
  environment: "concrete non-generic environment"
  prerequisites: "concrete non-generic prerequisites"
  initial_state: "concrete observable start"
  actions: ["concrete ordered reproduction action"]
  expected_result: "concrete observable expected result"
  success_signal: "concrete observable success"
  failure_signal: "concrete observable failure"
  cleanup: "concrete cleanup or explicit not-needed reason"
  automation_limit: "concrete reason human observation remains material"
  evidence_refs: ["read-only source/evidence locator"]
  completion_record:
    status: "completed | failed | blocked | stopped"
    validators: ["executed proposal validator"]
    gates: []
    risks: []
    next_destination: "loki-manual-qa orchestrator"
```

`runtime-qa` is read-only/proposal-only: it does not observe runtime, ask the
human, persist a catalog, mutate state or approve a gate. A non-completed
handoff blocks dependent publication. The orchestrator rejects invented refs,
short or placeholder fields, materially repeated guides across unrelated
candidates, guides not bound to their candidate, non-observable steps,
unsupported applicability and extra keys.

## Exhaustive source catalog

The handoff v2 closed keys are `schema_version`, `status`, `run_id`,
`execution_id`, `plan_directory`, `automatic_evidence_refs`,
`manual_qa_result_ref`, `manual_qa_attestation_ref`, `task_refs`,
`acceptance_criterion_refs`, `gate_refs`, `changed_target_refs`, and `reason`.
Require schema 2, `ready-for-manual-qa`, technical/canonical status
`awaiting-manual-qa`, exact anchors, unique ordered refs and byte equality in
state/result/dashboard/consistency. No handoff v1 reader exists.

The candidate set is exactly the ordered concatenation of:

1. every `acceptance_criterion_ref` in handoff order;
2. every `gate_ref` whose gate-record-v2 `kind` is `human-validation`, in
   handoff order (automatic gates remain eligibility evidence);
3. every `changed_target_ref` in handoff order, represented as changed-surface.

Each changed-target ref is the exact production target path projected from
completed handoff-record `target_digests` in task → handoff → target-row order,
deduplicated by first occurrence. Read its current bytes, require equality with
the corresponding automatic `path=digest` provenance, and use that byte digest
as the candidate/source digest; never replace it with a composite provenance
digest. The ref grants no production write.

A changed-surface guide may state only observable behavior already bound to
the owning task by a persisted acceptance-criterion statement or immutable
human-gate source statement. Record the exact statement locator and digest in
the proposal/source coverage. If no such observable fact exists, classify the
changed surface `not-applicable` with that concrete absence as its reason;
never invent behavior from a filename, implementation bytes or task title.
Guides must retain real candidate/source locators and digests. Reject an
unrelated source fact and reject near-duplicate guides even when paths or
digests have merely been substituted.

Require exact equality with task-validation ACs, all current gate refs and all
changed targets in the upstream tree. No candidate may be missing, duplicated
or synthesized. Persist:

```yaml
manual_qa_source:
  schema_version: 1
  source_kind: "acceptance-criterion | human-gate | changed-surface"
  source_ref: "exact current candidate locator"
  source_digest: "sha256:<exact target bytes or canonical immutable AC/gate source fragment>"
  source_order: "zero-based JSON integer in exhaustive candidate order"
  applicability: "applicable | not-applicable"
  not_applicable_reason: "non-empty evidence-based reason iff not-applicable; otherwise null"
  task_refs: ["covered exact task locator"]
  acceptance_criterion_refs: ["covered exact AC locator"]
  gate_refs: ["covered exact gate-v2 locator"]
  changed_surface_refs: ["covered exact changed-target locator"]
  observable_fact_refs: ["exact immutable statement locator"]
  observable_fact_digests: ["sha256:<exact immutable statement fragment>"]
  observable_fact_statements: ["exact observable source statement"]
  guide_fact_bindings:
    environment: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    prerequisites: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    initial_state: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    actions: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    expected_result: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    success_signal: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    failure_signal: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    cleanup: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
    automation_limit: {fact_ref: "exact source fact", fact_digest: "sha256:<same fact>"}
  environment: "concrete"
  prerequisites: "concrete"
  initial_state: "concrete"
  actions: ["one or more concrete ordered actions"]
  expected_result: "concrete observable outcome"
  success_signal: "concrete observable signal"
  failure_signal: "concrete observable signal"
  cleanup: "concrete action or not-needed reason"
  automation_limit: "concrete material human-observation limit"
  runtime_qa_proposal_ref: "persisted sanitized proposal evidence locator"
  runtime_qa_proposal_digest: "sha256:<exact proposal bytes>"

manual_qa_source_catalog:
  schema_version: 1
  run_id: "loki-run-v2:<64 lowercase hex>"
  execution_id: "loki-execution-v2:<64 lowercase hex>"
  plan_directory: "canonical planos/<plan>"
  state_ref: "<plan>/tasks.md#loki_run_state"
  state_digest: "sha256:<canonical state>"
  handoff_ref: "<plan>/tasks.md#loki_run_state.manual_qa_handoff"
  handoff_digest: "sha256:<canonical handoff v2>"
  candidate_refs: ["exact exhaustive ordered candidate refs"]
  candidate_digests: ["sha256:<exact candidate source>"]
  sources: ["exact ordered manual_qa_source v1 rows"]
  applicable_source_refs: ["exact applicable subset in source order"]
  not_applicable_source_refs: ["exact not-applicable subset in source order"]
  coverage_digest: "sha256:<canonical candidate refs/digests + source coverage>"
  catalog_digest: "sha256:<canonical record excluding catalog_digest>"
```

Every row is required. `not-applicable` requires a concrete proposal-supported
reason and is preserved in the catalog but omitted from dashboard steps.
`applicable` requires a null reason and a complete concrete guide. Reject empty
applicable set, generic boilerplate, uncovered refs, extra rows or a coverage
digest mismatch.

A required pending human-validation gate v2 is always `applicable`;
Runtime-QA and the orchestrator may never mark it `not-applicable`. Doing so
would waive the gate that made the plan `awaiting-manual-qa` and is a hard
schema/coverage failure.

## Dashboard and interaction transition table

Derive one `MQ-<n>` step for each applicable catalog row, preserving source
order and its entire guide verbatim. IDs are consecutive in applicable order;
`source_order` remains the catalog order and therefore need not equal the step
array index when earlier sources are not applicable. Persist catalog ref/digest,
all steps, applicable digest and the applicable/not-applicable source refs.
Render every step without truncation or pagination.

All current views are exact-key closed schema v1. Their keys are:

```yaml
manual_qa_step:
  schema_version: 1
  id: "MQ-<two-or-more digits>"
  source_kind: "acceptance-criterion | human-gate | changed-surface"
  source_ref: "exact catalog ref"
  source_order: "exact catalog order"
  title: "concrete expected-result title"
  environment: "concrete"
  prerequisites: "concrete"
  initial_state: "concrete"
  actions: ["concrete ordered action"]
  expected_result: "concrete observable outcome"
  success_signal: "concrete observable signal"
  failure_signal: "concrete observable signal"
  cleanup: "concrete action/reason"
  automation_limit: "concrete human-observation limit"

manual_qa_dashboard:
  schema_version: 1
  run_id: "typed run id"
  execution_id: "typed execution id"
  plan_directory: "canonical plan"
  state_ref: "canonical state locator"
  state_digest: "canonical state digest"
  handoff_ref: "canonical handoff locator"
  handoff_digest: "canonical handoff digest"
  implementation_result_ref: "canonical ref"
  implementation_result_digest: "exact-byte digest"
  implementation_dashboard_ref: "canonical ref"
  implementation_dashboard_digest: "exact-byte digest"
  implementation_consistency_ref: "canonical ref"
  implementation_consistency_digest: "exact-byte digest"
  demand_ref: "canonical ref"
  demand_digest: "exact-byte digest"
  analysis_ref: "canonical ref"
  analysis_digest: "exact-byte digest"
  source_catalog_ref: "canonical ref"
  source_catalog_digest: "exact-byte digest"
  applicable_source_refs: []
  not_applicable_source_refs: []
  steps: []
  applicable_steps_digest: "canonical steps digest"
  dashboard_digest: "canonical self digest"

manual_qa_attestation:
  schema_version: 1
  run_id: "typed run id"
  execution_id: "typed execution id"
  applicable_steps_digest: "canonical steps digest"
  demand_digest: "exact demand-byte digest"
  analysis_digest: "exact analysis-byte digest"
  human_statement: "exact non-empty human statement"
  declaration: "all-applicable-manual-tests-tested-and-approved"
  attestation_review_ref: "exact independent review locator"
  attestation_review_digest: "sha256:<exact review bytes>"
  recorded_at: "RFC3339 UTC"

manual_qa_attestation_review:
  schema_version: 1
  run_id: "typed run id"
  execution_id: "typed execution id"
  reviewer_identity: "manual-qa-attestation-auditor"
  independent_agent_run_evidence_ref: "exact independent execution evidence locator"
  independent_agent_run_evidence_digest: "sha256:<exact evidence bytes>"
  statement_digest: "sha256:<exact raw statement bytes>"
  dashboard_ref: "immutable dashboard-presentation locator"
  dashboard_digest: "sha256:<exact presentation bytes>"
  applicable_steps_digest: "canonical steps digest"
  evaluator_policy_id: "manual-qa-semantic-policy-v1"
  evaluator_policy_digest: "sha256:<pinned policy bytes>"
  assessment_ref: "exact orchestrator assessment locator"
  assessment_digest: "sha256:<exact assessment bytes>"
  signals: "exact closed five-boolean mapping"
  decision: "approve | reject"
  rationale: "independent semantic rationale"
  confidence: "low | medium | high"
  completion_record: "closed status/validators/gates/risks/success/failure mapping"
  review_digest: "canonical self digest"

manual_qa_report:
  schema_version: 1
  report_id: "manual-qa-report-v1:<digest>"
  run_id: "typed run id"
  execution_id: "typed execution id"
  status: "open | resolved"
  kind: "failure | blocker"
  summary: "1..280 Unicode code points"
  impact: "non-empty"
  next_action: "non-empty"
  recorded_at: "RFC3339 UTC"
  resolution_ref: "canonical ref or null"
  resolution_digest: "exact bytes or null"
  resolved_at: "RFC3339 UTC or null"
  revalidation_refs: []
  revalidation_digests: []

manual_qa_interaction:
  schema_version: 1
  run_id: "typed run id"
  execution_id: "typed execution id"
  status: "in-progress | awaiting-attestation | paused | issue-open | issue-resolved | attested | stopped"
  attestation_ref: "canonical ref or null"
  attestation_digest: "exact bytes or null"
  report_ref: "canonical ref or null"
  report_digest: "exact bytes or null"
  interaction_digest: "canonical self digest"
```

Persist separate interaction, attestation and report files under the handoff
run directory. Enforce this closed table:

Source catalog, dashboard, interaction, report and manual result are the
current correlated views of the run. Publish their updates serially under the
one orchestrator owner and treat the set atomically through transaction phase
and exact parity; attestation alone is create-exclusive/immutable.

| Interaction | Attestation | Report | Result | Allowed meaning |
| --- | --- | --- | --- | --- |
| `in-progress` | absent | absent | `in-progress` | catalog/dashboard transaction is being published |
| `awaiting-attestation` | absent | absent | `pending-input` | complete dashboard shown |
| `paused` | absent | absent or resolved | `in-progress` | explicit pause; resume from disk |
| `issue-open` | absent | open | `blocked` | failure or blocker requires external correction |
| `issue-resolved` | absent | resolved | `in-progress` | revalidation/rederivation required |
| `attested` | present | absent or resolved | `in-progress` | terminal commit not yet complete |
| `attested` | present | absent or resolved | `completed` | transaction committed and consistent |
| `stopped` | absent | absent or resolved | `stopped` | explicit safe stop with resume reason |

All other pairs fail. Help reads one step and changes no bytes. Pause writes
only the correlated current interaction/result/transaction phase. Attestation
is create-exclusive and immutable. The LLM accepts any unambiguous natural
language statement that the human already tested everything; no approval word
or magic token is required. It preserves `human_statement` and normalizes
`declaration` to `all-applicable-manual-tests-tested-and-approved`. The
deterministic validator checks the canonical record/correlation, not a lexical
whitelist.

The help handler snapshots every plan-tree file digest before lookup, resolves
exactly one current MQ ID, and requires the complete after-snapshot to be
identical. The command accepts only `human_statement` from the user; identity,
owner, policy, decision, signals and review are never caller-controlled input.
The orchestrator prepares the semantic assessment under the pinned current-only assessor,
owner and evaluator-policy identity/digest after reading the current
interaction and immutable `dashboard-presentation.json`. It records rationale
and five signals: `explicit_completed_all`, `ambiguous`, `negated`,
`future_intent` and `partial_scope`. The mechanical validator only checks the
closed record, provenance, correlation, signal types and the decision implied
by those persisted signals. It does not decide the meaning of free-form prose.
Persist `semantic-assessment.json` with the exact
statement/digest, persisted dashboard-presentation ref/digest,
applicable-steps digest, pinned assessor/owner/policy, signals, derived
decision, rationale and self-digest. Then dispatch the independent read-only,
proposal-only `manual-qa-attestation-auditor` with raw statement, IDs,
dashboard/applicable/policy bindings, orchestrator assessment ref/digest and
collector-owned `agent_session_evidence` XML schema 1 ref/digest. The XML must
bind typed run/agent-run/handoff/agent identity, terminal runtime parentage and
locator, every completeness dimension and gap, pointer-only snapshot/security,
verified canonical integrity, correlated completion and exact evidence-first
collector-only policy. It does not review guides, observe
runtime, ask the human, create per-test evidence, write, attest, approve gates
or promote anything. It returns closed `manual_qa_attestation_review` v1 with
the five signals, `approve|reject`, rationale, confidence, completion and
destinations. The terminal journal is overwritten as the first terminal write,
then assessment and review are published before any attestation; rejected
reviews remain journaled and never create attestation bytes. The
semantic phrase corpus is formal-audit material for the LLM policy, never an
executable regex/whitelist classifier. Only exact assessment/review equality
with independent decision `approve` creates the canonical attestation, which
binds review ref/digest. Rejection commits a correlated current view with the
assessment, review, interaction and pending result, and a later declaration starts a
new terminal batch whose predecessor is that rejected transaction.

Report identity material is immutable. The only issue transition is open to
resolved with an externally produced resolution ref/exact-byte digest, resolved timestamp, and
revalidation refs/digests equal to the new terminal technical projection.
Resolution is input evidence, never an internal target or write.
Resolution invalidates prior catalog/dashboard/result/consistency and requires
complete re-enumeration, proposals and presentation before attestation.

## Managed-state transaction and restricted terminal promotion

The recoverable journal is the first manual-QA write, before any proposal,
catalog, dashboard, interaction, assessment, attestation, report, manual
result/consistency, gate or canonical write. Derive the complete unique target
set and pre-write digests first. Before each target publication, persist its
intended digest; after writing, verify exact bytes and advance the cursor and
phase in the journal.

Use exactly one current journal file, overwritten first for each of four
closed batches. Derive its `target_refs` from the requested transition:

- initial publication: proposals in candidate order, source catalog, manual
  dashboard, immutable dashboard presentation, interaction, manual result;
- issue transition: report, interaction, manual result; an external resolution
  is validated by ref/digest but is not in `target_refs`;
- terminal rejection: semantic assessment, independent attestation review,
  interaction and manual result;
- terminal attestation/promotion: semantic assessment, independent attestation
  review, attestation,
  human-validation gates in
  handoff order, canonical whole `tasks.md`, implementation result,
  implementation dashboard, implementation consistency, proposals in candidate order,
  source catalog, manual dashboard, interaction, manual
  result, manual consistency.

The terminal batch rebuilds the dependent manual views after canonical
promotion so their implementation digests are final. Task and AC refs are
coverage inputs, never write targets. Omission of any applicable class,
addition, duplication or reordering blocks before any target write.
`before_digests` and
`intended_after_digests` have exactly this cardinality/order; published and
residue refs are order-preserving subsets of it.

```yaml
manual_qa_transaction:
  schema_version: 1
  transaction_id: "manual-qa-transaction-v1:<sha256(run_id, execution_id, batch_kind, transition_intent_digest, predecessor_transaction_id)>"
  run_id: "loki-run-v2:<64 lowercase hex>"
  execution_id: "loki-execution-v2:<64 lowercase hex>"
  batch_kind: "initial | issue | terminal-reject | terminal"
  transition_intent_digest: "sha256:<immutable batch kind and exact target refs>"
  predecessor_transaction_id: "prior committed batch identity; null only for initial"
  predecessor_transaction_digest: "sha256:<exact prior journal bytes>; null only for initial"
  phase: "journal-created | manual-publishing | assessment-published | review-published | attested | gates-promoted | canonical-promoted | consistency-published | committed | recovery-required"
  next_target_index: 0
  owner: "loki-manual-qa-orchestrator"
  target_refs: ["exact ordered manual outputs, human gates, state, result, dashboard, consistency"]
  before_digests: ["sha256:<exact pre-write bytes/canonical fragment>"]
  intended_after_digests: ["sha256:<validated intended bytes/canonical fragment>"]
  published_refs: ["ordered refs already written"]
  published_digests: ["sha256:<exact current bytes>"]
  residue_refs: ["written refs not yet reconciled"]
  residue_digests: ["sha256:<exact current bytes>"]
  attestation_ref: "exact handoff v2 anchor after attestation, otherwise null"
  attestation_digest: "sha256:<exact attestation bytes> after attestation, otherwise null"
  transaction_digest: "sha256:<canonical record excluding transaction_digest>"
```

The closed batch/phase boundaries are:

| Batch | Phase | Required cursor boundary |
| --- | --- | --- |
| initial | journal-created | `0` |
| initial | manual-publishing | exact published prefix |
| initial | committed | all initial targets |
| issue | journal-created | `0` |
| issue | manual-publishing | exact published prefix |
| issue | committed | report, interaction and result all published |
| terminal-reject | journal-created | `0` |
| terminal-reject | assessment-published | `1` |
| terminal-reject | review-published | `2` |
| terminal-reject | committed | assessment, review, interaction and pending result all published |
| terminal | journal-created | `0` |
| terminal | assessment-published | `1` |
| terminal | review-published | `2` |
| terminal | attested | `3` |
| terminal | gates-promoted | assessment, review, attestation and all human gates |
| terminal | canonical-promoted | whole canonical batch through implementation consistency |
| terminal | consistency-published or committed | every terminal target |

Every issue, terminal-reject or terminal overwrite records the exact predecessor transaction
identity and journal-byte digest before the first new-batch write.
`recovery-required` in any batch preserves the exact published prefix as the
residue prefix with byte-equal digests and resumes only its next target.
If a crash occurs after writing that next target but before advancing the
journal, resume accepts it only when current bytes, persisted intended digest
and freshly rederived digest are exactly equal; it then journals that target as
published/residue and advances the cursor before processing another target.
Any other post-write state is drift and blocks.

The batch identity is stable while its journal bytes advance, but distinct
open/resolved, reject/reject and reject/approve transitions cannot collide
because batch kind, immutable intent and predecessor are identity material.
Manual result,
manual consistency and terminal projections carry only `transaction_ref` and
`transaction_id`; they never embed the mutable journal byte digest. Replay and
Response validate the final exact journal bytes externally after commit. This
current-only identity rule prevents a result/journal digest cycle.

After attestation, promote every eligible pending human-validation gate v2 to
`passed`, preserving its other fields and setting attestation ref/digest. Then
publish the whole `tasks.md` with only LokiRunState v3 promoted, followed by
implementation result v3, dashboard v3 and consistency v2, in that order, from
`awaiting-manual-qa` to `completed`; preserve `manual_qa_handoff`
byte-equivalent. Then rebuild the dependent manual views and publish manual
consistency last.
Only full parity permits `committed` and a completion claim.

Journal and publish `tasks.md` as one whole file with whole-file before,
intended and current digests; never journal a state fragment as the write
target. Task and AC contracts were technically passed upstream: prove their
exact bytes/semantic source digests unchanged,
report them as covered/reconciled, and keep `promoted_task_refs` and
`promoted_acceptance_criterion_refs` empty. Preserve YAML frontmatter, prose,
all non-state sections and task contracts outside the one LokiRunState block
byte-for-byte. Immediately before every target write, compare its current bytes
to the frozen `before_digest`; any concurrent drift blocks publication. After
every write, update phase,
`next_target_index`, published refs/digests and residue. Recovery validates the
exact published prefix and resumes the next index in every legal phase. A failure
does not claim rollback or completion: set `recovery-required`, list exact
residue and next safe idempotent action. Resume rederives the intended bytes
under the pinned current builder, verifies every before/current/intended digest
and persisted prefix, restores attestation correlation after its publication,
and advances the legal assessment, attestation, gate, canonical and consistency
boundaries while writing the actual remaining targets to committed. Every
target boundary, including gates, whole `tasks.md`, implementation consistency
and manual consistency, is resumable; an exact committed replay is a no-op. It
blocks target drift, stale evidence, an unexpected write or arbitrary replay.

## Terminal result and consistency projections

The closed result and consistency records include all common identity/digest
fields from the dashboard/interaction plus these mandatory terminal fields:

```yaml
terminal_manual_qa_projection:
  source_catalog_ref: "<plan>/builds/manual-qa/source-catalog.json"
  source_catalog_digest: "sha256:<exact bytes>"
  transaction_ref: "<plan>/builds/manual-qa/transaction.json"
  transaction_id: "manual-qa-transaction-v1:<stable batch identity>"
  covered_task_refs: []
  covered_acceptance_criterion_refs: []
  covered_gate_refs: []
  covered_changed_surface_refs: []
  promoted_task_refs: []
  promoted_acceptance_criterion_refs: []
  promoted_gate_refs: []
  canonical_asset_refs: ["tasks.md", "implementation result", "implementation dashboard", "implementation consistency"]
  canonical_asset_digests: ["sha256:<exact final bytes>"]
  validator_refs: []
  validator_digests: []
  audit_refs: []
  audit_digests: []
  final_plan_status: "awaiting-manual-qa | completed"
  blockers: []
  resume: "non-empty disk-only resume condition"
```

`manual_qa_result` has exactly the projection keys above plus `schema_version`,
`run_id`, `execution_id`, `status`, `state_ref/digest`, `handoff_ref/digest`,
`dashboard_ref/digest`, `interaction_ref/digest`, `attestation_ref/digest`,
`report_ref/digest`, `applicable_steps_digest`,
`demand_revalidation_digest`, `automatic_gate_refs/digests`,
`reconciled_handoff_ref`, `next_action`, and `result_digest`.
`manual_qa_consistency` has the same projection and common ref/digest keys,
replaces result status/next-action/self-digest with `result_ref`, exact-byte
`result_digest`, and `consistency_digest`, and exists only for completed state.
All slash-pairs mean two distinct required keys; nullable ref/digest pairs are
jointly null or non-null and every ref/digest array has identical order/length.

Before completion, all covered arrays are non-empty and equal catalog coverage,
all promoted arrays are empty and status is not completed. Completed
result/consistency require non-empty exact coverage; empty task/AC promotions;
non-empty promoted human gates equal to covered human gates; exactly four
canonical assets in tasks/result/dashboard/consistency order; non-empty paired
validator and audit refs/digests; final status `completed`; blockers empty;
transaction committed; attestation anchored/digested; and byte-equal handoff.
Every ref array is unique and every ref/digest array is length-paired. Exact-key
schemas in the validator are canonical; no distributed per-test outcomes or
false completed projection is accepted.

## Validators, gates, stops and completion handoff

Run the deterministic validator over closed schemas, containment, exhaustive
coverage, source concreteness, transition pairs, refs/exact bytes, automatic
evidence plus independent `agent_session_evidence` XML, target/commit drift,
transaction phases/residue, promotion parity and fresh replay. Scan every live
`skills/loki-*` bundle except this one and reject legacy `manual_steps`,
`Playtest question`, `pending-human-validation`, or foreign derivation,
presentation, collection, reconciliation or promotion semantics; explicit
prohibitions, rejections and immutable handoffs remain allowed. Human gates are source applicability approval through the
validated proposal contract and the one aggregate statement after dashboard
presentation. Stop on missing input, proposal, ref, permission, validator,
coverage, gate, attestation, transaction phase, byte parity or safe recovery
path; on cancellation persist a stopped resumable current view only.

Every runtime-qa handoff returns its terminal completion record. The command's
own completion record contains status, exact artifacts/files, validators,
human gates, handoffs, transaction phase/residue, covered/promoted refs, risks,
next destination and the direct-write exception/future-writer opportunity.
Formal independent quality approval is external and cannot be self-issued.

Run `python3 scripts/validate-manual-qa-contracts.py --self-test`, then the
upstream implementation validator, Python compilation, forbidden-reference
scan and `git diff --check`. A failed check blocks completion.
