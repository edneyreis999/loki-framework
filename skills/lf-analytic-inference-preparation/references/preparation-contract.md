---
doc_id: "analytic-inference-preparation-contract"
version: "3.0.0"
status: "draft"
last_updated: "2026-07-21"
scope: "Exact deterministic pre-investigation preparation object and its pure execution boundary"
not_scope: "XML parsing, catalog mutation, report materialization, investigation, dispatch admission, or workflow orchestration"
authority: "Approved caller envelope, this contract, then lf-analytic-inference contracts"
canonical_source: "skills/lf-analytic-inference-preparation/references/preparation-contract.md"
intended_llm_task: "generation"
source_priority:
  - "approved caller envelope for exact input and permitted read scope"
  - "this preparation contract"
  - "skills/lf-analytic-inference-preparation/references/candidate-discovery.md"
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
  required_keys: [candidate_ceiling, catalog_retrieval_page_size, minimum_candidate_floor]
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

## Pre-core blocked failure envelope

When a required demand, source, control, policy, authority, or canonical root
fails before every field of `inference_preparation` can be truthfully formed,
return this exact non-persistable capability response instead of inventing a
blocked preparation core:

<output_format>
preparation_failure:
  status: blocked
  stage: input | source | request-controls | policy | root | authority
  blockers: ["sorted unique non-empty observed blocker"]
  minimum_next_path: "one permitted action"
  execution_boundary:
    dispatch_authorized: false
    investigation_handoffs_dispatched: 0
    agent_runs_created: 0
    handoffs_created: 0
    web_research_performed: false
    downstream_workflows_invoked: []
    catalog_mutation_applied: false
</output_format>

Every key is required. This failure envelope is not an
`inference_preparation`, has no preparation identity or digest, is never
persisted by `loki-generate-inferences`, and cannot be interpreted as a partial
candidate core. Use the canonical preparation schema below only after all its
identity-domain fields are available. A later catalog-validation failure may
still produce the fully formed `inference_preparation.status: blocked` defined
below.

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

## Inquiry-first candidate semantics

Read [candidate-discovery.md](candidate-discovery.md) before creating or
classifying candidates. Each candidate represents an unresolved question whose
answer may change a later decision. It is not a proposed solution, task, plan,
or implementation instruction.

For every candidate:

- `summary` names the unknown concisely;
- `investigable_statement` is one direct question ending in `?`;
- `support_evidence_refs` names demand or approved-source facts that caused the question;
- `confirm_or_reject_evidence` contains declarative future lookup actions using the vocabulary in `candidate-discovery.md`;
- `stop_condition` says what observable finding answers the question or proves that permitted evidence cannot answer it;
- a selected `disposition_reason` includes ` | decision-impact: ` followed by why the answer can change a later decision.

Do not emit generated candidates that merely restate the demand, prescribe
implementation, invent project state, or lack a material decision consequence.
A catalogued record that violates inquiry-first shape is invalid before
candidate interpretation and follows the catalog blocking rules. Section names
in the demand are optional and never control coverage.

## Exact output schema

<output_format>
inference_preparation:
  schema_version: 3
  artifact_type: analytic-inference-preparation
  preparation_id: "prep-<64-lowercase-hex>"
  input_fingerprint: "sha256:<64-lowercase-hex>"
  preparation_digest: "sha256:<64-lowercase-hex>"
  status: pre-investigation-complete | partial | blocked
  input:
    demand_digest: "sha256:<64-lowercase-hex>"
    ordered_source_digests: ["sha256:<64-lowercase-hex>"]
    request_controls:
      candidate_ceiling: null
      catalog_retrieval_page_size: "positive integer copied from policy"
      minimum_candidate_floor: "positive integer copied from policy"
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
    diagnostics: ["sorted unique non-empty observable diagnostic"]
    retrieval_pages_read: "non-negative integer"
    retrieval_exhausted: true | false
    retrieval_resume_cursor: "non-empty cursor | null"
  technologies: []
  candidates: []
  duplicate_analysis:
    exact_duplicates:
      - candidate_id: "existing exact-duplicate candidate ID"
        duplicate_of: "different existing candidate ID"
    near_duplicates:
      - candidate_id: "existing near-duplicate candidate ID"
        duplicate_of: "different existing candidate ID"
  selected_for_investigation: []
  planned_investigations:
    - candidate_id: "(cat|gen)-<64-lowercase-hex>"
  dispatch_admitted: false
  generation_state:
    completion_reason: semantic-saturation | context-interruption
    semantic_saturation: true | false
    resume_cursor: "non-empty deterministic cursor | null"
    unexplored_surfaces: []
    explored_surfaces: []
    final_pass_new_distinct_candidates: "0 | null"
    saturation_evidence_refs: [] # sorted unique non-empty strings; non-empty for semantic saturation
  validators: ["sorted unique non-empty name of a check that passed"]
  blockers: ["sorted unique non-empty observable limitation or blocker"]
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

