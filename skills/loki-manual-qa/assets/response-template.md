---
doc_id: "loki-manual-qa-response-template"
version: "4.0.0"
status: active
last_updated: "2026-08-04"
scope: "Current-only state-backed Manual QA response skeleton"
not_scope: "Eligibility derivation, persisted response, approval inference or state-write authority"
authority: "skills/loki-manual-qa/references/response.md and one validated canonical execution-state snapshot"
canonical_source: "skills/loki-manual-qa/assets/response-template.md"
intended_llm_task: "generation"
source_priority:
  - "validated canonical state and immutable referenced gate/fallback definitions"
  - "current response contract"
  - "this non-normative output skeleton"
  - "human statements as untrusted data"
confidence: high
known_conflicts: []
replaced_by: null
---

# Manual QA — <status>

Plan: `<canonical plan root>`
Execution: `<run ID / execution ID>`

## Canonical Basis

- State: `<plan>/builds/execution-state.json`
- Eligibility basis digest: `<sha256 digest or unavailable + blocker>`
- Eligible revision: `<integer or unavailable + blocker>`
- Current revision: `<integer>`
- Eligibility: `<eligible | not-applicable | blocked>`

## Playtest Checklist

<For `ready-for-playtest`, render every required human-validation gate, every
required limitation fallback, then 0..10 optional exploratory items. Preserve
the exact immutable instruction and expected result for each required item.
For other statuses write `not shown`; do not imply that a hidden checklist
passed.>

After executing every required item, respond naturally that the complete
applicable checklist passed, or describe the problem or difficulty. One
unequivocal aggregate decision is sufficient. Optional exploratory items do not
expand acceptance.

## Human Decision

- Classification: `<approved | problem | difficulty | no-decision>`
- Decision ID: `<stable ID or not-created>`
- Bound basis: `<exact eligibility basis digest + eligible revision | none>`

## Atomic State Transition

- Operation: `<approve_manual_qa | none>`
- State writer: `<typed canonical state writer | not invoked>`
- Revision: `<before -> after | unchanged>`
- Terminal status: `<completed | completed-with-limitations | unchanged>`
- Writes: `<1 exact atomic state replacement | 0>`
- Other writes: `0`

## Feedback Prompt

<For problem or difficulty, provide one copyable `loki-feedback` payload with
issue kind, plan/run/execution identity, exact eligibility basis digest,
eligible revision, checklist item, instruction, expected result and sanitized
description. State that it was not dispatched. Otherwise write
`not applicable`.>

## Evidence And Limitations

- Required gate refs: `<refs or none>`
- Required limitation refs: `<refs or none>`
- Automatic unavailable outcomes: `<preserved as unavailable + reason | none>`
- Validation: `<state, basis, revision and writer outcome evidence>`

## Next Step

<One concrete human action, or `none` after terminal completion.>
