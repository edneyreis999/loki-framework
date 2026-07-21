---
doc_id: "analytic-inference-preparation-contract"
version: "1.0.0"
status: "draft"
last_updated: "2026-07-20"
scope: "Exact deterministic pre-investigation preparation object and its pure execution boundary"
not_scope: "XML parsing, catalog mutation, report materialization, investigation, dispatch admission, or workflow orchestration"
authority: "Approved caller envelope, this contract, then lf-analytic-inference contracts"
canonical_source: "skills/lf-analytic-inference-preparation/references/preparation-contract.md"
intended_llm_task: "generation"
source_priority:
  - "approved caller envelope for exact input and permitted read scope"
  - "this preparation contract"
  - "skills/lf-analytic-inference/references/inference-contract.md"
  - "skills/lf-analytic-inference/references/retrieval-and-ranking.md"
  - "skills/lf-analytic-inference/references/policy-v1.json"
  - "normalized input, local sources, and fixture data"
confidence: "high"
known_conflicts:
  - "retrieval-and-ranking.md requests version, explicit exclusion, and evidence rejection from index metadata; the index schema lists none of those fields. The index schema is authoritative for available index fields, so those checks are post-record-load only."
replaced_by: null
---

# Analytic Inference Preparation Contract

<summary>
Define the exact canonical core produced before investigation. The core is
independent of command name, run identifier, timestamp, destination, and its
own digest.
</summary>

## Authority and composition

<instructions>
- `lf-analytic-inference` remains the only authority for canonical root
  resolution, XML parsing, XML validation, locator containment, record/index
  parity, policy interpretation, and live catalog state.
- This contract composes that capability. It contains no parser procedure, XML
  grammar, state layout, or replacement retrieval contract.
- Approved caller input grants only its exact read scope and supplied data. It
  does not change this contract's output keys, root rule, safety boundary, or
  terminal semantics.
- A conflict without declared priority returns `blocked`; never invent a merge.
</instructions>

## Inputs and normalization

<input>
normalized_demand:
  required_keys: [demand_digest, facts, evidence_refs]
permitted_local_sources:
  required_keys: [sources]
  source_item_keys: [locator, digest, facts]
request_controls:
  required_keys: [discovery_limit, relevant_result_floor, cost_budget, safe_preference]
inference_policy:
  required: false
  required_when_supplied: [policy_id, policy_digest, values]
</input>

`demand_digest`, every source `digest`, `catalog_snapshot_digest`,
`policy_digest`, and `request_controls_digest` are lowercase `sha256:`
digests. Canonical JSON is UTF-8, lexicographically sorted object keys, arrays
in their declared order, no insignificant whitespace, and no omitted required
keys. Strings, IDs, and numbers retain the canonical representation supplied by
their authoritative source.

Resolve `consumer_root` exactly once from canonical `pwd` by composing
`lf-analytic-inference`. Return `root_provenance: canonical-pwd`. A caller may
not supply, replace, or cause a second derivation of the root.

## Index-first catalog retrieval

<facts>
- `PIR-INDEX-01`: current index entries prove only `inferenceId`, `revision`,
  `status`, `summary`, `technologies`, `surfaces`, `objectives`, `signals`, and
  `locator` as entry fields.
- `PIR-INDEX-02`: index prefilter may use exact technology, surfaces,
  objectives, signals, allowed index status, and locator/revision identity
  checks that the index exposes.
- `PIR-INDEX-03`: version compatibility, explicit exclusion, and required
  evidence are not index fields. Evaluate them only after the referenced record
  is loaded and validated.
- `PIR-INDEX-04`: the conflict with retrieval-and-ranking wording is resolved
  by index-schema precedence; this resolution remains visible for technical
  review.
</facts>

Load matching indices before records. `absent`, `empty`, and `no-match` are
honest observations that permit contextual candidates only when demand evidence
is sufficient. Invalid root, schema, locator, identity, revision, status,
provenance, traversal, symlink, or containment is `blocked` and fails closed.

## Exact output schema

<output_format>
inference_preparation:
  schema_version: 1
  artifact_type: analytic-inference-preparation
  preparation_id: "prep-<64-lowercase-hex>"
  input_fingerprint: "sha256:<64-lowercase-hex>"
  preparation_digest: "sha256:<64-lowercase-hex>"
  status: pre-investigation-complete | partial | blocked
  input:
    demand_digest: "sha256:<64-lowercase-hex>"
    ordered_source_digests: ["sha256:<64-lowercase-hex>"]
    request_controls_digest: "sha256:<64-lowercase-hex>"
  root:
    consumer_root: "canonical root resolved from pwd"
    root_provenance: canonical-pwd
  source_map:
    sources:
      - locator: "approved relative source locator"
        digest: "sha256:<64-lowercase-hex>"
        facts: []
  policy:
    policy_id: "non-empty policy identifier"
    policy_digest: "sha256:<64-lowercase-hex>"
    values: {}
  catalog_observation:
    state: loaded | absent | empty | no-match | blocked
    catalog_snapshot_digest: "sha256:<64-lowercase-hex> | null"
    indices_read: []
    record_locators_loaded: []
    diagnostics: []
  technologies: []
  candidates: []
  duplicate_analysis:
    exact_duplicates: []
    near_duplicates: []
  selected_for_investigation: []
  planned_investigations: []
  dispatch_admitted: false
  validators: []
  blockers: []
  minimum_next_path: "non-empty next permitted action"
  execution_boundary:
    dispatch_authorized: false
    investigation_handoffs_dispatched: 0
    agent_runs_created: 0
    handoffs_created: 0
    web_research_performed: false
    downstream_workflows_invoked: []
    catalog_mutation_applied: false
