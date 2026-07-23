# loki-deep-analysis — Deep Analysis Report

- Report contract version: 3

## Status

<completed | partial | insufficient | blocked | failed>

## Summary

<Concise evidence-based result, or exact reason the run did not complete.>

## Delivery and artifacts

- Delivery mode: <report-artifact | response-only>
- Canonical report: <exact approved Markdown destination | response-only>
- Report write: <validated | not-written | blocked + reason>
- Interaction-gate record: <exact approved path + status | none>
- Catalog mutation performed: false
- Other artifacts: <exact paths and roles | none>

## Objective, scope and completion

- Objective: <normalized analysis objective>
- Included scope: <paths, surfaces or questions>
- Exclusions and forbidden writes: <explicit boundaries>
- Completion criteria: <observable criteria>
- Terminal reason: <why this status is valid>

## Sources and evidence map

- Analysis input: <text identity or path>
- Sources read: <path + classification + freshness | none + reason>
- Sources not read: <path + reason | none>
- Research gate: <not-needed | skipped-with-reason | performed-with-citations>
- Facts: <statement + evidence reference | none>
- Inferences: <labelled statement + evidence reference | none>
- Hypotheses: <labelled statement + validation need | none>
- Source conflicts: <conflict + affected conclusion | none>
- Evidence gaps: <gap + impact | none>

## Technology and surface discovery

| Technology/domain | Aliases/versions | Surfaces | Confidence | Evidence | Limitations |
| --- | --- | --- | --- | --- | --- |
| <ID> | <values> | <values> | <high/medium/low/unknown> | <refs> | <limits> |

If empty: <no sufficiently supported technology + consequence>.

## Policy and execution controls

- Policy ID: <ID>
- Policy digest: <verified digest>
- Policy source/status: <source + status>
- Maximum investigation rounds: 3
- Maximum delegated investigations per round: 6
- Concurrent handoff limit: 2
- Cost mode: telemetry-only
- Handoff timeout ticks: <observed approved value>
- Persistent catalog limit: 3 (storage and maintenance only)
- Catalog retrieval page size: 20 (not a total limit)
- Minimum candidate floor: 8 (not a stop condition)
- Candidate ceiling: none
- Preparation completion: <semantic-saturation | context-interruption>
- Preparation request-controls digest: <verified digest of the exact mapping>
- Invariants: <no generation/retrieval ceiling, no automatic mutation, cost telemetry-only>

## Immutable preparation core

```yaml
preparation_core:
  schema_version: 3
  locator: "<approved immutable preparation artifact locator>"
  preparation_id: "prep-<64-lowercase-hex>"
  preparation_digest: "sha256:<64-lowercase-hex>"
  input_fingerprint: "sha256:<64-lowercase-hex>"
  status: "<pre-investigation-complete | partial | blocked>"
  validators: ["<sorted unique non-empty name of a preparation check that passed>"]
  catalog_retrieval_state:
    retrieval_pages_read: <non-negative integer>
    retrieval_exhausted: <true | false>
    retrieval_resume_cursor: <non-empty cursor | null>
  generation_state:
    completion_reason: <semantic-saturation | context-interruption>
    semantic_saturation: <true | false>
    resume_cursor: <non-empty cursor | null>
    unexplored_surfaces: [] # populated items are non-empty strings
    explored_surfaces: [] # populated items are non-empty strings
    final_pass_new_distinct_candidates: <0 | null>
    saturation_evidence_refs: [] # sorted unique non-empty strings; non-empty for semantic saturation
  execution_boundary:
    dispatch_authorized: false
    investigation_handoffs_dispatched: 0
    agent_runs_created: 0
    handoffs_created: 0
    web_research_performed: false
    downstream_workflows_invoked: []
    catalog_mutation_applied: false
```

- Core digest verification: <passed | failed + reason>
- Core validator interpretation: <all material outcomes + effect>
- Canonical candidate projection: <the core's ordered candidates,
  selected_for_investigation and planned_investigations, reproduced without
  sorting, filtering, relabelling, reclassification, reidentification or added
  fields>