Every schema version, page size, floor, retrieval-page count, final-pass count
and execution-boundary count uses the exact JSON integer type; booleans,
floating-point equivalents and numeric strings are invalid. Boolean fields use
the exact JSON boolean type. These type rules do not alter the stated values.
Every populated list of digests, technologies, surfaces, evidence references,
capabilities, catalog indices, record locators, diagnostics, validators,
blockers or candidate IDs contains non-empty strings. The array itself may
remain empty wherever the schema's cardinality and state rules permit.
All shown keys are required, including arrays when empty. `status` is
`pre-investigation-complete` only when validators pass and
`catalog_observation.state` is not `blocked`. Honest `absent`, `empty`, and
`no-match` observations do not degrade status by themselves. `partial` retains
the same exact keys and requires a real observable non-blocking limitation as
a non-empty string in `blockers` or `catalog_observation.diagnostics`.
`blocked` retains its integrity, authority, root, schema, locator, policy, and
required-provenance failure semantics.

`pre-investigation-complete` requires `blockers: []`. It may retain a catalog
diagnostic only when that diagnostic is informational and does not describe an
unresolved limitation or blocker; diagnostics must never disguise a status
that should be `partial` or `blocked`.

`validators` is a non-empty, lexicographically sorted, unique list of stable,
non-empty check names whose checks passed. A failed check is never listed as a
validator; record the observable failure in `blockers` or
`catalog_observation.diagnostics`. Those two arrays are also sorted, unique
lists of non-empty strings when populated.

Each candidate has exactly these keys:

```yaml
candidate:
  candidate_id: "(cat|gen)-<64-lowercase-hex>"
  origin: catalogued | generated
  lifecycle_status: unreviewed
  summary: "non-empty"
  investigable_statement: "one direct question ending in ?"
  technologies: []
  surfaces: []
  support_evidence_refs: []
  confirm_or_reject_evidence: ["lookup action using one allowed stable prefix"]
  stop_condition: "non-empty"
  catalog_locator: "relative locator or null"
  catalog_revision: "positive integer or null"
  duplicate_relation: none | exact-duplicate | near-duplicate
  disposition: selected | rejected | deferred
  disposition_reason: "non-empty observable reason"
  suggested_capabilities: []
```

Every populated candidate `technologies`, `surfaces`,
`support_evidence_refs`, `confirm_or_reject_evidence`, and
`suggested_capabilities` array contains only non-empty strings. Every
`investigable_statement` ends in `?`. Every non-empty
`confirm_or_reject_evidence` item begins with one allowed stable prefix from
`candidate-discovery.md` and has a non-empty target after the prefix.

`selected_for_investigation` is a sorted list of candidate IDs whose
`disposition` is `selected`. `planned_investigations` is a sorted list of
future, declarative investigation intents. Every item is an exact one-key
object `{candidate_id}` whose non-empty string value is the corresponding
selected candidate ID; no missing or additional key is valid. It contains no
agent identity. `dispatch_admitted` is always `false`; selection and planning
never authorize dispatch.

`request_controls` has exactly three keys. The floor and page size equal their
validated active policy values; `candidate_ceiling` is always `null`.
`request_controls_digest` covers that exact mapping. Reaching the floor does
not end generation and the page size never limits total retrieval. Cost,
impact, round capacity, concurrency and post-investigation accounting are not
preparation controls.

