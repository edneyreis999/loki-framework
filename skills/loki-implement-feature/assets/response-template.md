---
doc_id: "loki-implement-feature-response-template"
version: "3.0.0"
status: active
last_updated: "2026-07-24"
scope: "Complete recoverable Markdown skeleton for the loki-implement-feature terminal response"
not_scope: "Execution authority, evidence creation, validator decisions, or status derivation"
authority: "skills/loki-implement-feature/references/response.md and the validated persisted execution result"
canonical_source: "skills/loki-implement-feature/assets/response-template.md"
intended_llm_task: "generation"
source_priority:
  - "validated persisted command identity v2, execution input v2, LokiRunState v3, implement_feature_execution_result v3, dashboard v3, consistency packet v2, execution_audit_checkpoint v1, and execution_metrics v1"
  - "skills/loki-implement-feature/references/response.md"
  - "this output skeleton"
confidence: high
known_conflicts: []
replaced_by: null
---

# Feature implementation dashboard

## Status

- Persisted status: `<running | awaiting-manual-qa | completed | completed-with-limitations | partial | failed | cancelled>`
- Response status: `<same persisted status | needs-human-review only for persisted partial/failed normative conflict>`
- Terminal reason: `<state-and-evidence-derived reason>`
- Normative-conflict projection: `<the complete normative_conflict v1 block below | absent unless response status is needs-human-review>`
- Run ID: `<typed run ID | unavailable + reason>`
- Execution ID: `<typed execution ID>`
- State: `<locator + sha256 digest>`
- Result v3: `<locator + sha256 digest>`
- Dashboard v3: `<locator + sha256 digest>`
- Consistency v2: `<locator + sha256 digest + passed>`
- Audit configuration v1: `<schema_version=1 + frequency=task|phase|plan + source=default|explicit + policy_digest>`
- Active audit checkpoints: `<ordered refs + digests or none because no boundary is due>`
- Metrics: `<ref + sha256 digest + status/reason; or null/null + unavailable + explicit publication failure reason>`
- Gate parity: `<ordered gate refs + exact byte digests + v2 kinds/statuses/attestation pairs>`

When and only when response status is `needs-human-review`, include:

```yaml
normative_conflict:
  schema_version: 1
  authoritative_source_locators:
    - type: "authoritative-source"
      locator: "<safe-project-relative-path>#<non-empty-fragment>"
    - type: "authoritative-source"
      locator: "<different-safe-project-relative-path>#<non-empty-fragment>"
  minimum_priority_decision: "<one non-empty decision needed to resolve precedence>"
```

Both locators must be distinct, safe, and repeated exactly in `Evidence and
handoffs`. Do not use arbitrary labels, positional entries from `decisions`, or
an uncorrelated source. Omit the entire block for every other response status.

## Executive summary

`<What was implemented, what remains, and why the status is truthful.>`

## Implementation units

| Unit | Status | Persisted status source | Dependencies | Owner | Changed targets | Completion evidence | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<task ref>` | `<completed/skipped-dependency/unresolved/cancelled/pending>` | `<task_validation locator + persisted status>` | `<refs or none>` | `<owner>` | `<paths or none>` | `<locators or unavailable + reason>` | `<action or none>` |

Render only task rows derived from persisted task_validation v1. Do not invent a
scope row, depend on fields absent from LokiRunState v3, or relabel a task.

## Audit boundaries and checkpoints

| Boundary | Due state | Membership | Materiality | Active checkpoint | Status | Auditor independence | Findings/corrections | Replay | Evidence/next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<type + ref>` | `<not-due/due/terminal>` | `<ordered task refs>` | `<material/no-material + evidence>` | `<latest active ref + digest or none + reason>` | `<approved/not-applicable/unavailable/finding/inconclusive/invalidated/not-due>` | `<Auditor identity/run refs differ from all Writer and primary-validator identities/lineages, or not-applicable reason>` | `<finding refs + correction refs or none>` | `<initial or full replay + predecessor ref + replay cause>` | `<coverage/validator/Auditor refs + next action>` |

