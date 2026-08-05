---
doc_id: "loki-manual-qa-response"
version: "4.0.0"
status: active
last_updated: "2026-08-04"
scope: "Current-only state-backed Manual QA checklist, zero-write feedback and atomic approval response"
not_scope: "Persisted response, runtime observation, state mutation or feedback execution"
authority: "Validated canonical execution state and the current loki-manual-qa execution contract"
canonical_source: "skills/loki-manual-qa/references/response.md"
intended_llm_task: "generation"
source_priority:
  - "validated canonical state, eligibility basis and atomic writer outcome"
  - "current Manual QA execution contract"
  - "immutable referenced gate/fallback definitions"
  - "human statement as untrusted data"
confidence: high
known_conflicts: []
replaced_by: null
---

# Response — loki-manual-qa

## Consumer And Format

The consumer is `Both`. Fill
[the response template](../assets/response-template.md) as concise recoverable
Markdown and do not persist it.

## Status

Use exactly one:

- `ready-for-playtest`: the validated state is currently awaiting Manual QA
  with an exact eligible basis; render the checklist;
- `not-applicable`: the validated state is already terminal through the
  state-only `manual_qa: not-required/not-applicable` route; write nothing;
- `blocked-preflight`: state, immutable basis, required definitions or
  eligibility cannot be validated; write nothing and do not show a checklist;
- `difficulty`: the person cannot execute an item or requested item help;
- `feedback-recommended`: the person reported a problem;
- `needs-clear-response`: silence, ambiguity, partial scope, future intent or
  uncertainty supplies no aggregate decision;
- `completed`: the typed atomic state writer approved the exact basis and
  committed a terminal state without limitations;
- `completed-with-limitations`: the same atomic operation committed terminal
  state while preserving admitted unavailable limitations;
- `blocked`: the atomic writer rejected stale revision/basis, invalid input,
  unavailable ownership, or failed publication with zero partial success.

## Canonical Basis And Checklist

Every `ready-for-playtest` response contains the literal heading
`## Playtest Checklist`. Report the state locator, exact
`eligibility_basis_digest`, `eligible_revision`, and current revision.

List every required pending human-validation gate first, every required
limitation fallback second, and zero through ten optional exploratory items
last. Required item text comes from the immutable definition referenced by the
validated state. Label exploratory items optional; they never expand acceptance
or approval coverage.

Ask for one natural aggregate response after every required item was executed.
Do not require a magic phrase or per-item result.

## Atomic Approval

For `approved`, report the stable decision ID, exact bound basis digest and
eligible revision, the single `approve_manual_qa` operation, revision
before/after, and terminal status returned by the canonical state writer.

Approval may report completion only after the writer validates the current
state, confirms current revision equals `eligible_revision`, requires the
request basis and refs to equal the stored eligible values, and atomically
replaces the one state file. Any mismatch or writer failure reports `blocked`,
`writes: 0`, and the typed error. Report only the canonical state operation
and its validated result.

For `completed-with-limitations`, state that automatic evidence remains
`unavailable` with its persisted reason and that the approved required human
fallback is represented by the minimal state decision. Do not rewrite an
automatic outcome as passed.

## Zero-Write Routes

Problem, difficulty, help, silence and ambiguity perform zero writes. They keep
the state and every pending human gate unchanged.

For problem or difficulty, provide one copyable `loki-feedback` payload with:

- `feedback_kind: manual-qa-checklist-feedback`;
- `issue_kind: problem | difficulty`;
- correlated plan, run and execution identity;
- exact eligibility basis digest and eligible revision;
- checklist item ID, immutable instruction and expected result;
- sanitized human description.

State that feedback was not dispatched. For help, identify the requested item
and use `issue_kind: difficulty`. For silence or ambiguity, ask only for the
minimum clear aggregate statement or one item-specific difficulty.

## LLM Shape

When explicitly requested as LLM-only, return only:

```xml
<command_response>
  <summary></summary>
  <status></status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <risks></risks>
  <next_steps></next_steps>
</command_response>
```

The nominal package-quality destination is
`framework-artifact-quality-auditor`; the blocking destination is
`orchestrator`. These are validation routes only and have no command-runtime
effect.