`generation_state.completion_reason: semantic-saturation` requires
`semantic_saturation: true`, a null resume cursor, no unexplored surfaces, at
least one explored surface, and an observable final-pass evidence reference
showing zero new distinct material candidates.
It may honestly complete below the floor; padding is forbidden.
`context-interruption` requires `partial`, `semantic_saturation: false`, a
non-empty cursor and at least one unexplored surface. An unexhausted catalog
page sequence likewise requires `partial` and a non-empty retrieval cursor;
the next invocation continues from that cursor rather than treating the page
boundary as total exhaustion.

## Deterministic identity and digest domains

<constraints>
- `PID-01`: `input_fingerprint` is `sha256:` plus SHA-256 of canonical JSON
  for exactly `demand_digest`, `ordered_source_digests`,
  `catalog_snapshot_digest`, `policy_digest`, and `request_controls_digest`.
- `PID-02`: `catalog_snapshot_digest` is supplied by composed validated catalog
  observation; it is non-null only for `loaded` and is `null` for `absent`,
  `empty`, `no-match`, and `blocked`.
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
lexicographically. Each `duplicate_analysis` array contains exact two-key
objects `{candidate_id, duplicate_of}`, sorted lexicographically by that pair
and unique by `candidate_id`. Both IDs must name distinct existing candidates.
`candidate_id` is the duplicate; `duplicate_of` is its canonical representative
or reference and must have `duplicate_relation: none`. A representative does
not receive the duplicate relation of the pair and may be referenced by
multiple duplicates.
The `candidate_id` in `exact_duplicates` has `duplicate_relation:
exact-duplicate`; the one in `near_duplicates` has `duplicate_relation:
near-duplicate`. Every candidate with either relation appears exactly once in
the corresponding array, and no other candidate appears there. No
`duplicate_of` may also occur as `candidate_id` in either array; chains,
reciprocal pairs, and cycles are invalid within or across the arrays. Exact
duplicates remain represented without merge; near duplicates remain separate
with an observable relation and are not rejected merely for being near.
Duplicate analysis has no separate semantic digest field or digest domain.

## Dispositions and stops

Use `selected` only for candidates that are relevant, investigable, supported
by observable provenance, valid and compatible, and not exact duplicates.
Preserve every such material candidate; neither persistent catalog capacity,
retrieval page size nor the minimum floor may truncate it. Use `rejected` only for irrelevant, invalid,
incompatible, unverifiable, or exact-duplicate candidates. Use `deferred` only
for unresolved essential evidence, compatibility, or context. Cost and impact
never select, reject, defer, rank, or identify a preparation candidate. Never
pad a limit, treat a score as mutation authority, or promote a candidate.

`disposition_reason` begins with exactly one machine-checkable reason code,
followed optionally by ` | ` and observable detail:

- `selected:essential-criteria-satisfied` for `selected`;
- `rejected:irrelevant`, `rejected:invalid`, `rejected:incompatible`,
  `rejected:unverifiable`, or `rejected:exact-duplicate` for `rejected`;
- `deferred:essential-evidence`, `deferred:compatibility`,
  or `deferred:context` for `deferred`.

An exact duplicate is always rejected with
`rejected:exact-duplicate`. A near duplicate remains a distinct candidate and
may not use the exact-duplicate reason. A selected candidate has non-empty
`support_evidence_refs` and `confirm_or_reject_evidence`, and its
`disposition_reason` contains non-empty `decision-impact` detail. There is no
selected candidate ceiling.

## Version compatibility

Schema v3 is the only preparation schema accepted for new selection. Existing
schema-v1 and schema-v2 artifacts are immutable historical evidence. Readers and consumers
must reject v1/v2 before candidate interpretation and require regeneration to a
new separately approved versioned artifact. No reader, conversion, rewrite,
migration, or fallback is permitted. Candidate IDs, preparation IDs, input
fingerprints, and digests naturally recompute from the schema-v3 domains.

Required catalog observations are `loaded`, `absent`, `empty`, `no-match`, and
`blocked`. `blocked` is fail-closed: no catalogued candidate may be presented
and the terminal status is `blocked`. The minimum next path names only a
permitted subsequent action; it does not invoke one.

## Validation and terminal boundary

<instructions>
- Validate exact output keys, allowed enums, required-empty arrays, canonical
  ordering, ID uniqueness, digest reproduction, request-controls equality and
  digest, full selected-candidate preservation without a ceiling, inquiry-first
  candidate shape, lookup-action prefixes, decision impact, and disposition semantics.
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
