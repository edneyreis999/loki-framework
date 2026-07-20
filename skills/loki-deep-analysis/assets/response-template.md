# loki-deep-analysis — Deep Analysis Report

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
- Fan-out limit: <observed approved value>
- Cost budget: <observed approved value>
- Handoff timeout ticks: <observed approved value>
- Requested catalogued floor: <integer + source + authorization + digest | not-configured>
- Requested generated floor: <integer + source + authorization + digest | not-configured>
- Invariants: <eligibility-only, no automatic mutation, other enforced limits>

## Selective catalog retrieval

- Canonical consumer root: <path>
- Root resolution source: canonical-pwd
- Consumer root source: canonical-pwd
- Derived state root: <consumer-root>/.loki/analytic-inference/v2
- Live serialization/layout: XML v2 (`registry.xml`, `index.xml`, `rev-N.xml`, event `.xml`)
- Catalog state: <absent | empty | loaded | blocked>
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
| <ID/revision> | <validated locator> | <technology/surface/objective/signal> | <version/exclusion/evidence/freshness/risk/cost> | <observable reason> | <selected/rejected> |

If empty: <no record loaded + reason>. Confirm that the whole catalog was not
loaded.

## Candidate pipeline

### Reused catalogued inferences

| ID/revision | Locator | Relevance | Freshness | Evidence | State |
| --- | --- | --- | --- | --- | --- |
| <ID/revision> | <locator> | <reason> | <state> | <refs> | <selected/rejected/not-investigated> |

### Generated inferences

| Candidate ID | Demand relation | Provenance | Confirm/reject evidence | Impact | Cost | Stop condition | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <ID> | <relation> | <refs> | <evidence> | <impact> | <value/unknown/unsupported> | <condition> | <generated/selected/rejected> |

### Deduplicated and near-duplicate candidates

| Candidate | Match | Kind | Deterministic/proposal result | Provenance preserved |
| --- | --- | --- | --- | --- |
| <ID> | <other ID> | <exact/near-duplicate> | <deduplicated/review-proposed> | <yes + refs> |

### Rejected candidates

| Candidate | Origin | Reason | Evidence | Reconsideration condition |
| --- | --- | --- | --- | --- |
| <ID> | <catalogued/generated> | <typed reason> | <refs> | <condition/none> |

### Selected, investigated and validated states

| Candidate | Origin | Selected | Investigated | Validated | Material finding | Task helped | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <ID> | <catalogued/generated> | <yes/no> | <yes/no> | <yes/no> | <yes/no> | <yes/no> | <refs> |

Each state is independent. If a category is empty or below a configured floor,
state the evidence, utility or budget reason; never pad a quota.

## Investigations and specialist coverage

| Handoff ID | Agent-run ID | Evidence ID | Inference | Owner/capability | Selection reason | Dependencies | Terminal state | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <typed IDs> | <typed ID> | <typed ID> | <ID> | <observed match> | <reason> | <depends_on_handoff_id/none> | <status> | <summary> |

- Persistent specialist gaps: <capability + effect | none>
- Temporary-agent use: <observed adapter support + read-only/proposal-only mode | none>
- Non-terminal or degraded handoffs: <status + reason + minimum next path | none>
- Fan-out validation: <independence, disjoint/read-only targets, DAG, limit>
- Serialized consolidation/shared writes: <owner + result>

## Findings

### Material findings

<Finding + fact/inference/hypothesis label + evidence + impact | none + reason>

### Negative findings

<Investigated possibility + observable negative result + evidence | none>

### Conflicts and unresolved hypotheses

<Conflict/hypothesis + affected conclusion + required resolution | none>

## Costs, liveness and stopping

| Investigation/handoff | Context cost | Tool cost | Cost evidence | Cumulative budget | Liveness/timeout result |
| --- | --- | --- | --- | --- | --- |
| <ID> | <observed/unknown/unsupported> | <observed/unknown/unsupported> | <source> | <used/limit> | <terminal/partial/unavailable/unsupported + reason> |

- Deferred before budget overrun: <candidate + reason | none>
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

## Unreviewed generated candidates

```yaml
generated_candidates:
  - schema_version: 1
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
      freshness: "<current | stale | unknown>"
    investigation:
      confirm_or_reject_evidence: []
      potential_impact: "<impact>"
      cost: "<low | medium | high | unknown | unsupported>"
      stop_condition: "<observable condition>"
      suggested_capabilities: []
    distinction:
      exact_duplicate_of: null
      near_duplicates: []
      distinction_reason: "<observable difference or no-match reason>"
    downstream:
      eligible_for_ci_evaluation: true
      durable_mutation_authorized: false
```

If empty: `generated_candidates: []` plus <reason>. Report inclusion is not
promotion.

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
| loki-generate-action-plan | <yes/no> | <analysis sufficiently resolved> | <approved report/decisions> | <owner> |
| further bounded investigation | <yes/no> | <insufficient evidence> | <minimum source/capability> | <owner> |

Do not auto-invoke a downstream workflow from this response.

## Next steps

1. <Concrete next action, owner, input and gate.>
2. <Additional action or none.>

## Resume state

```yaml
deep_analysis_resume_state:
  status: "<completed | partial | insufficient | blocked | failed>"
  delivery_mode: "<report-artifact | response-only>"
  report_destination: "<exact path | null>"
  objective: "<normalized objective>"
  source_refs: []
  policy_id: "<ID>"
  policy_digest: "<digest>"
  request_controls:
    schema_version: 1
    requested_catalogued_floor: "<integer | null>"
    requested_generated_floor: "<integer | null>"
    provenance:
      source: "<source | not-configured>"
    authorization: "<ref | not-configured>"
    digest: "<digest | not-configured>"
  completed_stages: []
  loaded_locators: []
  candidate_decisions: []
  terminal_handoffs: []
  evidence_states: []
  observed_cost:
    used: "<value | unknown | unsupported>"
    budget: "<value>"
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