- Boundary rule: run IDs, timestamps, destination, caller/report identity and
  `generated_in_report` are absent from the core and its candidate identity /
  digest domains.

```yaml
preparation_candidate_projection:
  candidates: []
  selected_for_investigation: []
  planned_investigations: []
```

This payload is copied from the referenced immutable preparation core in its
canonical order. Do not add report/run/destination/timestamp provenance or
recompute a candidate ID, classification, ordering, or digest. If empty, retain
the empty core arrays and state the core's reason. Report inclusion is not
promotion.

## Post-boundary evidence

All items below this heading are observed after preparation. They may reference
a preparation candidate only by its existing `candidate_id`; they do not modify
the immutable core.

## Selective catalog retrieval

- Canonical consumer root: <path>
- Root resolution source: canonical-pwd
- Consumer root source: canonical-pwd
- Derived state root: <consumer-root>/.loki/analytic-inference/v2
- Live serialization/layout: XML v2 (`registry.xml`, `index.xml`, `rev-N.xml`, event `.xml`)
- Catalog state: <absent | empty | no-match | loaded | blocked>
- Registry locator: <relative/root-bound locator | absent>
- Catalog mutation applied: false
- Zero-mutation proof: <validator/evidence that no catalog-owned target changed>

### Indices read

| Technology | Index locator | Entries inspected | Validation | Reason loaded |
| --- | --- | ---: | --- | --- |
| <ID> | <relative locator> | <count> | <status> | <observed match> |

If empty: <empty catalog, uncertain technology or no matching index + reason>.

### Record locators loaded

| Inference ID/revision | Record locator | Index filter facts | Record-only checks | Rerank reason | Result |
| --- | --- | --- | --- | --- | --- |
| <ID/revision> | <validated locator> | <technology/surface/objective/signal> | <version/exclusion/evidence/freshness> | <observable reason> | <selected/rejected> |

If empty: <no record loaded + reason>. Confirm that the whole catalog was not
loaded.

## Candidate pipeline

### Reused catalogued inferences

| ID/revision | Locator | Relevance | Freshness | Evidence | State |
| --- | --- | --- | --- | --- | --- |
| <ID/revision> | <locator> | <reason> | <state> | <refs> | <selected/rejected/not-investigated> |

### Immutable preparation candidate projection

The table below is a human-readable view derived from the canonical YAML
payload above. It displays a column subset, preserves row order and every
displayed value, and does not treat omitted columns as absent fields. It is not
a second normative projection or schema and must not be used for machine
interpretation.

| Candidate ID | Origin | Summary | Support evidence | Confirm/reject evidence | Stop condition | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| <existing content-addressed ID> | <catalogued/generated> | <core summary> | <core support refs> | <core confirm/reject refs> | <core condition> | <core disposition> |

### Duplicate relations

Exact duplicates remain represented as rejected candidates and are never
merged or removed; near duplicates remain distinct proposals.

| Candidate | Match | Kind | Deterministic/proposal result | Provenance preserved |
| --- | --- | --- | --- | --- |
| <ID> | <other ID> | <exact/near-duplicate> | <represented-and-rejected/review-proposed> | <yes + refs> |

### Rejected candidates

| Candidate | Origin | Reason | Evidence | Reconsideration condition |
| --- | --- | --- | --- | --- |
| <ID> | <catalogued/generated> | <typed reason> | <refs> | <condition/none> |

### Selected, investigated and validated states

| Candidate | Origin | Selected | Investigated | Validated | Material finding | Task helped | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <ID> | <catalogued/generated> | <yes/no> | <yes/no> | <yes/no> | <yes/no> | <yes/no> | <refs> |

Each state is independent. If a category is empty, state the evidence or
utility reason; never pad the preparation floor or truncate at a page boundary.

## Adaptive investigation rounds and specialist coverage

