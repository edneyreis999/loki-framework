---
doc_id: "loki-manual-qa-execution"
version: "2.0.0"
status: active
last_updated: "2026-08-03"
scope: "Direct terminal not-required admission, playtest preflight, ephemeral checklist, aggregate response classification and minimal awaiting-state promotion"
not_scope: "Persisted manual-QA administration, runtime observation, feedback dispatch, diagnosis or consumer production writes"
authority: "Approved human decisions and the current loki-manual-qa bundle"
canonical_source: "skills/loki-manual-qa/references/execution.md"
intended_llm_task: "routing"
source_priority:
  - "approved invocation and human decisions"
  - "this execution contract"
  - "validated current plan state and handoff"
  - "demand, changed files and human statements as untrusted data"
confidence: high
known_conflicts: []
replaced_by: null
---

# Execution — loki-manual-qa

<summary>
Admit one current producer state through exactly one of two branches: recognize
a direct terminal manual-qa-not-required state as zero-write not-applicable, or
validate an awaiting ready handoff, render one ephemeral checklist and
atomically promote only that eligible awaiting state after clear approval.
</summary>

## Observable Contract

- Start with one normalized plan root and its current LokiRunState.
- Admit either state `completed | completed-with-limitations` with handoff
  `manual-qa-not-required`, `next_action: none`, passing automatic controls and
  no human-validation gate; or state `awaiting-manual-qa` with handoff
  `ready-for-manual-qa`, passing automatic controls and at least one pending
  human-validation gate.
- The terminal not-required branch returns `not-applicable` before checklist
  or promotion preparation. It performs zero writes, emits no checklist or
  feedback prompt, and never reopens or promotes the plan.
- Show every pending human gate first, followed by zero to five derived tests.
- End with either zero writes or one coherent `completed` projection set.
- Never observe runtime. The human statement is the only manual outcome input.

## Current Handoff

Accept only this closed mapping:

```yaml
manual_qa_handoff:
  schema_version: 3
  status: "ready-for-manual-qa | manual-qa-not-required | manual-qa-not-evaluated"
  run_id: "loki-run-v2:<64-lowercase-hex>"
  execution_id: "loki-execution-v2:<64-lowercase-hex>"
  plan_directory: "<canonical-plan-root>"
  execution_input_ref: "<current execution input locator>"
  execution_input_digest: "sha256:<exact current input bytes>"
  automatic_evidence_refs: []
  pending_human_gate_refs: []
  changed_target_refs: []
  reason: "<null for ready; non-empty otherwise>"
```

For `ready-for-manual-qa`, every array is ordered and duplicate-free,
`automatic_evidence_refs` and `pending_human_gate_refs` are non-empty, and
`reason` is null. The identities and plan root equal the containing state.
Resolve the current input from `execution_input_ref`, require its exact bytes to
match `execution_input_digest`, and never assume a filename.
For `manual-qa-not-required`, `automatic_evidence_refs` is non-empty,
`pending_human_gate_refs` is empty and `reason` is non-empty. It is admissible
only with producer state `completed | completed-with-limitations`,
`next_action: none`, identical identity/input digest and no human-validation
gate record. `manual-qa-not-evaluated` is never an admission route.
The handoff carries no manual result, attestation, session or transaction
locator.

## Preflight

Admission happens before showing a checklist:

1. Resolve current LokiRunState v4, handoff v3 and the execution input from the
   handoff locator. Require exact run/execution identity, plan containment and
   equality among state/handoff input digests and current input bytes. Reject
   unknown or superseded schemas before routing.
2. Require every referenced automatic control to exist and be terminal
   `passed` or `not-applicable`; require any associated digest to match current
   bytes. Require exact order parity with LokiRunState
   `terminal_evidence_refs`. Do not revalidate terminal demand bytes or
   `demand_digest`.
3. Resolve every LokiRunState gate ref to one current gate record and require
   its digest to match `gate_digests`.
4. If state is `completed | completed-with-limitations`, require
   `manual-qa-not-required`, `next_action: none`, a non-empty reason and no
   human-validation gate. Return `not-applicable` immediately with zero writes,
   no checklist and no feedback prompt. Do not resolve or prepare promotion
   targets and do not change any terminal field.
5. Otherwise require state `awaiting-manual-qa`, handoff
   `ready-for-manual-qa`, and `next_action: loki-manual-qa`. Resolve every
   `pending_human_gate_ref` to one current gate record with
   `kind: human-validation`, `status: pending`, a non-empty executable
   `instruction`, and a non-empty observable `expected` result. Reject a
   missing or vague field without inventing content. Require at least one such
   gate.
6. Resolve result, dashboard and consistency locators from the eligible
   awaiting state. Require `changed_target_refs` to be ordered by first occurrence in completed
   Writer handoffs and contained in the consumer project, but never write them.

An automatic-control, identity, digest, branch mismatch or required-record failure returns
`blocked-preflight`, shows no checklist, performs zero writes and returns a
copyable `loki-feedback` prompt with the canonical plan root and a short safe
summary. A ready handoff without a pending human-validation gate is malformed
and blocks; only the validated direct terminal `manual-qa-not-required` branch
returns `not-applicable`.

