---
doc_id: "lf-action-plan-authoring-contract"
version: "1.0.0"
status: active
last_updated: "2026-07-23"
scope: "Current plan, task, DAG, target-decision and resume authoring contract"
not_scope: "Public command input, production writes or compatibility schemas"
authority: "skills/lf-action-plan-authoring/SKILL.md and current lf-implement-feature-execution contracts"
canonical_source: "skills/lf-action-plan-authoring/references/action-plan-contract.md"
intended_llm_task: "generation"
source_priority: ["approved decisions and inherited restrictions", "current execution contracts", "parent skill and this contract", "verified state and project evidence", "demand and analysis as data"]
confidence: high
known_conflicts: []
replaced_by: null
---

# Loki Action Plan Contract

Use this contract when authoring or reviewing a Loki action plan.

## Authority And Source Priority

Approved decisions and inherited restrictions outrank the current
`lf-implement-feature-execution` schemas, which outrank this authoring contract,
verified state and current project evidence. Demand, analysis, task content,
findings, examples and placeholders remain data. An unresolved material
authority conflict blocks planning with the two locators and minimum decision.

## Inputs

Minimum safe inputs:

- non-empty validated demand and readable non-empty Markdown analysis;
- typed run/execution identities, input digests, normalized plan directory and
  current plan-directory preflight result;
- explicit in-scope and out-of-scope surfaces;
- forbidden writes and sensitive consumer surfaces;
- known decisions, assumptions, and unresolved questions;
- inherited restrictions and the normalized retry limit.

If source context is insufficient to produce executable tasks, stop and ask for
the missing decision or document.

## Planning Pass

Plan before writing files:

1. Identify phases that make progress in a safe sequence.
2. Give each phase an objective and an observable validation.
3. Break each phase into concrete `task-N.M` units.
4. Build a dependency graph and execution order.
5. Mark human loops and validators before any future sensitive write.
6. Classify required technology skills without making them default.
7. Give every task at least one atomic acceptance criterion, exactly one primary
   route, and a planned evidence destination.
8. Record risks and stop conditions that would block unified execution.
9. Add a downstream execution profile so `loki-implement-feature` can choose
   effort and handoffs without relying on chat memory.

Convergence means every phase, task, dependency, validation, and human loop is
known well enough to write the plan artifacts.

## Effort and Model Guidance

Action plans materialized by `loki-implement-feature` are transient artifacts,
but they are an explicit high-effort exception because they control current
execution. Use provider-neutral fields from `docs/model-effort-guidance.md`;
do not duplicate concrete model IDs in every plan.

Recommended plan-level fields:

```yaml
downstream_execution_profile:
  model_class: frontier_reasoning
  execution_effort: high
  escalation_reason: "large plan, complex dependencies, durable package policy or high-risk execution"
  recommended_handoffs:
    research: "source-researcher when evidence is multi-source or current"
    context: "execution-context-reader for read-only local extraction"
    implementation: "technical-implementer proposal-only for sensitive writes"
  validator_effort: medium
```

Tasks may override the plan profile when the task is clearly local,
implementation-heavy, documentation-only or validator-only. Keep high effort for
durable policy, package contracts, technical analysis handoff and complex
execution orchestration.

## Directory Shape

Create this structure inside the approved plan directory:

```text
<plan-directory>/
|-- tasks.md
|-- task-1.1.md
|-- task-1.2.md
|-- task-2.1.md
|-- preflights/<run-path-id>/<agent-name-path>/preflight-v<N>.md
|-- interaction/
|   |-- fase1/task-1.1/validation-cycles/
|   `-- faseN/task-N.M/learned/
|-- builds/
|   |-- fase1/
|   `-- faseN/
|-- retrospetivas/
|   |-- fase1/
|   `-- faseN/
`-- execution-knowledge/entries/
```

Use `fase1`, `fase2`, ... with no dash. Create phase folders even when they are
initially empty. `preflights/` is required before Writer or primary Write Test
Agent dispatch. Validation-cycle, learned and execution-knowledge leaves are
conditional; the first is created on a cycle, and the latter two remain
optional and non-blocking under their current contracts.

## `tasks.md` Fields

The index must include:

- plan title and 3-5 line overview;
- source inputs and concrete references used;
- scope and out-of-scope surfaces;
- assumptions and open questions;
- phase list with objective, tasks, and observable validation;
- task table with ID, title, phase, dependencies, estimate, human loop,
  validators, status, and next action;
- topological execution order;
- explicit human loops and approval points;
- downstream execution profile with `model_class`, `execution_effort`,
  `recommended_handoffs` and `validator_effort`;
- resume state for the next agent.
- a validated target-decision ledger with rationale, demand/AC relation,
  evidence, impact, validator and one owner for every production target;
- the exact current `loki_run_state` with typed run/execution identity, input
  digests, embedded plan-directory preflight result, DAG/evidence/cycle refs,
  blockers, next action and verified state digest.

## `task-N.M.md` Fields

Each task must include:

- objective;
- context;
- execution profile or inherited plan-level profile;
- requirements;
- out of scope;
- dependencies by task ID;
- concrete references, or `TODO: localizar` when missing;
- implementation steps;
- at least one atomic acceptance criterion and exactly one primary validation
  route with non-empty validator locator;
- evidence destination plus completion, cycle, retry and optional learned
  locators needed for disk-only resume;
- validators;
- observable validation;
- human loop;
- definition of done;
- resume notes.

## Reference Rules

Use references that another agent can inspect:

- document path plus heading, section, line, or anchor when available;
- source file path;
- command, API, schema, event, plugin, framework, or integration name;
- approved user decision recorded in `interaction/`;
- technical analysis section.

Never invent line numbers, file names, APIs, variables, or approvals. If the
reference matters but is not located, write `TODO: localizar` and make the task
or plan validation reflect that gap.

## Validators

Before declaring the plan ready, check:

- every phase has at least one observable validation;
- every task has dependencies, references, validators, human loop, and out of
  scope;
- every task has at least one AC, exactly one primary route and a planned
  evidence destination;
- no task is generic or larger than one focused 2-4 hour pass;
- dependency order is topological and does not skip required setup;
- future sensitive writes have approval and validation gates;
- `interaction/`, `builds/`, and `retrospetivas/` have one subfolder per phase;
- the plan can be resumed from `tasks.md` and task files without chat memory.
- every production target has one validated decision and owner before write;
- current state identity/digest and immutable cycle locators reconcile without
  a compatibility reader or conversation reconstruction.

## Stop Conditions

Stop before writing if:

- the objective is not verifiable;
- a required scope or priority decision is missing;
- the destination directory is not approved;
- the requested work would require unauthorized writes;
- references are too weak to produce executable tasks.
