# Analytic inference preparation

This template materializes the canonical semantic response model owned by
`references/response.md`. It does not define a second response schema.

## Status and summary

- Status: `{{completed | partial | blocked}}`
- Summary: {{non-empty concise summary}}

## Facts, candidate inferences, sources, and gaps

- Facts: {{observed facts or []}}
- Candidate inferences: {{preparation candidates or []}}
- Analysis input: `{{inline | canonical file locator}}`
- Ordered local sources: {{locators or []}}
- Demand digest: `{{sha256 digest | unknown}}`
- Ordered source digests: {{digests or []}}
- Active policy ID: `{{policy id | not-resolved}}`
- Policy digest: `{{sha256 digest | not-resolved}}`
- Request controls digest: `{{sha256 digest | not-derived}}`
- Gaps: {{gaps or []}}

## Destination and write

- Canonical consumer root: `{{path | unknown}}`
- Destination directory: `{{canonical existing directory | unknown}}`
- Resolved target: `{{canonical exact path | not-resolved}}`
- Basename: `{{basename | not-resolved}}`
- Version: `{{positive integer | not-resolved}}`
- Before-state: `{{target-absent | target-collided | not-checked}}`
- Write completion: `{{created-once | not-run | partial}}`

## Preparation core

- Preparation ID: `{{preparation_id | none}}`
- Input fingerprint: `{{sha256 digest | none}}`
- Preparation digest: `{{sha256 digest | none}}`
- Preparation status: `{{pre-investigation-complete | partial | blocked | not-run}}`
- Generation completion: `{{semantic-saturation | context-interruption | not-run}}`
- Generation resume cursor: `{{non-empty cursor | none}}`
- Unexplored surfaces: {{surfaces or []}}

The following fenced block is the sole machine-readable source for the
preparation core. It contains exactly one canonical `inference_preparation`
object; prose and response metadata do not extend or override it. This artifact
template is used only after a preparation core is eligible to be written. A
blocked pre-write result creates no artifact and is reported only through the
terminal response contract.

```json
{{canonical JSON object with top-level key "inference_preparation"}}
```

## Validators and gates

Render validator objects in their canonical order. Repeat the grouped
`Validator` item below exactly once for every validator object; never split,
merge, deduplicate, or omit an item. When the canonical array is empty, render
exactly `- Validators: []` instead of the repeated block.

- Validators:
  - Validator:
    - Name: `{{non-empty validator name}}`
    - Status: `{{passed | failed | blocked | not-run}}`
    - Evidence: {{non-empty observed evidence or not-run reason}}
- Exact-target approval: `{{pending | resolved | invalidated | not-applicable}}`

## Zero execution boundary

- Dispatch authorized: `false`
- Investigation handoffs dispatched: `0`
- Agent runs created: `0`
- Handoffs created: `0`
- Web research performed: `false`
- CI performed: `false`
- Downstream workflows invoked: `[]`
- Catalog mutation applied: `false`

## Risks and blockers

- Risks: {{risks or []}}
- Blockers: {{blockers or []}}

## Resume state

- Input mode: `{{inline | file | unknown}}`
- Preparation invocation count: `{{0 | 1}}`
- Directory snapshot identity: `{{digest or locator | none}}`
- Approval binding: `{{canonical-directory+target+basename+version+before-state+one-create | none}}`
- Retained artifact: `{{canonical path | none}}`

## Minimum next path

{{one permitted action | none; no downstream workflow was invoked}}