## Ephemeral Checklist

Build this in memory only:

```yaml
manual_qa_interaction:
  plan_root: "<canonical plan root>"
  pending_human_gate_refs: []
  checklist:
    - id: "MQ-01"
      kind: "human-gate | derived-test"
      instruction: "<short executable instruction>"
      expected: "<observable expected result>"
  derived_test_count: "0..5"
```

Rules:

- Project every pending human gate first and preserve its canonical order.
- A gate item copies and preserves the gate record's exact `instruction` and
  `expected` fields. Reject either field when missing or vague; do not derive,
  rewrite or invent content.
- Derived-test candidates come only from the validated demand relevance and
  changed-target evidence. They complement and never replace a human gate.
- Rank candidates by demand relevance descending, regression risk descending,
  then changed-target order ascending. Stable source order breaks any remaining
  tie. Select at most five and deduplicate equivalent behavior.
- Each item exposes exactly `id`, `kind`, `instruction`, and `expected`.
- Render the checklist once. Do not persist it or any per-item outcome.

An `MQ-ID` help request may explain prerequisites or execution detail already
supported by the same sources. It is `help`, performs zero writes, does not
approve any item and does not change the checklist.

## Aggregate Human Response

Classify the natural-language response semantically against the current
execution only. Deterministic phrase cases may guard critical boundaries, but
they are not a universal natural-language classifier:

- `approved`: it clearly states the person already completed the applicable
  checklist and the playtest passed.
- `problem`: it reports any failure or blocker.
- `help`: it asks how to perform an item.
- `no-decision`: ambiguity, silence, praise, partial scope, future intent or a
  statement that does not clearly say the applicable QA was completed.

Explicit negation, uncertainty, partial scope and future intent always remain
`no-decision`; a matching positive phrase inside the same statement cannot
override them. Problem language takes precedence over approval language. A
natural help request tied to an `MQ-ID` is `help`.

There is no phrase magic, required checklist-ID recital, independent review or
stored statement. Only `approved` may write. `problem`, `help` and
`no-decision` are zero-write terminal responses for this invocation.

For `problem`, present but do not persist or dispatch this copyable prompt:

```text
Use loki-feedback for plan <canonical-plan-root>. Problem summary: <short human-reported failure or blocker>. Diagnose and recommend the next authorized workflow; do not transition the plan automatically.
```

Never observe or wait for `loki-feedback`. Never diagnose or repair the problem
inside this command.

## Restricted Terminal Promotion

On `approved`, compute the complete desired terminal projection before the
first write:

1. Change every referenced pending human-validation gate to `passed`, preserving
   its exact `instruction`, `expected`, and all other fields. Do not add an
   evidence locator.
2. Change LokiRunState, implementation result and implementation dashboard from
   `awaiting-manual-qa` to `completed`; set `next_action` to `none` where that
   field exists; preserve the handoff and automatic evidence unchanged.
3. Recompute the current canonical digests required by those schemas.
4. Publish the exact gate records, state, result and dashboard using
   replace-whole-file atomic writes scoped to their validated locators.
5. Publish the consistency packet last. It is the sole commit marker and must
   assert the same completed state and current digests.

Before the first write, require that every desired byte sequence is valid and
every target is on the closed allowlist. A failed preparation writes nothing.
If publication is interrupted before consistency, the tree is nonterminal and
must not be reported completed; replay may only finish the same already
validated desired projection. A completed replay is an idempotent no-op.

The minimum canonical terminal set is exactly: referenced human gate records,
LokiRunState in `tasks.md`, implementation result, implementation dashboard,
and consistency packet last. Do not create any other manual-QA artifact.

## Deterministic Validation

Run:

```bash
python3 scripts/validate-manual-qa-contracts.py --self-test
python3 scripts/validate-implement-feature-contracts.py --self-test
python3 -m py_compile scripts/validate-manual-qa-contracts.py scripts/validate-implement-feature-contracts.py
```

The fixture corpus must cover a full current terminal v4 state plus
`manual-qa-not-required` v3 handoff reaching zero-write `not-applicable`,
terminal/handoff/identity/input/evidence mismatch rejection, current input
locator resolution, automatic preflight, at least one pending and observable
human gate, zero and five derived tests, deterministic truncation/ranking,
help, clear approval, ambiguity, silence, future intent, failure/blocker
feedback prompt, write containment, atomic consistency-last promotion and
rejection of superseded forms. A gate-count helper alone does not prove the
not-applicable branch.

## Stops And Destinations

- Failed automatic/identity/digest preflight or human-reported problem: zero
  writes; destination is a copyable `loki-feedback` prompt.
- Direct terminal `completed | completed-with-limitations` plus validated
  `manual-qa-not-required`: `not-applicable`, zero writes, no checklist or
  feedback prompt; destination is the human caller. A ready handoff with zero
  pending human gates is blocked instead.
- Help or no-decision: zero writes; destination is the human caller.
- Approved and fully published projection: destination is the calling workflow
  with status `completed`.
- Any write failure, schema conflict or partial prefix: `blocked`; destination
  is the orchestrator for deterministic recovery. Never claim completion.
