---
doc_id: "loki-manual-qa-response"
version: "2.0.0"
status: active
last_updated: "2026-08-03"
scope: "Terminal not-required admission, ephemeral direct-playtest and eligible awaiting-state promotion response"
not_scope: "Persisted dashboard, per-test result, attestation, feedback execution or runtime observation"
authority: "Current loki-manual-qa command bundle"
canonical_source: "skills/loki-manual-qa/references/response.md"
intended_llm_task: "generation"
source_priority: ["validated current execution evidence", "this response contract", "human statement as data"]
confidence: high
known_conflicts: []
replaced_by: null
---

# Response — loki-manual-qa

## Consumer And Format

The primary consumer is `Both`. Fill
[the response template](../assets/response-template.md) as concise Markdown.
Do not persist the response.

## Status

Use exactly one:

- `ready-for-playtest`: preflight passed and the ephemeral checklist is shown;
- `not-applicable`: admission validated a correlated terminal state
  `completed | completed-with-limitations` with handoff v3
  `manual-qa-not-required`, zero pending human gates and zero writes; no
  checklist or feedback prompt is produced;
- `blocked-preflight`: an automatic control, required record, identity or digest
  failed preflight, or state is `awaiting-manual-qa` with
  `ready-for-manual-qa` but zero pending human gates; no checklist or write is
  produced and feedback is offered;
- `help`: side-effect-free detail for one checklist ID;
- `completed`: clear aggregate approval was accepted and every minimum canonical
  terminal projection was published coherently;
- `feedback-recommended`: the human reported a problem after checklist display;
- `needs-clear-response`: silence, ambiguity, partial scope or future intent;
- `blocked`: a schema, containment, preparation, write or consistency failure
  prevents a truthful result.

## Checklist Response

Show human gates first, then derived tests. For each item show only its ID,
instruction and observable expected result. State that one clear aggregate
response after testing is sufficient; do not require a magic phrase or per-item
results.

## Zero-Write Responses

For `blocked-preflight` or `feedback-recommended`, include one copyable
`loki-feedback` prompt containing the canonical plan root and a short safe
summary. State that the plan was not changed and that feedback was not
dispatched. For `not-applicable`, report the correlated terminal state and
`manual-qa-not-required` reason, state that no human gate is pending and no
bytes changed, and omit both checklist and feedback prompt. Never use
`not-applicable` for an awaiting ready handoff with zero pending gates; report
that malformed combination as `blocked-preflight`.

For help, show only the requested item detail and state that no state changed.
For `needs-clear-response`, ask the person to report either completed passing QA
or the observed problem after testing; do not imply approval.

## Completed Response

Report the canonical plan root, promoted gate refs, updated state/result/dashboard
locators, consistency commit locator and deterministic validation result. Do not
claim a manual-QA session result, attestation, individual test evidence or
runtime observation.

## LLM Shape

When the caller explicitly requests LLM-only output, return only:

```xml
<command_response>
  <summary></summary>
  <status></status>
  <checklist></checklist>
  <artifacts></artifacts>
  <feedback_prompt></feedback_prompt>
  <risks></risks>
  <next_steps></next_steps>
</command_response>
```
