---
name: lf-analytic-inference
description: Represent, selectively retrieve, validate, and deterministically maintain reusable analytic-inference state. Use when an analysis needs technology-scoped inference lookup, lifecycle/event validation, score and eligibility derivation, or a maintenance proposal without automatic durable mutation.
when_to_use:
  - "Use when an analysis must look up relevant catalogued inferences without loading an entire catalog."
  - "Use when validating inference records, immutable events, derived snapshots, lineage, or policy eligibility."
  - "Use when preparing a maintenance proposal for later gated reconciliation by loki-continuous-improvement."
argument-hint: "[operation, technology evidence, catalog root or records, optional events and policy]"
arguments:
  required:
    - operation
  optional:
    - technology_evidence
    - catalog_root
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
  retrieval_and_ranking: "references/retrieval-and-ranking.md"
  policy: "references/policy-v1.json"
shell: bash
type: skill
status: draft
used_by: [loki-deep-analysis, loki-continuous-improvement, loki-retrospectiva-tecnica]
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
- `retrieve` also requires observed `technology_evidence`, a readable
  `catalog_root`, and a query describing objectives, surfaces, signals,
  versions, evidence, risk, and cost constraints.
- `validate` requires one or more index, record, event, snapshot, or policy
  objects.
- `derive-state` requires a valid record, its ordered event set, and an
  approved policy.
- `propose-maintenance` requires valid derived state, evidence references, and
  the intended operation. It never applies the proposal.

Locate omitted required input only within the caller-approved read scope. Stop
with `insufficient` when it cannot be found; never invent technology, evidence,
records, paths, events, approval, or policy overrides. The default policy is
[policy-v1.json](references/policy-v1.json). Reject an override unless its
schema, provenance, authorization, bounds, and digest are explicit.

## Procedure

1. Read [inference-contract.md](references/inference-contract.md) completely
   for `validate`, `derive-state`, or `propose-maintenance`, and whenever a
   retrieved record will be interpreted or emitted.
2. For `retrieve`, read
   [retrieval-and-ranking.md](references/retrieval-and-ranking.md) completely;
   load technology indices first and only then load candidate records.
3. Validate schema version, identity, revision, locators, lineage, provenance,
   event idempotency, freshness, and policy before deriving any result.
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
  unauthorized override; or a requested mutation lacks its independent gate.

Every output names the operation, policy ID and digest when used, loaded
locators, rejected candidates and reasons, diagnostics, evidence limits, and
terminal state. Empty catalogs and no-match lookups are valid `insufficient`
results, never fabricated success.

## Limits

- Do not load the whole catalog when index filtering can narrow candidates.
- Do not treat catalogued inferences as rules or limits on contextual reasoning.
- Do not automatically promote, merge, reorganize, rewrite, or purge.
- Similarity may request human review; it never authorizes merge or removal.
- Durable catalog reconciliation belongs to `loki-continuous-improvement`.
- Physical purge is irreversible, catalog-owned only, and requires exact
  just-in-time approval independently of policy approval.
- Do not delete reports, retrospectives, evidence, or other external sources.
- Do not create a durable consumer-specific overlay in v1.
- Do not depend at runtime on `planos/**`, consumer-private paths, or package
  inventory files. The v1 base catalog starts empty; fixtures are not seed data.

## Validation and gates

Use deterministic validation for schema, exact duplicates, IDs, revisions,
locators, lineage, event replay, counters, score, ordering, limits, and policy
digests. Unknown cost remains `unknown` or `unsupported`, never zero.

Packaged contract changes require `technical-review`. Durable promotion,
reorganization, merge, or policy change requires applicable review and human
approval. Purge additionally requires a separate just-in-time approval bound to
exact inference IDs, canonical catalog-owned paths, and a dry-run digest.