</output_format>

All shown keys are required, including empty arrays. `status` is
`pre-investigation-complete` only when validators pass and
`catalog_observation.state` is not `blocked`. `partial` retains the same exact
keys and names its limitation in `blockers` or validator diagnostics.

Each candidate has exactly these keys:

```yaml
candidate:
  candidate_id: "(cat|gen)-<64-lowercase-hex>"
  origin: catalogued | generated
  lifecycle_status: unreviewed
  summary: "non-empty"
  investigable_statement: "non-empty"
  technologies: []
  surfaces: []
  support_evidence_refs: []
  confirm_or_reject_evidence: []
  impact: "typed observed impact or unknown"
  cost: "typed observed cost or unknown"
  stop_condition: "non-empty"
  catalog_locator: "relative locator or null"
  catalog_revision: "positive integer or null"
  duplicate_relation: none | exact-duplicate | near-duplicate
  disposition: selected | rejected | deferred
  disposition_reason: "non-empty observable reason"
  suggested_capabilities: []
```

`selected_for_investigation` is a sorted list of candidate IDs whose
`disposition` is `selected`. `planned_investigations` is a sorted list of
future, declarative investigation intents keyed by candidate ID and contains no
agent identity. `dispatch_admitted` is always `false`; selection and planning
never authorize dispatch.

## Deterministic identity and digest domains

<constraints>
- `PID-01`: `input_fingerprint` is `sha256:` plus SHA-256 of canonical JSON
  for exactly `demand_digest`, `ordered_source_digests`,
  `catalog_snapshot_digest`, `policy_digest`, and `request_controls_digest`.
- `PID-02`: `catalog_snapshot_digest` is supplied by composed validated catalog
  observation; it is `null` only for `absent`, `empty`, or `no-match`.
- `PID-03`: `candidate_id` is `cat-` plus SHA-256 of canonical JSON for a
  catalogued candidate's validated `catalog_locator`, `catalog_revision`, and
  semantic payload; it is `gen-` plus SHA-256 of canonical JSON for
  `input_fingerprint` and a generated candidate's semantic payload. Semantic
  payload is every candidate field except `candidate_id`, including
  `disposition_reason` in every case; its source facts remain included.
- `PID-04`: `preparation_id` is `prep-` plus SHA-256 of canonical JSON for
  `input_fingerprint` and the sorted candidate IDs.
- `PID-05`: `preparation_digest` is `sha256:` plus SHA-256 of canonical JSON
  for the complete `inference_preparation` object with only
  `preparation_digest` omitted.
- `PID-06`: every identity and digest excludes command name, run identifier,
  timestamp, destination, caller identity, and the digest being calculated.
</constraints>

Sort source digests by the ordered `sources` input, technologies and locators
lexicographically, candidates by `candidate_id`, and every ID list
lexicographically. Exact duplicates share a semantic digest and are represented
without merge. Near duplicates remain separate with an observable relation.

## Dispositions and stops

Use `selected` only for candidates that are relevant, investigable, within
policy controls, supported by observable provenance, and not exact duplicates.
Use `rejected` for incompatible, irrelevant, unverifiable, invalid, duplicate,
or over-budget candidates. Use `deferred` for otherwise plausible candidates
whose evidence, cost, or policy decision remains insufficient. Never pad a
floor, treat a score as mutation authority, or promote a candidate.

Required catalog observations are `loaded`, `absent`, `empty`, `no-match`, and
`blocked`. `blocked` is fail-closed: no catalogued candidate may be presented
and the terminal status is `blocked`. The minimum next path names only a
permitted subsequent action; it does not invoke one.

## Validation and terminal boundary

<instructions>
- Validate exact output keys, allowed enums, required-empty arrays, canonical
  ordering, ID uniqueness, digest reproduction, and candidate/disposition
  consistency.
- Validate root provenance once, catalog index/record parity through
  `lf-analytic-inference`, and index-first filtering against `PIR-INDEX-01`
  through `PIR-INDEX-04`.
- Validate all execution-boundary fields literally equal their zero/false/empty
  values before returning `pre-investigation-complete`.
</instructions>

The human decision fixes parity as structural and deterministic by fixtures:
equal normalized fixture inputs, sources, catalog snapshot, and policy must
produce an equal canonical preparation object and digest. It does not promise
byte equality for independent new semantic LLM generations.
