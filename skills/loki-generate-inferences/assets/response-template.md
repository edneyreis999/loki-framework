# Analytic inference preparation

## Status

`{{completed | partial | blocked}}`

## Summary

{{concise human summary of the preparation result and terminal boundary}}

## Artifact

- Target: `{{exact approved destination | not-created}}`
- Write owner: `{{orchestrator direct-write exception | none}}`
- Write completion: `{{created once | not-run | partial}}`
- Preparation: `{{preparation_id | none}}` / `{{preparation_digest | none}}`

## Preparation core

The following fenced block is the sole machine-readable source for the
preparation core. It contains exactly one canonical `inference_preparation`
object; prose does not extend or override it. The YAML resume state below is
human/recoverable response metadata only, not a second machine-readable
preparation payload and never an authority over this JSON block.

```json
{{canonical JSON object with top-level key "inference_preparation"}}
```

## Validation and boundary

- Validators: {{input, destination, preparation, JSON/digest, Markdown, and zero-boundary outcomes}}
- Handoffs: `0`
- Investigation dispatch: `false`
- Agent runs: `0`
- Web research: `false`
- CI: `not-run`
- Downstream workflows: `[]`
- Catalog mutation: `false`
- Technical review: `{{pending | resolved | not-applicable}}`

## Risks and blockers

{{collision, policy, source, validator, gate, or none}}

## Resume state

This YAML is a recoverable human-facing summary of command state. It is not a
serialization of `inference_preparation`, must not be consumed as an alternate
core, and cannot override the preceding canonical JSON.

```yaml
loki_generate_inferences_state:
  status: "{{completed | partial | blocked}}"
  canonical_consumer_root: "{{path | unknown}}"
  destination: "{{exact path | not-created}}"
  input_mode: "{{inline | file | unknown}}"
  ordered_source_digests: []
  policy_digest: "{{sha256 digest | not-configured}}"
  preparation_id: "{{prep id | none}}"
  preparation_digest: "{{sha256 digest | none}}"
  preparation_status: "{{pre-investigation-complete | partial | blocked | not-run}}"
  write_completion: "{{created-once | not-run | partial}}"
  validators: []
  gate_state: "{{pending | resolved | not-applicable}}"
  blockers: []
  minimum_next_path: "{{one permitted action | none}}"
```

## Next step

{{minimum permitted action; no downstream workflow was invoked}}