```yaml
investigation_round_ledger:
  schema_version: 1 # exact JSON integer
  preparation_binding:
    preparation_id: "prep-<64-lowercase-hex>"
    preparation_digest: "sha256:<64-lowercase-hex>"
    candidate_ids: []
  candidate_universe: []
  initial_classification:
    selected_candidate_ids: []
    useful_candidate_ids: []
    decisions: {}
  initial_useful_investigations: []
  policy:
    max_rounds: 3 # exact JSON integer
    max_delegated_per_round: 6 # exact JSON integer
    concurrent_handoff_limit: 2 # exact JSON integer
    cost_mode: telemetry-only
  rounds:
    - round: <exact JSON integer 1 | 2 | 3>
      status: terminal
      delegated_investigations:
        - candidate_id: <candidate ID from prior useful set>
          owner: <non-empty owner/capability>
          material_question: <non-empty question>
          reinvestigation_rationale: <non-empty material rationale | null on first investigation>
          subwave: <positive exact JSON integer>
          handoff_id: "handoff-<unique suffix>"
          agent_run_id: "agent-run-<unique suffix>"
          evidence_id: "evidence-<unique suffix>"
          cost: <finite real number >= 0 | unknown | unsupported>
          terminal_state: <completed | partial | blocked | failed | unavailable | unsupported>
      local_resolutions: []
      terminal_barrier: []
      reclassification:
        all_candidate_ids: []
        useful_next_round: [] # preparation-selected actionable candidates only
        decisions: {}
  analysis_terminal_reason: <round-limit-reached | no-useful-investigation | analysis-sufficient>
  downstream_handoff:
    analysis_phase_complete: true
    auto_invoked: false
    allowed_destinations: ["<at least one sorted unique permitted destination>"]
    minimum_next_path: <non-empty action>
```

Keep `candidate_universe` equal to every candidate in the validated immutable
preparation core, including rejected and deferred candidates. Admit round-one
local or delegated work only from `initial_useful_investigations`: the ordered
subset of the core's exact `selected_for_investigation` list retained by the
observable decision recorded for every selected candidate in
`initial_classification.decisions`. Rejected and deferred candidates remain
available for full-universe reclassification but cannot enter round-one work.
Every round decision map still covers the complete universe, but
`useful_next_round` never contains a rejected or deferred candidate. New
evidence may be recorded as an observation for those candidates; operational
promotion requires a newly versioned preparation artifact that includes the
candidate in `selected_for_investigation`. Do not emit a round whose delegated
and local action arrays are both empty; terminate before materializing it.
Resolve each candidate locally at most once. A later local-to-delegated change
uses the delegated record's non-empty `reinvestigation_rationale`; a
delegated-to-local change is supported by the preceding full-universe decision
and useful set. Cost accepts only a finite real number at least zero, `unknown`,
or `unsupported`; booleans, NaN, infinities and other strings are invalid.

For each round, record disjoint delegated investigations and local resolutions,
subwaves, terminal barrier, all-candidate reclassification, useful next-round
candidates, per-candidate decisions, reinvestigation rationale and fresh IDs.
Every action after round one must come from the prior useful-next-round set.
The downstream handoff lists at least one sorted unique permitted destination.
All structural integer fields reject booleans, floats and numeric strings;
downstream flags are exact JSON booleans. Cost retains its separate finite
integer-or-float telemetry rule.

| Handoff ID | Agent-run ID | Evidence ID | Inference | Owner/capability | Selection reason | Dependencies | Terminal state | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <typed IDs> | <typed ID> | <typed ID> | <ID> | <observed match> | <reason> | <depends_on_handoff_id/none> | <status> | <summary> |

