---
name: lf-analytic-inference
description: Represent, selectively retrieve, validate, and deterministically maintain reusable analytic-inference state. Use when an analysis needs technology-scoped inference lookup, lifecycle/event validation, score and eligibility derivation, or a maintenance proposal without automatic durable mutation.
when_to_use:
  - "Use when an analysis must look up relevant catalogued inferences without loading an entire catalog."
  - "Use when validating inference records, immutable events, derived snapshots, lineage, or policy eligibility."
  - "Use when preparing a maintenance proposal for later gated reconciliation by loki-continuous-improvement."
argument-hint: "[operation, technology evidence, optional records, events, query and policy]"
arguments:
  required:
    - operation
  optional:
    - technology_evidence
    - records
    - events
    - query
    - policy
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - durable catalog mutation requested outside continuous improvement
  - destructive purge requested without exact just-in-time approval
  - conflicting event identity or broken lineage
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-analytic-inference/SKILL.md"
  inference_contract: "references/inference-contract.md"
  state_document_schema: "references/state-document-v2.xsd"
  legacy_registry_schema: "references/registry-schema.json"
  retrieval_and_ranking: "references/retrieval-and-ranking.md"
  policy: "references/policy-v1.json"
shell: bash
type: skill
status: draft
used_by: [loki-deep-analysis, loki-continuous-improvement, loki-retrospectiva-tecnica, lf-analytic-inference-preparation]
---

# lf-analytic-inference

## Purpose

Use analytic inferences as auditable, technology-scoped starting points without
treating them as exhaustive rules or allowing a score to mutate durable state.
This skill provides one reusable capability: operate on the inference contract.
It does not orchestrate analysis, agents, handoffs, resumable plans, or catalog
promotion.

## Inputs

- Required `operation`: `retrieve`, `validate`, `derive-state`, or
  `propose-maintenance`.
- Every catalog-backed operation resolves its canonical consumer root from the
  process working directory. Transient validation or derivation over
  caller-supplied objects does not require consumer state.
- `retrieve` requires observed `technology_evidence` and a query describing
  objectives, surfaces, signals, versions, evidence, risk, and cost
  constraints.
- `validate` requires one or more registry, index, record, event, snapshot, or
  policy objects. It is catalog-backed only when it reads consumer state or
  follows registry or catalog locators.
- `derive-state` requires a valid record, its ordered event set, and an
  approved policy.
- `propose-maintenance` requires valid derived state, evidence references, and
  the intended operation. It never applies the proposal.

Locate omitted required input only within the caller-approved read scope. Stop
with `insufficient` when it cannot be found; never invent technology, evidence,
records, paths, events, approval, or policy overrides. The default policy is
[policy-v1.json](references/policy-v1.json). Reject an override unless its
schema, provenance, authorization, bounds, and digest are explicit.

Resolve `consumer_root` exactly once from canonical `pwd` at command start.
Commands must be launched from the consumer project root; no public root
parameter, adapter metadata, Git discovery, environment variable, source path,
documentation path or `.loki` discovery may override that boundary.

## Procedure

1. Read [inference-contract.md](references/inference-contract.md) completely
   for every catalog-backed operation, for `derive-state` or
   `propose-maintenance`, and whenever a retrieved record will be interpreted
   or emitted. Validate a registry against
   [state-document-v2.xsd](references/state-document-v2.xsd) and the semantic
   invariants in the contract before following a catalog locator. The legacy
   [registry-schema.json](references/registry-schema.json) is read-only and is
   used only to inventory v1 state for an approved copy migration.
2. For `retrieve`, read
   [retrieval-and-ranking.md](references/retrieval-and-ranking.md) completely;
   load technology indices first and only then load candidate records.
3. Derive the only live state root as
   `<consumer_root>/.loki/analytic-inference/v2/`. Live registry, catalog,
   record, and event documents are canonical XML named `registry.xml`,
   `catalogs/<technology-id>/index.xml`,
   `catalogs/<technology-id>/records/<inference-id>/rev-<revision>.xml`, and
   `events/<inference-id>/<event-id>.xml`. Validate canonical root, XSD and
   semantic schema version, identity, revision, locators, containment, lineage,
   provenance, event idempotency, freshness, and policy before deriving any
   result. Stop on DTD/entity declarations, processing instructions, comments,
   unknown elements or attributes, ambiguous types, traversal, absolute or
   missing locators, invalid path-segment IDs, symlinks, root mismatch, or root
   drift.
