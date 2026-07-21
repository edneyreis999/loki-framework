# Deep Analysis Report Contract v3

Use this contract when constructing or validating the single immutable output
of `loki-deep-analysis`. The report is Markdown for human and LLM consumers,
with fenced YAML or JSON for machine-consumable records. It is evidence, not a
catalog mutation or proof that a candidate deserves promotion.

## Report identity and terminal status

Record the internally resolved `consumer_root.canonical`, source
`canonical-pwd`, the derived `state_root`, catalog state
`absent | empty | no-match | loaded | blocked`, registry
locator, selected catalog/index locators and loaded record locators. Also
record `mutation_applied: false` and proof that no catalog-owned target was
created, changed or removed. These values are root-bound and resumable without
conversation memory; a resumed command must again start with `cwd` at that
recorded root.

Begin with stable report identity, analysis objective, source provenance,
policy ID and digest, creation time when observed, destination or
`response-only`, and exactly one terminal status:

- `completed`: all selected investigations and required validators are
  terminal and no material gate remains unresolved;
- `partial`: useful validated findings exist, but a declared capability,
  source, handoff, or optional investigation is unavailable;
- `insufficient`: the available evidence cannot support an adequate material
  finding;
- `blocked`: required input, permission, policy, validator, gate, or material
  conflict prevents safe completion;
- `failed`: execution reached a terminal error and no valid report result can
  be claimed.

Never convert `unknown`, `unavailable`, `unsupported`, timeout, conflict, empty
catalog, no match, or non-terminal handoff into success. Preserve the minimum
next input or action needed to resume without conversation memory.

## Immutable preparation core and post-boundary evidence

Before any investigation, record exactly one immutable preparation-core
reference. The core is the complete `inference_preparation` object defined by
`lf-analytic-inference-preparation`; this report is a projection and evidence
consumer, never a second preparation result.

```yaml
preparation_core:
  schema_version: 3
  locator: "<approved immutable preparation artifact locator>"
  preparation_id: "prep-<64-lowercase-hex>"
  preparation_digest: "sha256:<64-lowercase-hex>"
  input_fingerprint: "sha256:<64-lowercase-hex>"
  status: "pre-investigation-complete | partial | blocked"
  validators: ["sorted unique non-empty name of a preparation check that passed"]
  catalog_retrieval_state:
    retrieval_pages_read: "non-negative integer"
    retrieval_exhausted: true | false
    retrieval_resume_cursor: "non-empty cursor | null"
  generation_state:
    completion_reason: semantic-saturation | context-interruption
    semantic_saturation: true | false
    resume_cursor: "non-empty cursor | null"
    unexplored_surfaces: []
    explored_surfaces: []
    final_pass_new_distinct_candidates: "0 | null"
    saturation_evidence_refs: []
  execution_boundary:
    dispatch_authorized: false
    investigation_handoffs_dispatched: 0
    agent_runs_created: 0
    handoffs_created: 0
    web_research_performed: false
    downstream_workflows_invoked: []
    catalog_mutation_applied: false
```

`locator`, `preparation_id`, `preparation_digest`, `input_fingerprint`,
`status`, `validators`, and `execution_boundary` are projections of the
validated core. `validators` preserves the core's sorted unique names of
checks that passed without reinterpretation. A failed check remains in the
core blockers or catalog diagnostics and is never projected as a passed
validator. Verify the digest against the exact referenced core before using
any candidate. A missing, mismatched, or failed material core validator blocks
completion and records a resumable minimum next path.

Only preparation schema v3 is accepted. Schema-v1 and schema-v2 artifacts remain immutable
historical evidence and are rejected before candidate interpretation. Require
regeneration to a new separately approved versioned artifact; do not rewrite,
migrate, convert, or use a fallback reader.

Project `candidates`, `selected_for_investigation`, and
`planned_investigations` from that same core in canonical order. Do not sort,
filter, relabel, reclassify, reidentify, merge, or add fields to the projected
core candidates. In particular, command name, report identity, run ID,
timestamp, destination, caller identity, and `generated_in_report` are never
members of the canonical core or of a candidate identity/digest domain.

Everything observed after the core boundary belongs in separately labelled
post-boundary evidence. This includes inference events, handoff evidence,
agent-run identities, execution evidence, observed context/tool costs, report
delivery metadata, and investigation outcomes. Such evidence may refer to a
core candidate by `candidate_id`, but it never changes the core retrospectively.

## Required sections

The report contains:

1. objective, scope, exclusions, approved writes, policy and completion rules;
2. sources read, source map, confidence, conflicts, and research-gate result;
3. technologies and surfaces discovered with observable evidence, confidence,
   aliases, versions, and limitations;