- Persistent specialist gaps: <capability + effect | none>
- Temporary-agent use: <observed adapter support + read-only/proposal-only mode | none>
- Non-terminal or degraded handoffs: <status + reason + minimum next path | none>
- Round validation: <max 3, capacity 6, concurrency 2, barrier, reclassification, early stop>
- Round validator invocation: `validate-investigation-rounds.py <ledger> --preparation <validated-preparation-v3>`
- Preparation authority source: <separate immutable preparation artifact path; never ledger snapshot>
- Serialized consolidation/shared writes: <owner + result>

## Findings

### Material findings

<Finding + fact/inference/hypothesis label + evidence + impact | none + reason>

### Negative findings

<Investigated possibility + observable negative result + evidence | none>

### Conflicts and unresolved hypotheses

<Conflict/hypothesis + affected conclusion + required resolution | none>

## Costs, liveness and stopping

| Investigation/handoff | Context cost | Tool cost | Cost evidence | Telemetry effect | Liveness/timeout result |
| --- | --- | --- | --- | --- | --- |
| <ID> | <observed/unknown/unsupported> | <observed/unknown/unsupported> | <source> | telemetry-only | <terminal/partial/unavailable/unsupported + reason> |

- Cost-based admission or deferral performed: false
- Unknown costs treated as zero: false
- Stop/degradation decisions: <decision + observable trigger>

## Structured inference events

```yaml
inference_events:
  - schema_version: 1
    event_id: "<stable idempotency key>"
    source:
      analysis_ref: "<report identity or destination>"
      run_id: "<observed or unavailable>"
      handoff_id: "<observed or unavailable>"
      evidence_refs: []
    inference_id: "<catalog or generated candidate ID>"
    inference_revision: 1
    stage: "<selected | investigated | validated | rejected | material-finding | task-helped | false-positive | repeated-evidence | stale>"
    outcome: "<typed observed outcome>"
    reason: "<non-empty observable summary>"
    agent_capability: "<observed capability | unavailable>"
    cost:
      context: "<observed | unknown | unsupported>"
      tools: "<observed | unknown | unsupported>"
```

If empty: `inference_events: []` plus <reason>. Events are immutable,
idempotent and stage-independent; they authorize no catalog write.

## Execution evidence

| Agent-run/evidence ID | Overall | Transcript | Tool I/O | Errors | Reasoning summary | Token usage | Locator/integrity | Missing reasons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <typed IDs> | <complete/partial/pointer-only/unavailable/unsupported> | <state> | <state> | <state> | <state> | <state> | <typed locator + verified/unverified/mismatch/unavailable> | <reason per non-complete dimension> |

Every overall and per-dimension `<state>` is exactly `complete`, `partial`,
`pointer-only`, `unavailable`, or `unsupported`; explain every non-complete
dimension.

- Sanitization: <performed + result | unavailable + reason>
- Raw payload/transcript persisted: false
- Private/full chain-of-thought included: false
- Fabricated identity, locator or usage: false
- Retrospective fallback used: false

## Validators, gates and approvals

| Validator/gate/approval | Status | Evidence/source | Effect |
| --- | --- | --- | --- |
| <name> | <passed/failed/pending/unavailable/unsupported/not-applicable> | <ref> | <completion effect> |

- Failed or inconclusive material validators: <items | none>
- Pending material handoffs/gates/approvals: <items | none>
- Report target/write-set verification: <result>
- Catalog mutation verification: <no catalog-owned change + evidence>

## Human-validation status

- Gate: `<human_validation_gate>`
- Required: <true | false>
- State: <deferred | passed | failed | not-applicable>
- Source: <observable gate source | unavailable>
- Evidence refs: <refs | none>
- Reason: <non-empty reason for the state>
- Minimum next path: <exact next evidence/action | none>
- Runtime/integration/persisted consumer behavior claimed validated: false
- Completion rule: <required gate passed | gate not required with reason | unresolved and report degraded/blocked>

## Limitations, blockers and risks

- Limitations: <evidence or capability limits | none>
- Blockers: <blocker + owner + exact resume condition | none>
- Residual risks: <risk + mitigation/owner | none>
- Unsupported or unavailable capabilities: <capability + reason | none>

