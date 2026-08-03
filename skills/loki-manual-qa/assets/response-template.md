---
doc_id: "loki-manual-qa-response-template"
version: "2.1.0"
status: active
last_updated: "2026-08-03"
scope: "Recoverable complete manual QA, visible administrative degradation and eligible terminal promotion response skeleton"
not_scope: "Execution authority or evidence creation"
authority: "skills/loki-manual-qa/references/response.md"
canonical_source: "skills/loki-manual-qa/assets/response-template.md"
intended_llm_task: "generation"
source_priority: ["validated current views", "response reference", "this template"]
confidence: high
known_conflicts: []
replaced_by: null
---

# Manual QA dashboard

## Status and eligibility

- Status: `<administrative-schema-degraded | in-progress | pending-input | blocked | stopped | completed>`
- Plan / run / execution: `<validated locators and typed IDs>`
- Final plan status: `<awaiting-manual-qa | completed>`
- Handoff v2: `<ref + digest + byte-equal parity>`
- Automatic validators / gates / audits: `<terminal refs, outcomes and digests>`
- Source catalog: `<ref + digest + coverage digest>`
- Transaction: `<initial | issue | terminal-reject | terminal; immutable intent digest + phase + ref/digest + predecessor + exact prefix/residue refs/digests>`
- Dashboard presentation: `<persisted ref + exact digest used by semantic assessment>`
- Independent attestation review: `<ref + exact digest + reviewer/evidence identity + approve|reject>`
- Aggregate attestation: `<ref + exact-byte digest | absent>`
- Blockers: `<none | exact blockers>`
- Resume: `<disk-only condition and next legal action>`

## Administrative admission

`<none | admission ref/digest + administrative-admission phase +
MARKDOWN_CONTRACT_BLOCK_INVALID + source/projection/target/evidence/control/gate
proofs + cross-projection control-set parity + recomputed validator digest +
unchanged-upstream non-Markdown semantic/provenance validation passed +
publication created|recovered|no-op with admission.json.tmp residue absent +
capture status/reason/minimum-next-path + allowed actions + forbidden actions +
non-empty blockers>`

While this section is active, terminal reconciliation below must say
`forbidden-while-degraded`; do not request or record aggregate attestation.

## Source coverage

- Covered tasks: `<refs>`
- Covered acceptance criteria: `<refs>`
- Covered human gates: `<refs>`
- Covered changed surfaces: `<refs>`
- Not applicable: `<source ref + concrete reason for every row>`

## All applicable tests

### MQ-01 — `<concrete title>`

- Origin/order: `<source kind + exact ref + source_order>`
- Environment: `<concrete environment>`
- Prerequisites: `<concrete prerequisites>`
- Start: `<observable initial state>`
- Reproduce: `<complete ordered actions>`
- Expect: `<observable expected result>`
- Success: `<observable signal>`
- Failure: `<observable signal>`
- Cleanup: `<action or explicit not-needed reason>`
- Automation limit: `<material human-observation reason>`

Repeat for every applicable source in deterministic order. There is no response
length cap. Never truncate, paginate, summarize away or hide later tests.

## Terminal reconciliation

- Eligibility: `<eligible | forbidden-while-degraded>`
- Covered/reconciled tasks (bytes unchanged): `<refs>`
- Covered/reconciled acceptance criteria (bytes unchanged): `<refs>`
- Promoted tasks: `none`
- Promoted acceptance criteria: `none`
- Promoted human gates: `<refs | none-before-completion>`
- Canonical assets: `<whole tasks.md/result/dashboard/consistency refs + exact final digests; task/AC unchanged proof>`
- Manual assets: `<catalog/dashboard/semantic assessment/independent review/attestation/interaction/report/result/consistency refs + digests; transaction ref + stable ID + externally checked final journal digest>`
- Validators and audits: `<refs + digests + outcomes>`
- Runtime-QA handoffs: `<terminal completion records>`
- Managed-state completion: `<owner, direct-write exception, checks, gates, residue, future writer opportunity>`

## Next action

`<help for MQ-ID | state naturally that every applicable item was already tested | resolve issue | resume transaction | no-op terminal replay>`

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