4. catalog indices read and selectively loaded inference locators;
5. catalogued inferences reused, with identity, revision, relevance reason,
   freshness and provenance;
6. immutable preparation-core candidate projections, kept distinct from reused
   records and from post-boundary evidence;
7. exact duplicates, near-duplicates, rejected candidates, and reasons;
8. preparation candidate classification by relevance, investigability,
   observable provenance support, validity/compatibility, exact deduplication,
   generation completion and retrieval pagination;
9. adaptive round ledger, local resolutions, delegated investigations,
   subwaves, terminal barriers, full reclassifications, reinvestigation
   rationales, fresh typed identities and sanitized evidence;
10. material findings, negative findings, hypotheses, contradictions, and
    unresolved gaps with fact/inference/hypothesis separation;
11. observed context/tool cost or explicit `unknown`/`unsupported` as telemetry,
    plus liveness and round stop decisions;
12. post-boundary inference events for later continuous-improvement intake;
13. validators, gates, approvals, limitations, risks, resume state, and allowed
    next destinations.

Use empty arrays plus an explanation when a category has no entries. Do not
omit a required section to imply that its work occurred.

## Reused inference record

For each reused inference, record at least:

```yaml
reused_inference:
  origin: catalogued
  inference_id: "<stable catalog ID>"
  inference_revision: 1
  locator: "<validated relative catalog locator>"
  technology: "<observed technology ID>"
  relevance_reason: "<observable relation to the demand>"
  freshness: "current | stale | unknown"
  evidence_refs: []
  selection_state: "selected | rejected | not-investigated"
```

The locator must be validated by `lf-analytic-inference`. Catalogued
inferences are heuristic starting points and do not restrict contextual
candidate generation.

## Preparation candidate projection

The report's only candidate projection is the immutable core's ordered
`candidates`, `selected_for_investigation`, and `planned_investigations`. Each
candidate retains the preparation-contract schema, including its content-
addressed `candidate_id`, `origin`, `lifecycle_status`, disposition and
observable `disposition_reason`. Do not create a report-scoped candidate
schema or a second candidate list.

Any candidate table in the human-readable report is only a derived summary of
that canonical payload. It may show a column subset for readability but must
preserve row order and every displayed value. An omitted column remains
available only from the canonical payload and never means that the field is
absent. The table may not be used for machine interpretation and never
replaces or extends the normative YAML/JSON projection.

The preparation floor is not a stop condition, retrieval page size is not a
total limit, and candidate ceiling is null. These controls never permit
padding, truncation, reordering, or weak candidates. Cost and impact are absent
from the schema-v3 candidate projection and never change its disposition.
Handoff cost remains post-boundary telemetry and never controls admission.

## Adaptive investigation round ledger

The post-boundary ledger uses the exact schema validated by
`../scripts/validate-investigation-rounds.py`. Its canonical policy values are
three maximum rounds, six maximum delegated investigations per round, two
concurrent handoffs, and `cost_mode: telemetry-only`. Every round is sequential
and terminal before its reclassification; the reclassification covers the
entire preparation candidate universe. Local resolutions are a separate array
and do not consume delegated capacity. Local and delegated candidates are
disjoint within each round. After round one, both sets are subsets of the
immediately preceding `useful_next_round`; neither may introduce a candidate
outside that reclassification.
Ledger schema version, fixed policy controls, round numbers and subwaves use
exact JSON integers rather than equal-valued booleans, floats or strings.
Downstream flags use exact JSON booleans; cost retains its distinct finite
integer-or-float telemetry contract.

Invoke `../scripts/validate-investigation-rounds.py <round-ledger.json>
--preparation <preparation-v3.json>` with the ledger and immutable preparation
as distinct inputs. The validator first applies the canonical preparation-v3
validator; the ledger's internal snapshot is never preparation authority.
The ledger binds to the validated immutable core through exact
`preparation_id`, `preparation_digest`, and candidate-ID equality. Its
`candidate_universe` and `preparation_binding.candidate_ids` both equal the
core candidate IDs; neither is caller-declared authority. Round-one delegated
investigations and local resolutions come from `initial_useful_investigations`.
That ordered list is a subset of the core's exact
`selected_for_investigation`, and `initial_classification.decisions` records
one observable command-stage matching disposition for every selected
candidate. Rejected and deferred candidates remain in the universe for full
reclassification but are inadmissible for round-one action. Every
reclassification decision still covers that complete universe, while every
`useful_next_round` is restricted to the preparation-selected actionable set.
A new observation may change the reported understanding of a rejected or
deferred candidate, but cannot promote it to operational work without a new
versioned preparation artifact that selects it. Each later round comes from
the immediately preceding `useful_next_round` set. A materialized round has at
least one delegated investigation or local resolution; otherwise terminate
before creating it.