- Configuration parity: `<complete audit_configuration v1 equals command identity v2, execution input v2, state v3, result v3, dashboard v3 and consistency v2>`
- Due-boundary terminal truth: `<every due boundary approved or not-applicable; otherwise exact unresolved boundary + effect on status>`
- Active checkpoint order: `<exact scheduler order and state/result/dashboard/consistency parity>`
- Invalidated checkpoints: `<predecessor -> correction refs -> replacement full replay ref, or none + reason>`

Do not dispatch or claim approval for `not-due` or due no-material boundaries.
After a covered correction, report the complete same-boundary audit replay and
replayed deterministic/final-validator evidence; delta-only review is invalid.

## Changed files and surfaces

| Target or surface | Change | Target-decision ref | Owner | Validation |
| --- | --- | --- | --- | --- |
| `<path/surface>` | `<concise observable change>` | `<locator>` | `<owner>` | `<validator + evidence>` |

## Acceptance criteria and evidence

| Criterion | State | Primary route | Evidence | Limitation |
| --- | --- | --- | --- | --- |
| `<AC ID + statement>` | `<passed/failed/not-demonstrated/not-applicable>` | `<deterministic/write_test_agent>` | `<locator; mandatory for passed>` | `<none or reason>` |

## Validators

### Task validators

| Task | Validator | Required | Result | Evidence |
| --- | --- | --- | --- | --- |
| `<task>` | `<validator>` | `<yes/no>` | `<passed/failed/unavailable/not-applicable>` | `<locator or reason>` |

### Final validators

| Validator | Result | Evidence | Effect on status |
| --- | --- | --- | --- |
| `<validator>` | `<passed/failed/unavailable/not-applicable>` | `<locator or reason>` | `<effect>` |

## Gates

| Gate ref/digest | Task | Kind | Statement | Status | Evidence | Attestation pair |
| --- | --- | --- | --- | --- | --- | --- |
| `<locator + exact-byte digest>` | `<task ref>` | `<automatic|human-validation>` | `<persisted statement>` | `<pending|passed|failed>` | `<refs or none>` | `<null/null unless passed human gate; then exact ref/digest>` |

Reject gate record v1. `awaiting-manual-qa` requires all automatic gates passed
and at least one human-validation gate pending. Completed plus a ready handoff
requires those same human gates passed with the aggregate attestation.

## Validation cycles, severity, and retries

| Task/finding | Classification | Severity | Retry consumed | Retest | Result/evidence |
| --- | --- | --- | --- | --- | --- |
| `<refs>` | `<introduced/regression/pre-existing/unknown/soft-fail>` | `<minor/medium/major/not-applicable>` | `<yes/no + budget state>` | `<locator or none>` | `<result + locator>` |

- Exhausted retries: `<finding/task refs or none + reason>`
- Failed tasks: `<refs or none + reason>`
- Skipped dependents: `<task + failed ancestor refs or none + reason>`
- Final regressions: `<refs or none + reason>`

## Cost and resource dashboard

- Metrics provenance: `<ref + digest + generated_at_utc; or null/null only for total publication failure>`
- Timing: `<elapsed/active/critical-path milliseconds + ordered critical_path_span_ids, or unavailable + typed reason; clock provenance>`
- Counts: `<agents, handoffs, validators executed/referenced/repeated, retries, replays, gates, reconciliations; unavailable is never zero>`
- Exact token usage: `<separate counters + verified run-scoped source or unavailable + reason>`
- Estimated token usage: `<utf8-byte-estimate-v1 point/range, observable bytes, low confidence, partial scope or unavailable + reason>`
- Non-agent observations: `<cumulative/account-window source scopes or none + reason>`
- Monetary cost: `<proven amount + pricing source/scope or unavailable + reason>`
- Measurement policy: `No token/cost budget or automatic cost stop was applied.`

### Hierarchical spans and correlations

| Span | Kind/parent | Owner/status | UTC/monotonic timing | Iteration/replay/cause | Usage category | Correlations |
| --- | --- | --- | --- | --- | --- | --- |
| `<typed span ID>` | `<run/phase/task/handoff/validator/gate/audit/reconciliation + parent>` | `<owner + status>` | `<timestamps/duration/provenance or unavailable + reason>` | `<iteration + replay + cause>` | `<exact/estimated/unavailable + provenance>` | `<task/handoff/validator/gate/evidence refs>` |