## Allowed downstream routing

| Destination | Allowed | Reason | Required input/gate | Expected owner |
| --- | --- | --- | --- | --- |
| loki-continuous-improvement | <yes/no> | <evaluate events/candidates; never automatic promotion> | <report refs + gates> | <owner> |
| loki-human-decision-preflight | <yes/no> | <material unresolved decisions> | <decision evidence> | <owner> |
| loki-implement-feature | <yes/no> | <demand and Markdown analysis are decision-complete> | <approved report/decisions + readable analysis locator> | <owner> |
| further bounded investigation | <yes/no> | <insufficient evidence> | <minimum source/capability> | <owner> |

Do not auto-invoke a downstream workflow from this response.

## Next steps

1. <Concrete next action, owner, input and gate.>
2. <Additional action or none.>

## Resume state

```yaml
deep_analysis_resume_state:
  report_contract_version: 3
  status: "<completed | partial | insufficient | blocked | failed>"
  delivery_mode: "<report-artifact | response-only>"
  report_destination: "<exact path | null>"
  objective: "<normalized objective>"
  source_refs: []
  policy_id: "<ID>"
  policy_digest: "<digest>"
  preparation_core:
    schema_version: 3
    locator: "<approved immutable preparation artifact locator>"
    preparation_id: "prep-<64-lowercase-hex>"
    preparation_digest: "sha256:<64-lowercase-hex>"
    input_fingerprint: "sha256:<64-lowercase-hex>"
    status: "<pre-investigation-complete | partial | blocked>"
    validators: ["<sorted unique non-empty name of a preparation check that passed>"]
    catalog_retrieval_state:
      retrieval_pages_read: <non-negative integer>
      retrieval_exhausted: <true | false>
      retrieval_resume_cursor: <non-empty cursor | null>
    generation_state:
      completion_reason: <semantic-saturation | context-interruption>
      semantic_saturation: <true | false>
      resume_cursor: <non-empty cursor | null>
      unexplored_surfaces: [] # populated items are non-empty strings
      explored_surfaces: [] # populated items are non-empty strings
      final_pass_new_distinct_candidates: <0 | null>
      saturation_evidence_refs: [] # populated items are non-empty strings
    execution_boundary:
      dispatch_authorized: false
      investigation_handoffs_dispatched: 0
      agent_runs_created: 0
      handoffs_created: 0
      web_research_performed: false
      downstream_workflows_invoked: []
      catalog_mutation_applied: false
  request_controls:
    candidate_ceiling: null
    catalog_retrieval_page_size: 20
    minimum_candidate_floor: 8
  request_controls_digest: "<sha256 digest of the exact request_controls mapping>"
  completed_stages: []
  investigation_round_ledger:
    preparation_id: "prep-<64-lowercase-hex>"
    preparation_digest: "sha256:<64-lowercase-hex>"
    candidate_universe: []
    initial_selected_candidate_ids: []
    initial_matching_decisions: {}
    initial_useful_investigations: []
    rounds_completed: "<0 | 1 | 2 | 3>"
    terminal_reason: "<round-limit-reached | no-useful-investigation | analysis-sufficient>"
    last_terminal_barrier: []
    last_reclassification_digest: "<sha256 digest | unknown>"
  loaded_locators: []
  candidate_decisions: []
  terminal_handoffs: []
  evidence_states: []
  observed_cost:
    used: "<value | unknown | unsupported>"
    mode: telemetry-only
  validator_outcomes: []
  gate_outcomes: []
  approval_outcomes: []
  human_validation:
    gate: "<human_validation_gate>"
    required: "<true | false>"
    state: "<deferred | passed | failed | not-applicable>"
    source: "<observable source | unavailable>"
    evidence_refs: []
    reason: "<non-empty reason>"
    minimum_next_path: "<exact next evidence/action | none>"
  blockers: []
  next_destination: "<allowed destination | none>"
  minimum_next_path: "<exact next input/action | none>"
```
