# loki-generate-inferences — Response Contract

## Primary consumer and projection

The primary consumer is `Both`. Use the routed
[response template](../assets/response-template.md) to materialize recoverable
Markdown without a hard length limit. A human-only projection is
actionable Markdown of at most 7,000 characters. An LLM-only projection returns
only the XML shape below; projection changes serialization only, never status,
permissions, validators, gate state, risks, or next permitted action.

```xml
<loki_generate_inferences_response>
  <summary></summary>
  <status></status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <risks></risks>
  <next_steps></next_steps>
</loki_generate_inferences_response>
```

## Terminal states

- `completed`: one exact approved destination was created once; its canonical
  preparation core is valid, terminal at `pre-investigation-complete`, and all
  required validators passed.
- `partial`: a single artifact exists but a post-write validator cannot support
  full completion. State the artifact, failed validation, and no-rewrite rule.
- `blocked`: no artifact was created because input, authority, policy, root,
  destination, collision, gate, or pre-write validator failed.

Never report `completed` while technical review or a material validator is
pending. Never present `partial` as a ready artifact. Never invent a handoff:
`handoff_count` is always `0` and any attempted handoff is a blocker.

## Required response content

Return actual status, concise summary, exact target or `not-created`, input and
source identities, preparation ID/digest/status, validator evidence,
direct-write completion, gate state, zero-boundary proof, risks/blockers,
resume state, and the minimum next permitted action. Explicitly state that web
research, investigation, agent runs, handoffs, CI, downstream workflows, and
catalog mutation were not performed.

The only optional next step is a separately chosen later workflow using the
validated artifact. Do not invoke, dispatch, schedule, or imply continuation
to `loki-deep-analysis`, planning, execution, CI, catalog maintenance, or any
other command.