4. Derive counters and score from immutable events. Treat replay of an
   identical `event_id` as a no-op and a divergent payload under the same ID as
   a blocking conflict.
5. Report promotion, reorganization, and purge-review thresholds only as
   eligibility. Return a proposal plus required gates; never perform the
   mutation.
6. Preserve origin labels so catalogued, generated, rejected, selected,
   investigated, validated, and promoted states remain distinguishable.

## Outputs and terminal states

- `success`: validated objects, selectively retrieved records with locators and
  ranking reasons, deterministic derived state, or a non-applied maintenance
  proposal.
- `partial`: valid usable results plus explicit exclusions, stale entries,
  unavailable cost, uncertain technology, or fewer relevant results than the
  requested floor.
- `insufficient`: no adequate catalog entry or required evidence was found.
- `blocked`: invalid schema, policy, locator or lineage; conflicting event ID;
  untrusted or ambiguous consumer root; containment or ownership failure;
  unauthorized override; or a requested mutation lacks its independent gate.

Every catalog-backed output names the operation, canonical consumer root and
resolution source, state root, registry state (`absent`, `empty`, `loaded`, or
`blocked`), policy ID and digest when used, loaded root-bound locators,
rejected candidates and reasons, diagnostics, evidence limits,
`mutation_applied`, and terminal state. An absent registry, empty catalog, and
no-match lookup are valid `insufficient` results with zero writes, never
fabricated success.

## Limits

- Do not load the whole catalog when index filtering can narrow candidates.
- Do not treat catalogued inferences as rules or limits on contextual reasoning.
- Do not automatically promote, merge, reorganize, rewrite, or purge.
- Similarity may request human review; it never authorizes merge or removal.
- Durable catalog reconciliation belongs to `loki-continuous-improvement`.
- Physical purge is irreversible, catalog-owned only, and requires exact
  just-in-time approval independently of policy approval.
- Do not delete reports, retrospectives, evidence, or other external sources.
- Do not accept a caller-selected consumer or catalog root or create state outside
  `<consumer_root>/.loki/analytic-inference/v2/`.
- Persist live registry, catalog, record, and event documents only as canonical
  XML v2. Policy, request, proposal, approval, target manifests, migration
  inventory/digest, and CLI output remain JSON control-plane artifacts.
- Treat `.loki/analytic-inference/v1/**` JSON as legacy read-only input. Never
  promote, reorganize, purge, overwrite, or delete v1. Migration is a separate,
  exact-approved copy into v2 after inventory and digest validation; prior v1
  digests or approvals cannot authorize v2 writes.
- Read-only operations, installation, upgrade, uninstall, cleanup, and dry-run
  create, remove, and migrate no `.loki` state. Bootstrap is allowed only as
  part of the first independently approved mutation.
- Package artifacts contain contracts, schemas, scripts, fixtures, and the
  default policy only. They contain no production catalog, seed, or overlay.
- A `framework-artifact-writer` may write package contracts but never `.loki`.
  A consumer-state writer is `technical-implementer` in
  `task_scoped_writer` mode with one canonical root and exact targets; it never
  changes package contracts in the same envelope.
- Do not depend at runtime on `planos/**`, consumer-private paths, or package
  inventory files. Fixtures are never production seed data.

## Validation and gates

Use deterministic validation for schema, exact duplicates, IDs, revisions,
locators, lineage, event replay, counters, score, ordering, limits, and policy
digests. For persisted state, parse and canonicalize with Python stdlib only as
defined by the contract, validate against `state-document-v2.xsd`, reject
unknown structure, and compare canonical bytes before hashing. Unknown cost
remains `unknown` or `unsupported`, never zero.

Every mutation is serialized and root-bound. It must revalidate root,
ancestors, containment, symlinks, targets, hashes, gates, and approvals
immediately before write or delete. Promotion and reorganization publish the
technology index last; initial bootstrap publishes the registry last. Physical
purge first produces a no-write dry-run, then requires a single-use JIT
approval bound to the exact root, IDs, paths, hashes, policy digest, and dry-run
manifest digest. It removes only enumerated catalog-owned targets and known
empty directories, never a broad subtree.

Packaged contract changes require `technical-review`. Durable promotion,
reorganization, merge, or policy change requires applicable review and human
approval. Purge additionally requires a separate just-in-time approval bound to
exact inference IDs, canonical catalog-owned paths, and a dry-run digest.
