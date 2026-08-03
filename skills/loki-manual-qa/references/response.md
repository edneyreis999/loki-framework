---
doc_id: "loki-manual-qa-response"
version: "2.1.0"
status: active
last_updated: "2026-08-03"
scope: "Recoverable complete manual QA dashboard, visible administrative degradation and eligible terminal promotion response"
not_scope: "State authority, runtime observation or inferred per-test evidence"
authority: "skills/loki-manual-qa/references/execution.md and validated persisted state"
canonical_source: "skills/loki-manual-qa/references/response.md"
intended_llm_task: "generation"
source_priority: ["validated persisted state", "execution reference", "response template"]
confidence: high
known_conflicts: []
replaced_by: null
---

# loki-manual-qa — Response

## LLM artifact profile and readiness

This `both` artifact has `intended_llm_task: generation`; its primary reader is
the human performing QA and its secondary reader is a resuming orchestrator.
Authority is validated persisted state, required evidence is exact refs/digests,
freshness is current-run only, ambiguity blocks mutation, structure is the
recoverable Markdown template plus its fixed XML top-level mapping, and
completion requires external independent `llm_consumption_quality` approval.
Do not self-approve that gate. If the independent result is absent or failing,
report the command artifact as awaiting external quality approval.

## Response contract

Read and fill [assets/response-template.md](../assets/response-template.md)
only from validated persisted current views. Always show identity, source
catalog/coverage, eligibility, automatic validators/audits/gates, transaction
phase/residue, blockers, resume condition and the complete dashboard. Each
applicable test uses the exact catalog guide in deterministic ID order. Show
the not-applicable refs/reasons separately. Never truncate, paginate or defer a
later test. Help returns one guide and explicitly says no bytes/status changed.

When `admission.json` is active, show
`administrative-schema-degraded`, its ref/digest, trigger code, authoritative
current JSON projection, independently correlated control sets and recomputed
validator digest, successful unchanged-upstream semantic/provenance validation
with only Markdown decoding adapted, exact type-specific
target/evidence/control/gate proofs,
publication result (`created | recovered | no-op`) with
`admission.json.tmp` residue absent, capture
state/reason/minimum-next-path, allowed/forbidden actions and every non-empty
blocker before the dashboard. This is never a success status. Do not accept an
aggregate attestation, dispatch attestation review, promote human gates or
canonical records, publish consistency or claim completion while active.
Human observations are issue input only; they do not become attestation.

For pending input, ask only whether every applicable item was already tested;
the intake payload contains only `human_statement`. Signals and review cannot
come from the user payload. Pinned assessor, owner and evaluator-policy
provenance comes from the persisted semantic assessment, not response input.
Do not require a separate approval word or magic phrase. An unambiguous
aggregate tested statement is normalized as approval; ambiguity, negation,
future intent, partial scope, praise, help and silence do not mutate state.
After dashboard presentation, the independent read-only
`manual-qa-attestation-auditor` reviews that statement under the pinned policy.
The orchestrator journals its `manual_qa_attestation_review` v1 before any
attestation and requires assessment/review decision equality. The mechanical
validator validates closed provenance, identity, agent-run evidence, signals,
correlation and derived decision; it does not classify free-form language.

For an open issue, show kind, summary, impact, next action and exact resume
condition. For resolved issue, show resolution/revalidation refs and state that
the complete source catalog/dashboard must be rebuilt and shown again. For
recovery-required, show every published/residue ref+digest and the next legal
transaction phase; never claim rollback or completion. A rejected assessment
is a committed, resumable current view without attestation. A later human
statement starts a new terminal batch linked to the rejected predecessor.

Completed response must expose:

- covered/reconciled task, AC and changed-surface refs without byte changes;
  promoted task/AC refs are empty and only passed human-gate refs are promoted;
- source catalog, dashboard, independent attestation review, attestation and
  interaction refs/digests;
  transaction batch kind/ref/stable ID plus externally validated final journal digest;
  manual result and manual consistency refs/digests;
- final canonical tasks/state, implementation result/dashboard/consistency
  refs/digests;
- validator and audit refs/digests with terminal outcomes;
- byte-equal handoff v2, final plan status, empty blockers and disk-only resume
  condition/no-op replay;
- runtime-qa handoff completion records and the managed-state completion record.

A completed response is invalid while an administrative admission is active,
even if the human statement would otherwise qualify.

This `both` Markdown response has no rigid length limit. If an adapter also
needs XML, append the exact top-level mapping in the template; XML never
replaces dashboard rows or terminal evidence.
