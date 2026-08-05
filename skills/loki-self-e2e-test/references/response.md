---
doc_id: "loki-self-e2e-test-response"
version: "1.0.0"
status: active
last_updated: "2026-08-05"
scope: "Persisted and terminal response contract for loki-self-e2e-test"
not_scope: "The detailed E2E evidence schema already owned by the runbook"
authority: "loki-self-e2e-test execution result and the E2E runbook report contract"
canonical_source: "skills/loki-self-e2e-test/references/response.md"
intended_llm_task: "generation"
source_priority:
  - "validated E2E report and observed terminal state"
  - "current E2E runbook report schema"
  - "this terminal response adapter"
confidence: high
known_conflicts: []
replaced_by: null
---

# Response — loki-self-e2e-test

## Primary output

The primary output is always the finalized directory:

```text
<physical-loki-package-root>/e2e-runs/<e2e-execution-id>/
```

`result.md` and its evidence tree must follow the exact current schema and
section order in [e2e-runbook.md](e2e-runbook.md). Persist
observable prompts/responses, commands, stdout/stderr, states, diffs,
validators, stack traces, and concise decision summaries. Never persist raw
credentials, secrets, private chain-of-thought, or hidden runtime state.

## Terminal response

Consumer: `Both`. Use compact Markdown recoverable by a human and an LLM. Fill
`../assets/response-template.md` with exactly:

- terminal status and one-line summary;
- E2E execution ID;
- `passed` or `failed`;
- observed final plan status or `unavailable`;
- plan directory or `unavailable`;
- absolute report/evidence path;
- terminal handoff, risks, and next step.

Do not repeat the detailed timeline in chat. Do not ask a follow-up question.
Do not offer to repair a failed run. The report owns diagnosis and reproduction.
Human Markdown must stay below 7,000 characters. The `Both` rendering has no
additional hard limit but must remain this compact template.

## Outcome semantics

- `completed`: the E2E report is finalized and its verdict is `passed`.
- `failed`: the E2E report is finalized and its verdict is `failed`, including
  preparation, inference, installation, command, interaction, state, or
  postflight failure.
- A missing report is never a terminal response.
- A still-running subagent, `E2E-INCOMPLETE`, missing postflight decision, or
  pending interaction blocks terminal delivery.

## XML shape when an LLM-only caller requires it

```xml
<command_response>
  <summary></summary>
  <status>completed|failed</status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <risks></risks>
  <next_steps></next_steps>
</command_response>
```
