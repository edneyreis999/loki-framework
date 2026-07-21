# loki-deep-analysis — Response Contract

## Consumer and materialization

The primary consumer is `Both`. Materialize the terminal response with
[response-template.md](../assets/response-template.md) as recoverable Markdown
for a human and another LLM, with no hard length limit. Read
[analytic-report-contract.md](analytic-report-contract.md) before filling the
template. Preserve the exact report state; never omit a required category to
imply that work occurred.

Project the same response state for the caller's adapter:

- `Both`: use the recoverable Markdown template above, with no hard length
  limit.
- `LLM`: return valid, stable XML with no prose outside `command_response` and
  exactly the required top-level fields `summary`, `status`, `artifacts`,
  `evidence`, `handoff`, `risks`, and `next_steps`.
- `Human`: return clear, actionable Markdown of at most 7,000 characters,
  prioritizing result, decision, evidence, risk, and next action.

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

Adapter projection changes only serialization, never status, evidence,
validators, gates, risks, resume-critical state, or claim boundaries.

The response has two delivery modes:

- `report-artifact`: an exact approved Markdown destination was written once,
  validated, and is linked as the canonical report. The terminal response may
  summarize it but must retain resume-critical state.
- `response-only`: `destination` was null, no report file was written, and the
  fully materialized report is returned in the terminal response.

Never claim a report artifact when the write, collision check or validator is
pending. Never create a destination while responding. The command's only
possible writes remain the exact approved report file and one exact separately
approved interaction-gate record; it never writes the inference catalog.

## Terminal status

Use exactly one report status:

- `completed`: all selected investigations and material validators are
  terminal, required gates are resolved, and the artifact or response-only
  report is valid;
- `partial`: useful validated results exist, but a source, capability, cost,
  handoff, evidence dimension or optional investigation is degraded;
- `insufficient`: available evidence cannot support an adequate inference or
  material finding;
- `blocked`: missing authority, policy integrity, source, validator, gate,
  target safety, material conflict or non-terminal required handoff prevents
  safe completion;
- `failed`: a terminal execution error leaves no valid report result to claim.

Do not use `completed` while a material validator, gate, approval or handoff is
pending or failed. Record the exact blocker and `minimum_next_path`. Empty
catalogs, no matches, unknown cost, unsupported capability and absent runtime
validation are explicit states, never synthetic success.

## Required terminal content

The response and deep report must make these items recoverable:

- status, concise summary, objective, scope, exclusions and delivery mode;
- report artifact or response-only result and any approved interaction record;
- sources, research gate, technology/surface confidence and limitations;
- catalog indices read and exact record locators selectively loaded;
- catalogued, generated, represented exact-duplicate, near-duplicate, rejected,
  selected, investigated and validated inferences, each preserving origin;
- one immutable preparation-core reference with its exact locator,
  `preparation_id`, `preparation_digest`, input fingerprint, status,
  validator outcomes and zero-state execution boundary;
- canonical preparation candidate projections in their original order, with no
  report-scoped identity or provenance added to the core;
- specialist matches, capability gaps, handoff identities and terminal states;
- material findings, negative findings, conflicts, hypotheses and evidence;
- observed context/tool costs or honest `unknown`/`unsupported`, cumulative
  budget, degradation and stop decisions;
- policy ID/digest and non-normative request controls with values/source or
  `not-configured`;
- structured inference events and generated `unreviewed` candidates;
- evidence status per dimension, sanitization/integrity and missing reasons;
- validators, gates, approvals and human-validation status;
- canonical consumer root and resolution source, derived state root, catalog
  state, registry/catalog/record locators loaded, and `mutation_applied: false`;
- limitations, blockers, residual risks, allowed downstream destinations,
  resume state and `minimum_next_path`.

Use `none` only after verifying that a category is inapplicable. Otherwise use
an empty list plus a reason, or `unknown`, `unavailable`, `unsupported`,
`pending` or `not-configured` as defined by the execution/report contracts.

## Evidence and claim boundaries

Include only observable findings, concise sanitized summaries and approved
evidence references. Do not expose source payload copies, secrets, personal
data, hidden prompts, raw transcripts, raw tool payloads or private/full
chain-of-thought. Do not fabricate agent/run/handoff/evidence identities,
locators, usage or cost.

Inference events reflect only the stage actually observed. Generated
candidates remain `unreviewed`; eligibility, score or report inclusion does not
authorize promotion, merge, reorganization, purge or any catalog mutation.
Always state whether zero-mutation proof passed; `absent` and `empty` are
observed states, not permission to bootstrap.
State explicitly that catalog mutation was not performed.

The response projects, rather than reconstructs, one validated immutable
preparation core. It names the exact core locator, `preparation_id`,
`preparation_digest`, input fingerprint, core status, validator outcomes, and
execution boundary. It preserves the core candidate order, fields,
classification, and content-addressed IDs. It never places `run_id`, timestamp,
destination, caller identity, report identity, or `generated_in_report` inside
the canonical core. Inference events, handoff evidence, agent-run identities,
observed costs, delivery metadata, and investigation outcomes are explicitly
post-boundary evidence and may only refer to a candidate by its existing ID.

Represent consumer/runtime human validation with gate
`<human_validation_gate>`, `required`, state `deferred`, `passed`, `failed` or
`not-applicable`, observable source, evidence references, non-empty reason and
`minimum_next_path`. Do not claim runtime, integration, persisted consumer
state or perceptible behavior validated unless the required gate is `passed`.
Do not use `completed` while a required human-validation gate is unresolved.

## Intermediate and gate response

At a recoverable pause, ask only for the missing decision, approval, source or
capability. Include current status, reason, preserved state,
`minimum_next_path`, exact target when applicable, and the condition to resume.
Do not materialize a false terminal report or silently discard completed work.

## Allowed downstream routing

Recommend only a destination supported by the report evidence:

- `loki-continuous-improvement` for later evaluation of structured events and
  `unreviewed` candidates; this is not promotion authorization;
- `loki-human-decision-preflight` for unresolved material human decisions;
- `loki-generate-action-plan` when decisions and analysis are sufficient for
  executable planning;
- further bounded investigation or `blocked` when evidence is insufficient.

The response must name the expected owner, required input, gates and reason for
the route. Never auto-invoke downstream promotion or planning from Response.
