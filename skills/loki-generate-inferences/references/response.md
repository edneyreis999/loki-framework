# loki-generate-inferences — Response Contract

## Canonical semantic response model

This section is the sole normative response schema. The routed Markdown asset,
the human-only Markdown response, and the LLM-only XML response are projections
of one populated instance of this model. A projection may change serialization,
ordering for readability, or omit no semantic field; it cannot change status,
facts, permissions, validators, gates, zero-boundary evidence, risks, blockers,
resume state, or `minimum_next_path`.

```yaml
loki_generate_inferences_response:
  status: "completed | partial | blocked"
  summary: "non-empty concise summary"
  facts: ["observed fact"]
  candidate_inferences: ["exact candidate object from inference_preparation.candidates"]
  sources:
    analysis_input: "inline | canonical file locator"
    ordered_local_sources: ["canonical approved source locator"]
    demand_digest: "sha256:<64-lowercase-hex> | unknown"
    ordered_source_digests: ["sha256:<64-lowercase-hex>"]
    active_policy_id: "non-empty | not-resolved"
    policy_digest: "sha256:<64-lowercase-hex> | not-resolved"
    request_controls_digest: "sha256:<64-lowercase-hex> | not-derived"
  gaps: ["observed gap"]
  destination:
    canonical_consumer_root: "canonical path | unknown"
    directory: "canonical existing directory | unknown"
    resolved_target: "canonical exact path | not-resolved"
    basename: "resolved basename without .md | not-resolved"
    version: "positive integer | not-resolved"
    before_state: "target-absent | target-collided | not-checked"
    write_completion: "created-once | not-run | partial"
  preparation:
    preparation_id: "prep-<64-lowercase-hex> | none"
    input_fingerprint: "sha256:<64-lowercase-hex> | none"
    preparation_digest: "sha256:<64-lowercase-hex> | none"
    status: "pre-investigation-complete | partial | blocked | not-run"
    generation_completion: "semantic-saturation | context-interruption | not-run"
    generation_resume_cursor: "non-empty cursor | none"
    unexplored_surfaces: []
  validators:
    - name: "non-empty validator name"
      status: "passed | failed | blocked | not-run"
      evidence: "non-empty observed evidence or not-run reason"
  gate_state:
    exact_target_approval: "pending | resolved | invalidated | not-applicable"
    technical_review: "pending | resolved | not-applicable"
  zero_execution_boundary:
    dispatch_authorized: false
    investigation_handoffs_dispatched: 0
    agent_runs_created: 0
    handoffs_created: 0
    web_research_performed: false
    ci_performed: false
    downstream_workflows_invoked: []
    catalog_mutation_applied: false
  risks: ["observed risk"]
  blockers: ["observed blocker"]
  resume_state:
    input_mode: "inline | file | unknown"
    invocation_count: "0 | 1"
    directory_snapshot_identity: "non-empty digest or locator | none"
    approval_binding: "canonical-directory+target+basename+version+before-state+one-create | none"
    retained_artifact: "canonical path | none"
  minimum_next_path: "one permitted action | none"
```

Every key is required; every array may be empty when no item exists. `facts` contains only observed
facts. `candidate_inferences` contains the preparation candidates or remains
empty when no usable preparation exists; it never implies investigation or
promotion. `gaps`, `risks`, and `blockers` stay distinct. Missing material data
uses the declared sentinel and normally derives `blocked`, never an invented
value. The canonical fenced `inference_preparation` JSON in the Markdown
artifact remains the sole machine-readable preparation core; this response
model reports its identity and outcome without becoming a second core.

## Markdown projections

The primary consumer is `Both`. Materialize recoverable Markdown with the
routed [response template](../assets/response-template.md). A human-only
projection is valid only when every semantic field fits in actionable Markdown
of at most 7,000 characters. It may shorten prose but never truncate, summarize,
or omit array items or object fields. When lossless projection would exceed the
limit, use the primary `Both` projection without a length cap.

## LLM-only XML projection

Return only this XML projection populated from the same canonical semantic
model. Element names map one-to-one to model fields; collections use repeated
`<item>` elements and empty collections remain present.

