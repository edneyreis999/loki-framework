# Loki Action Plan Contract

Use this contract when authoring or reviewing a Loki action plan.

## Inputs

Minimum safe inputs:

- technical analysis, brief, feedback, or approved objective;
- explicit in-scope and out-of-scope surfaces;
- forbidden writes and sensitive consumer surfaces;
- known decisions, assumptions, and unresolved questions;
- destination base directory approved by the user before writes.

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
7. Record risks and stop conditions that would block `loki:run-plan`.

Convergence means every phase, task, dependency, validation, and human loop is
known well enough to write the plan artifacts.

## Directory Shape

Create this structure inside the approved plan directory:

```text
<plan-directory>/
|-- tasks.md
|-- task-1.1.md
|-- task-1.2.md
|-- task-2.1.md
|-- interaction/
|   |-- fase1/
|   `-- faseN/
|-- builds/
|   |-- fase1/
|   `-- faseN/
`-- retrospetivas/
    |-- fase1/
    `-- faseN/
```

Use `fase1`, `fase2`, ... with no dash. Create phase folders even when they are
initially empty.

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
- resume state for the next agent.

## `task-N.M.md` Fields

Each task must include:

- objective;
- context;
- requirements;
- out of scope;
- dependencies by task ID;
- concrete references, or `TODO: localizar` when missing;
- implementation steps;
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
- no task is generic or larger than one focused 2-4 hour pass;
- dependency order is topological and does not skip required setup;
- future sensitive writes have approval and validation gates;
- `interaction/`, `builds/`, and `retrospetivas/` have one subfolder per phase;
- the plan can be resumed from `tasks.md` and task files without chat memory.

## Stop Conditions

Stop before writing if:

- the objective is not verifiable;
- a required scope or priority decision is missing;
- the destination directory is not approved;
- the requested work would require unauthorized writes;
- references are too weak to produce executable tasks.