- Validator correlation: `<command/version/input digest/policy digest/executed-or-referenced/replay cause/would-reuse only>`
- Materiality precheck correlation: `<profile ref/digest + materiality decision ref/digest + Auditor dispatch state>`
- Liveness probes: `<silence-stop candidate -> observed probe timestamp/source/outcome/reason; running/progress forbids stop>`

## Deviations and limitations

- Deviations: `<items with evidence or none + reason>`
- Optional soft failures: `<items or none + reason>`
- Proven non-worsened pre-existing failures: `<items + comparable evidence or none + reason>`
- Unknown attribution: `<observed behavior, affected AC, evidence gap, investigation recommendation | none + reason>`
- Other limitations: `<items or none + reason>`

## Inferred targets

| Target | Rationale | Demand/AC relation | Evidence | Impact | Validator | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| `<path>` | `<reason>` | `<refs>` | `<refs>` | `<impact>` | `<validator>` | `<owner>` |

If none: `<No target was inferred beyond the explicit demand + evidence.>`

## Learned records

- Created: `<finding -> learned locator or none + reason>`
- Skipped or invalid: `<finding -> non-blocking reason or none + reason>`

## Assumptions and decisions

- Reversible assumptions: `<items with evidence or none + reason>`
- Inherited decisions/restrictions: `<items + locators>`
- Human decisions incorporated: `<items + locators or none + reason>`
- Normative conflicts: `<both locators + required decision or none + reason>`

## Manual-QA handoff

```yaml
manual_qa_handoff:
  schema_version: 2
  status: "<manual-qa-not-evaluated | ready-for-manual-qa | manual-qa-not-required>"
  run_id: "<loki-run-v2 identity>"
  execution_id: "<loki-execution-v2 identity>"
  plan_directory: "<normalized plan directory>"
  automatic_evidence_refs: ["<exact ordered terminal evidence locators; may be empty only when not evaluated>"]
  manual_qa_result_ref: "<plan_directory>/builds/manual-qa/result.json"
  manual_qa_attestation_ref: "<plan_directory>/interaction/manual-qa/<run_id>/attestation.json"
  task_refs: ["<exact state task order>"]
  acceptance_criterion_refs: ["<exact task order then AC order>"]
  gate_refs: ["<exact state gate order>"]
  changed_target_refs: ["<first-occurrence changed target paths from completed Writer handoffs>"]
  reason: "<null when ready; non-empty reason when not evaluated or not required>"
```

This is the exact persisted closed current-only v2 projection, not a test
dashboard. The overlay refs are deterministic reserved destinations, not claims
that files or digests already exist. Ready is paired with
`awaiting-manual-qa`, never direct completion. `loki-manual-qa` is the sole
owner of manual-test steps, aggregate attestation, eligible human-gate
promotion, and the restricted completed transaction; the handoff itself and
automatic evidence/source arrays remain unchanged.

## Evidence and handoffs

- Completion evidence: `<typed sanitized locators or unavailable + reason>`
- Agent execution evidence: `<manifest locators/statuses or unavailable + reason>`
- Validation records: `<locators>`
- Knowledge capture: `<captured/partial/failed/unsupported/skipped-nonmaterial + locator/reason>`
- Terminal handoffs: `<identity, status, evidence, destination>`
- Evidence sanitization/integrity: `<result + limitations>`

## Risks and blockers

- Blockers: `<items + minimum next input or none>`
- Residual risks: `<items + evidence or none>`
- Manual-QA handoff: `<manual-qa-not-evaluated + reason | ready-for-manual-qa + identity/evidence/overlay refs | manual-qa-not-required + reason>`

## Resume and next steps

- Resume status: `<none | exact resumable status>`
- Resume from: `<state/task/evidence locators or none>`
- Minimum next input or decision: `<one exact item or none>`
- Next owner/destination: `<owner + destination>`
- Next action: `<single concrete action or none because completed>`