```xml
<loki_generate_inferences_response>
  <status></status>
  <summary></summary>
  <facts><item></item></facts>
  <candidate_inferences>
    <item>
      <candidate_id></candidate_id>
      <origin></origin>
      <lifecycle_status></lifecycle_status>
      <summary></summary>
      <investigable_statement></investigable_statement>
      <technologies><item></item></technologies>
      <surfaces><item></item></surfaces>
      <support_evidence_refs><item></item></support_evidence_refs>
      <confirm_or_reject_evidence><item></item></confirm_or_reject_evidence>
      <stop_condition></stop_condition>
      <catalog_locator></catalog_locator>
      <catalog_revision></catalog_revision>
      <duplicate_relation></duplicate_relation>
      <disposition></disposition>
      <disposition_reason></disposition_reason>
      <suggested_capabilities><item></item></suggested_capabilities>
    </item>
  </candidate_inferences>
  <sources>
    <analysis_input></analysis_input>
    <ordered_local_sources><item></item></ordered_local_sources>
    <demand_digest></demand_digest>
    <ordered_source_digests><item></item></ordered_source_digests>
    <active_policy_id></active_policy_id>
    <policy_digest></policy_digest>
    <request_controls_digest></request_controls_digest>
  </sources>
  <gaps><item></item></gaps>
  <destination>
    <canonical_consumer_root></canonical_consumer_root>
    <directory></directory>
    <resolved_target></resolved_target>
    <basename></basename>
    <version></version>
    <before_state></before_state>
    <write_completion></write_completion>
  </destination>
  <preparation>
    <preparation_id></preparation_id>
    <input_fingerprint></input_fingerprint>
    <preparation_digest></preparation_digest>
    <status></status>
    <generation_completion></generation_completion>
    <generation_resume_cursor></generation_resume_cursor>
    <unexplored_surfaces><item></item></unexplored_surfaces>
  </preparation>
  <validators>
    <item><name></name><status></status><evidence></evidence></item>
  </validators>
  <gate_state>
    <exact_target_approval></exact_target_approval>
    <technical_review></technical_review>
  </gate_state>
  <zero_execution_boundary>
    <dispatch_authorized>false</dispatch_authorized>
    <investigation_handoffs_dispatched>0</investigation_handoffs_dispatched>
    <agent_runs_created>0</agent_runs_created>
    <handoffs_created>0</handoffs_created>
    <web_research_performed>false</web_research_performed>
    <ci_performed>false</ci_performed>
    <downstream_workflows_invoked></downstream_workflows_invoked>
    <catalog_mutation_applied>false</catalog_mutation_applied>
  </zero_execution_boundary>
  <risks><item></item></risks>
  <blockers><item></item></blockers>
  <resume_state>
    <input_mode></input_mode>
    <invocation_count></invocation_count>
    <directory_snapshot_identity></directory_snapshot_identity>
    <approval_binding></approval_binding>
    <retained_artifact></retained_artifact>
  </resume_state>
  <minimum_next_path></minimum_next_path>
</loki_generate_inferences_response>
```

Repeat the nested `candidate_inferences/item` structure exactly once per
candidate and preserve candidate order. Serialize `null` candidate scalars as
the exact text `null`; empty arrays remain as present empty parent elements.
No candidate field may be omitted or collapsed into free text.

## Terminal-state derivation

- `completed`: one resolved target was created once; the preparation is valid
  and terminal at `pre-investigation-complete`; every required validator and
  gate passed.
- `partial`: either the capability returned a structurally valid preparation
  whose own status is `partial`, with all limitations and
  `minimum_next_path` preserved, or the single created artifact is retained
  after a post-write validator failure. Name the capability limitation or
  failed validation and preserve the no-rewrite rule.
- `blocked`: no artifact was created because an input, authority, policy value,
  request-control derivation, root, destination, approval, collision, gate, or
  pre-write validator failed.

Never report `completed` while a material validator or gate is pending. Never
present `partial` as ready. `handoffs_created` is always `0`; any attempted
handoff is a blocker. The only optional next action is a separately chosen
later workflow using a validated artifact. Do not invoke, dispatch, schedule,
or imply automatic continuation to any downstream command.