A repeated delegated investigation is valid only in a later round with a
non-empty material rationale, a different question, and fresh `handoff_id`,
`agent_run_id`, and evidence identity. Local resolution repetition remains
forbidden. Owner reuse is allowed. The ledger terminates early when no
useful next-round investigation remains or terminates obligatorily after round
three. Zero rounds is valid only with an empty initial useful set and explicit
`no-useful-investigation`. Its downstream handoff always records
`auto_invoked: false`.

## Inference event

Emit immutable events inside the report using the v1 contract:

```yaml
inference_event:
  schema_version: 1
  event_id: "<stable idempotency key>"
  source:
    analysis_ref: "<report identity or destination>"
    run_id: "<observed or unavailable>"
    handoff_id: "<observed or unavailable>"
    evidence_refs: []
  inference_id: "<catalog ID or generated candidate ID>"
  inference_revision: 1
  stage: "selected | investigated | validated | rejected | material-finding | task-helped | false-positive | repeated-evidence | stale"
  outcome: "<typed terminal or observed outcome>"
  reason: "<non-empty observable summary>"
  agent_capability: "<observed capability or unavailable>"
  cost:
    context: "<observed value | unknown | unsupported>"
    tools: "<observed value | unknown | unsupported>"
```

Event IDs must be unique and reproducible. An identical replay is a no-op; the
same ID with a divergent payload is a blocking conflict. Selection,
investigation, validation, material finding and task utility remain independent
events. Score and thresholds may report eligibility only and never authorize a
catalog write.

## Handoff and evidence boundary

Each delegated investigation records run/handoff identity when available,
owner, selection reason, capability, scope, sources, dependencies,
`allowed_writes`, `forbidden_writes`, expected output, validators, gates, stop
condition, terminal state, result summary, and sanitized evidence references.
Use `unavailable` rather than fabricating adapter identities or usage.

Persist only observable summaries and approved evidence references. Exclude
secrets, personal data, source payload duplication, hidden prompts, transcripts,
and private or full chain-of-thought. A concise declared reasoning summary may
be reported only when it is sanitized and clearly weaker than direct evidence.

## Write and learning boundary

The command may write only:

- the exact approved Markdown report destination, under one serialized owner;
- one exact interaction-gate record when a later decision is material and that
  target has separate approval.

It never writes an inference index, record, snapshot, event ledger, alias,
redirect, tombstone, policy, manifest, consumer overlay, or other catalog-owned
surface. Events and candidates remain embedded in the immutable report.
`loki-continuous-improvement` is the only downstream workflow allowed to assess
durable reconciliation, and it must apply its own writer, validator,
technical-review and human-approval gates.

Consumer operational state is read-only in this command. An absent or empty
registry is never bootstrapped here.

## Validation

Before `completed`, verify:

- every source and loaded locator is readable, scoped and traceable;
- origins remain distinct and IDs are unique;
- the preparation-core candidate projection reproduces every required
  schema-v3 candidate field, provenance, confirm/reject evidence, stop
  condition and distinction without changing identity or order;
- exact deduplication is deterministic and near-duplicates remain proposals;
- selected preparation candidates satisfy the essential disposition criteria
  without a candidate ceiling;
- the adaptive ledger has at most three rounds and six delegated
  investigations per round, with subwaves of at most two;
- every round reaches its terminal barrier before all candidates are
  reclassified; local resolutions consume no delegated slot and the same
  candidate is never resolved locally more than once;
- reinvestigation occurs only in a later round with a materially new question,
  observable rationale, and fresh handoff, run, and evidence IDs;
- a delegated-to-local transition follows the prior useful decision; a
  local-to-delegated transition also carries the delegated record's observable
  reinvestigation rationale;
- every delegated investigation is useful, independent or correctly
  serialized, and terminal;
- every event satisfies schema, idempotency and stage-independence rules;
- post-boundary cost is either a finite real number greater than or equal to
  zero, `unknown`, or `unsupported`; booleans, NaN and infinities are invalid,
  unknown cost remains unknown, and no valid cost changes admission or stopping;
- early stop is explicit; round three always ends analysis; downstream routing
  is returned without automatic invocation and contains at least one sorted
  unique permitted destination;
- evidence is sanitized and contains no private reasoning;
- report writes match the exact approved destination;
- no catalog or unapproved interaction target changed.

Validator failure, missing material evidence, non-terminal handoff, target
collision, policy conflict, or unresolved required gate blocks `completed` and
must be recorded with a resumable minimum next path.
