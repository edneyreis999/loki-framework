---
doc_id: "loki-implement-feature-response-template"
version: "1.0.0"
status: active
last_updated: "2026-07-22"
scope: "Complete recoverable Markdown skeleton for the loki-implement-feature terminal response"
not_scope: "Execution authority, evidence creation, validator decisions, or status derivation"
authority: "skills/loki-implement-feature/references/response.md and the validated persisted execution result"
canonical_source: "skills/loki-implement-feature/assets/response-template.md"
intended_llm_task: "generation"
source_priority:
  - "validated persisted LokiRunState and implement_feature_execution_result"
  - "skills/loki-implement-feature/references/response.md"
  - "this output skeleton"
confidence: high
known_conflicts: []
replaced_by: null
---

# Feature implementation dashboard

## Status

- Status: `<completed | completed-with-limitations | pending-human-validation | partial | blocked | failed | cancelled | needs-human-review>`
- Terminal reason: `<state-and-evidence-derived reason>`
- Run ID: `<typed run ID | unavailable + reason>`
- Execution ID: `<typed execution ID>`
- State: `<locator + sha256 digest>`

## Executive summary

`<What was implemented, what remains, and why the status is truthful.>`

## Implementation units

| Unit | Status | Persisted status source | Dependencies | Owner | Changed targets | Completion evidence | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<task ref>` | `<completed/skipped-dependency/unresolved/cancelled/pending>` | `<task_validation locator + persisted status>` | `<refs or none>` | `<owner>` | `<paths or none>` | `<locators or unavailable + reason>` | `<action or none>` |
| `<blocked-scope:current_task/current_phase/plan_directory ref, only when LokiRunState.status=blocked>` | `<blocked>` | `<state locator + state_digest + selected scope field>` | `<refs or none>` | `<orchestrator>` | `<paths or none>` | `<non-empty state blockers>` | `<non-empty state next_action>` |

Omit the blocked-scope row unless validated LokiRunState status is `blocked`.
Never relabel a task row as blocked or invent a task status.

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

## Validation cycles, severity, and retries

| Task/finding | Classification | Severity | Retry consumed | Retest | Result/evidence |
| --- | --- | --- | --- | --- | --- |
| `<refs>` | `<introduced/regression/pre-existing/unknown/soft-fail>` | `<minor/medium/major/not-applicable>` | `<yes/no + budget state>` | `<locator or none>` | `<result + locator>` |

- Exhausted retries: `<finding/task refs or none + reason>`
- Failed tasks: `<refs or none + reason>`
- Skipped dependents: `<task + failed ancestor refs or none + reason>`
- Final regressions: `<refs or none + reason>`

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

## Manual test

- Status: `<steps | none>`
- None reason: `<non-empty surface-specific reason when status=none | not-applicable because steps exist>`

### Step 1

```yaml
manual_step:
  evidence_or_acceptance_criterion_ref: "<non-empty locator>"
  environment: "<non-empty environment>"
  prerequisites: []
  initial_state: "<non-empty observable starting state>"
  action: "<non-empty command or action>"
  expected_observable_result: "<non-empty observable result>"
  success_signals: ["<objective signal>"]
  failure_signals: ["<objective signal>"]
  cleanup_or_restore: "<action or not-needed with reason>"
  automation_limitation: "<limitation or none with reason>"
```

Repeat the complete step block in execution order. Remove Step 1 only when
status is `none` and the required surface-specific reason is present.

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
- Pending human validation: `<gate, observable steps, evidence destination | none + reason>`

## Resume and next steps

- Resume status: `<none | exact resumable status>`
- Resume from: `<state/task/evidence locators or none>`
- Minimum next input or decision: `<one exact item or none>`
- Next owner/destination: `<owner + destination>`
- Next action: `<single concrete action or none because completed>`
