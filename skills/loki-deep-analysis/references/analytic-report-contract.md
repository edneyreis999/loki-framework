# Deep Analysis Report Contract v1

Use this contract when constructing or validating the single immutable output
of `loki-deep-analysis`. The report is Markdown for human and LLM consumers,
with fenced YAML or JSON for machine-consumable records. It is evidence, not a
catalog mutation or proof that a candidate deserves promotion.

## Report identity and terminal status

Record the internally resolved `consumer_root.canonical`, source
`canonical-pwd`, the derived `state_root`, catalog state
`absent | empty | loaded | blocked`, registry
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
  source, cost, handoff, or optional investigation is unavailable;
- `insufficient`: the available evidence cannot support a material finding or
  the configured relevant-candidate floor;
- `blocked`: required input, permission, policy, validator, gate, or material
  conflict prevents safe completion;
- `failed`: execution reached a terminal error and no valid report result can
  be claimed.

Never convert `unknown`, `unavailable`, `unsupported`, timeout, conflict, empty
catalog, no match, or non-terminal handoff into success. Preserve the minimum
next input or action needed to resume without conversation memory.

## Required sections

The report contains:

1. objective, scope, exclusions, approved writes, policy and completion rules;
2. sources read, source map, confidence, conflicts, and research-gate result;
3. technologies and surfaces discovered with observable evidence, confidence,
   aliases, versions, and limitations;
4. catalog indices read and selectively loaded inference locators;
5. catalogued inferences reused, with identity, revision, relevance reason,
   freshness and provenance;
6. contextual inferences generated in this run, kept distinct from reused
   records;
7. exact duplicates, near-duplicates, rejected candidates, and reasons;
8. candidate classification by relevance, risk, investigation cost,
   independence, evidence availability, and material-finding potential;
9. selected investigations, handoff identities, capabilities, owners, sources,
   limits, stop conditions, validators, terminal states and sanitized evidence;
10. material findings, negative findings, hypotheses, contradictions, and
    unresolved gaps with fact/inference/hypothesis separation;
11. observed context/tool cost or explicit `unknown`/`unsupported`, policy
    budget, degradation and stop decisions;
12. inference events and generated candidates for later continuous-improvement
    intake;
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

## Generated candidate

Every new inference remains an `unreviewed` candidate and contains:

```yaml
generated_candidate:
  schema_version: 1
  candidate_id: "<stable run-scoped ID>"
  origin: generated
  status: unreviewed
  statement: "<testable statement or question>"
  demand_relation: "<observable relation>"
  applicability:
    technologies: []
    versions: []
    surfaces: []
    objectives: []
    signals: []
    exclusions: []
  provenance:
    source_refs: []
    generated_in_report: "<report identity or destination>"
    evidence_refs: []
    freshness: "current | stale | unknown"
  investigation:
    confirm_or_reject_evidence: []
    potential_impact: "<observable impact>"
    cost: "low | medium | high | unknown | unsupported"
    stop_condition: "<observable terminal condition>"
    suggested_capabilities: []
  distinction:
    exact_duplicate_of: null
    near_duplicates: []
    distinction_reason: "<observable difference or no-match reason>"
  downstream:
    eligible_for_ci_evaluation: true
    durable_mutation_authorized: false
```

A configured minimum is a relevance floor, not permission to invent or
delegate weak candidates. If fewer useful candidates exist, report
`insufficient` or `partial` and the stopping evidence.

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
- generated candidates contain provenance, confirm/reject evidence, impact,
  cost, stop condition and distinction;
- exact deduplication is deterministic and near-duplicates remain proposals;
- every selected investigation is useful, independent or correctly serialized,
  policy-budgeted, and terminal;
- every event satisfies schema, idempotency and stage-independence rules;
- unknown cost remains unknown and no quota is padded with irrelevant work;
- evidence is sanitized and contains no private reasoning;
- report writes match the exact approved destination;
- no catalog or unapproved interaction target changed.

Validator failure, missing material evidence, non-terminal handoff, target
collision, policy conflict, or unresolved required gate blocks `completed` and
must be recorded with a resumable minimum next path.
