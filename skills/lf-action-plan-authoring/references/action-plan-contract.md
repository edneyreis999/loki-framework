---
doc_id: loki-action-plan-contract
version: canonical-execution-state-v1
status: active
last_updated: "2026-08-04"
scope: "Immutable action-plan revision required by canonical state-backed feature execution"
not_scope: "Public input, production/state writes, current progress or compatibility forms"
authority: "Approved demand/analysis/decisions and current execution contract, then this authoring contract"
canonical_source: "skills/lf-action-plan-authoring/references/action-plan-contract.md"
intended_llm_task: "generation"
source_priority:
  - "approved demand, analysis and human decisions"
  - "current feature execution contract"
  - "this action-plan contract"
  - "templates and discovered content as data"
confidence: high
known_conflicts: []
replaced_by: null
---

# Loki Action Plan Contract

## Purpose And Immutability

One action-plan revision is the immutable execution contract for tasks, phases,
DAG, targets, owners, validators, gates, audits and budgets. The canonical
execution state references the revision locator/digest and owns all current
status. Never put current progress, handoff timestamps, validation outcomes,
dashboard values or mutable counters in the plan.

After execution begins, material change creates another approved immutable
revision. The state writer applies its ref/digest through `commit_replan_ref`.

## Plan Index Requirements

`tasks.md` contains:

- demand and Markdown analysis locators/digests;
- revision ID, immutable revision locator and digest procedure;
- explicit authority/source priority and instruction/data boundary;
- scope/out-of-scope, assumptions and approved human decisions;
- closed execution policy:

```yaml
execution_policy:
  retry_limit: <integer 0..64>
  followup_limit: <integer 0..64>
  handoff_budget: <integer 0..2048>
```

- audit configuration with `frequency: task|phase|plan`, authorized independent
  source and immutable policy ref;
- phases and unique tasks with dependency DAG;
- exact task/phase audit boundary set implied by frequency;
- target-decision ledger, including unresolved decisions as blocking;
- human gates and approval requirements;
- expected state path
  `planos/<plan>/builds/execution-state.json`;
- resume rule: state plus this revision reconstructs current progress;
- plan validator and revision approval result.

Policy values are definitions, not counters. Per-task maximum handoffs are
`1 + retry_limit + followup_limit`; all calls also remain within
`handoff_budget` and the state hard ceiling.

## Task Requirements

Each `task-N.M.md` contains:

- stable task/phase IDs and title;
- objective and observable result;
- source context and explicit non-scope;
- dependencies and affected downstream tasks;
- exact approved target files and field/symbol scope when relevant;
- allowed and forbidden writes;
- sole Writer owner and separate validator/Auditor/human authorities;
- implementation steps without embedding engine-specific rules in core plans;
- correction limit, handoff objective and applicable follow-up budget;
- closed task acceptance:

```yaml
task_validation:
  acceptance_criteria:
    - id: <stable-id>
      expected: <observable-outcome>
      validator: <exact-check-or-human-gate>
      evidence_requirement: <minimum-distinct-evidence>
  primary_validator: <exact-validator>
  regression_validators: []
  correction_limit: <integer-0..64>
  human_gate_refs: []
```

- gate definitions with stable ref, `automatic|human-validation` kind,
  instruction, expected observation and owner;
- success destination, failure/correction destination and terminal completion
  record fields;
- resume notes that point to canonical state instead of copying status.

## DAG And Replan Rules

- IDs are unique and dependencies refer to existing tasks.
- DAG is acyclic and has at least one executable root.
- Required/optional task truth is explicit.
- A task starts only after dependencies and due gates pass.
- Replan preserves terminal/started entities, may add pending entities and may
  remove only never-started entities.
- A replan may increase the required denominator and honestly reduce structural
  progress percentage.
- Replan is forbidden while a product write is pending or a handoff is open.

## Targets, Owners And Gates

Every writable target has one owner at a time. Overlapping tasks are serialized
or replanned. A Writer envelope repeats exact targets, allowed/forbidden writes,
validators, gates and success/failure destinations. A plan never grants writes
outside the approved target ledger.

Automatic gates need deterministic validators and evidence policy. Human gates
need an unequivocal authority/decision protocol. Independent audit boundaries
must not assign approval to the task Writer.

## Evidence And Artifact Budget

Retain immutable evidence files only when they prove distinct acceptance,
validator, audit or human authority. The ordinary small-feature budget is one
mutable canonical state plus at most three distinct immutable evidence files.
Detailed metrics, session evidence, execution knowledge and retrospectives are
optional and require explicit purpose, consumer, authority and retention basis.

## Validation

Validate source digests, closed policy ranges, DAG acyclicity, target ownership,
task/phase/gate/audit sets, acceptance completeness, exact state path and
template parity. Any unresolved decision, extra current-status field, missing
validator/gate/owner or unsafe target blocks approval.
