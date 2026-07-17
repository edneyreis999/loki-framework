# Domain Context Preflight Contract

Use this reference whenever `lf-domain-context-preflight` runs. It is the
complete execution contract for cold-start selection, classification, and
reporting of minimal durable domain context.

## Input Contract

Normalize the required and optional inputs before reading:

```yaml
preflight_input:
  agent: "<required stable agent identity>"
  task_id: "<required stable task identity>"
  task_context:
    objective: "<required>"
    unit_of_work: "<required>"
    relevant_surfaces: []
    known_facts: []
    scope: []
    targets: []
    constraints: []
    validators: []
    gates: []
    task_topics: []
    task_domain_ids: []
  domain_docs_root: "<required resolved domain folder>"
  current_sources:
    - locator: "<path or observation locator>"
      topics: []
      domain_ids: []
      observed_at: "<timestamp, revision, or other freshness locator>"
  material_context_requirements: []
  documentation_handoff_destination: "<caller-provided route or none>"
```

`task_context` must be self-contained even when its explicit `task_topics` or
`task_domain_ids` are empty. Derive those filters from the objective, unit,
surfaces, targets, facts, and constraints, then record the derivation. If the
objective or unit is missing, if the root resolves ambiguously, or if an
asserted material requirement cannot be interpreted, return `blocked` before
reading with the minimum missing input.

## Output Schema

Return exactly one record. Empty lists are explicit evidence that an item was
checked and not found; do not omit fields to hide an unperformed check.

```yaml
domain_context_preflight:
  schema_version: "1"
  agent: ""
  task_id: ""
  required: true
  domain_docs_root: ""
  task_topics: []
  task_domain_ids: []
  relevant_surfaces: []
  selection_basis: []
  read_attempt:
    readme_path: "<domain_docs_root>/README.md"
    status: "read | missing | inaccessible | root-absent"
    reason: ""
  docs_considered:
    - path: ""
      routed_by: "README | exact-topic | exact-domain-id | exact-surface"
      selected: false
      reason: ""
  docs_read:
    - path: ""
      relevance: ""
      matched_topics: []
      matched_domain_ids: []
      matched_surfaces: []
      freshness_status: "current | uncertain | stale | unavailable"
      freshness_evidence: []
  relevant_facts:
    - fact: ""
      source_locator: ""
      source_kind: "current-source | durable-doc"
  conflicts_with_task_context:
    - durable_locator: ""
      current_locator: ""
      resolution: "current-source-prevails"
      gap_recorded: ""
  freshness:
    status: "current | uncertain | stale | unavailable | absent"
    evidence: []
  missing_context:
    - item: ""
      material: false
      substitute_locator: "none"
      impact: ""
  cross_domain_lookup:
    required: false
    destination: "none"
    requested_domain: "none"
    requested_topics_or_ids: []
    reason: ""
  result: "ready | ready-with-gaps | blocked"
  result_reason: ""
  minimum_next_input: "none"
  durable_doc_gap_handoff:
    required: false
    destination: "none"
    gap_summary: []
```

The terminal `result` value must be exactly `ready`, `ready-with-gaps`, or
`blocked`. Other status vocabularies may describe reads or freshness but must
not replace or extend the terminal values.

## Deterministic Decision Procedure

Apply these steps in order. The first blocking condition stops further reads.

1. **Validate required input.** Require one agent, task, self-contained
   objective/unit, and one normalized domain root. Missing or ambiguous input
   yields `blocked` and names only the minimum next input.
2. **Build the filter.** Normalize explicit and derived topics, domain IDs, and
   relevant surfaces. Record each selection basis. Do not add unrelated topics.
3. **Check the root.** If the root is absent, set README status `root-absent`,
   freshness `absent`, and record a gap. Return `ready-with-gaps` unless an
   explicit material requirement lacks a trustworthy current substitute; then
   return `blocked`.
4. **Read README first.** If the root exists, attempt only `README.md` before
   other domain documents. A missing README is a gap and does not authorize a
   directory-wide scan. An inaccessible README blocks only when it prevents
   safe routing of a demonstrated material requirement with no narrow
   alternative.
5. **Select narrowly.** Prefer README links matching an exact task topic,
   domain ID, or relevant surface. If README is missing, use only filenames or
   already-known locators with exact matches. Record considered-but-not-selected
   candidates; do not enumerate unrelated folder contents for completeness.
6. **Stop when sufficient.** Read candidates one at a time and stop when every
   material requirement is covered, contradicted by a current source, or
   explicitly classified as a gap. More potentially relevant files are not a
   reason to continue.
7. **Resolve freshness.** Apply the freshness rules below. Current source
   evidence wins over stale durable content. Record both locators and the gap;
   never silently merge or repair the document.
8. **Route cross-domain needs.** Do not directly inspect another domain. If
   material context is known to live elsewhere, request only named topics,
   IDs, or surfaces through `documentation_handoff_destination`. If no route is
   provided and the context has no substitute, return `blocked` with that route
   as the minimum next input.
9. **Choose the terminal result.** Use the decision table and explain the
   decisive evidence.

## Result Decision Table

| Condition after minimal reads | Result |
| --- | --- |
| Every material requirement is covered by trustworthy current or durable evidence; no known material or non-material gap remains | `ready` |
| A folder/README/doc is absent, stale, uncertain, or unavailable, but the gap is non-material or a trustworthy current substitute permits safe execution | `ready-with-gaps` |
| A durable/current conflict was resolved in favor of a trustworthy current source and recorded for later documentation handling | `ready-with-gaps` |
| A cross-domain lookup is useful but non-material, or a substitute permits safe execution while the narrow handoff proceeds | `ready-with-gaps` |
| Required input, path identity, or read permission is unresolved and safe classification cannot continue | `blocked` |
| A demonstrated material requirement has neither trustworthy evidence nor a substitute | `blocked` |
| A material cross-domain requirement has no narrow handoff route or substitute | `blocked` |

Do not infer materiality merely because documentation is missing. Materiality
must come from task constraints, validators, gates, sensitive surfaces, an
explicit caller requirement, or a concrete safety/correctness dependency.

## Freshness Rules

Classify freshness using observable evidence rather than document age alone:

- `current`: the durable fact is corroborated by the current source/revision or
  has an applicable freshness marker with no conflicting newer evidence;
- `uncertain`: relevant documentation was read, but available evidence cannot
  establish whether it still matches the current project;
- `stale`: a current project source demonstrably supersedes or contradicts the
  durable fact;
- `unavailable`: the relevant known document or source cannot be read;
- `absent`: the resolved domain root does not exist.

When evidence differs, prefer the most direct current project observation for
task execution. Preserve the stale durable claim and the current locator in
`conflicts_with_task_context`; report a durable gap through the caller's
documentation mechanism. This preflight never authorizes the Write Agent to
correct consumer documentation.

## Cross-Domain Handoff

A handoff is a routing output, not an agent invocation performed by this skill.
Request the smallest unit another domain can answer:

```yaml
cross_domain_lookup:
  required: true
  destination: "<caller-provided documentation librarian/catalogador route>"
  requested_domain: "<one domain>"
  requested_topics_or_ids: ["<specific topic, ID, or surface>"]
  reason: "<why this unit is material or useful>"
```

Do not request an entire documentation tree, let the current agent search the
other domain directly, or treat the handoff as permission to write. Durable
correction or promotion remains a separate workflow owned by the configured
documentation mechanism.

## Conceptual Fixtures

These fixtures test the decision procedure without relying on conversation
memory.

### Current

- Input: root and README exist; README routes topic `combat-save` to one file;
  the file matches the current save schema; all material requirements are met.
- Reads: README, then the routed file; no other domain file.
- Output: freshness `current`, result `ready`, no gap or handoff.

### Stale

- Input: README routes an API topic to one durable file; a current source shows
  a newer field name; the current source is sufficient for the task.
- Reads: README, the routed file, and the already-provided current source.
- Output: freshness `stale`; conflict resolution
  `current-source-prevails`; durable gap handoff required; result
  `ready-with-gaps`. No doc edit occurs.

### Unavailable

- Input: README routes a material rule to one document that is inaccessible;
  no current substitute is available.
- Reads: README attempt and the narrow routed document attempt only.
- Output: freshness `unavailable`, result `blocked`, minimum next input is read
  access or a trustworthy locator for that one material rule.

If the same unavailable document is non-material or a trustworthy current
source substitutes for it, the result is `ready-with-gaps` instead.

### Absent

- Input: the normalized domain root does not exist and no material dependency
  on durable context is demonstrated.
- Reads: none; README status is `root-absent`.
- Output: freshness `absent`, explicit missing-context item, result
  `ready-with-gaps`.

If the task explicitly requires an approved domain decision found nowhere else,
the same absent root yields `blocked` and names that decision or a narrow
handoff route as `minimum_next_input`.

## Stop And Validation Conditions

Stop and return `blocked` when safe execution needs missing required input,
permission, material evidence, or a cross-domain route. Stop without changing
files when asked to write consumer docs, scan the entire folder without task
filters, inspect another domain directly, or orchestrate downstream work.

Before returning, verify:

1. the record has schema version `1` and all output fields;
2. one and only one terminal result is used;
3. every read document has an exact task relevance link;
4. the README attempt precedes other domain reads when the root exists;
5. current evidence prevails over stale durable content with both locators
   recorded;
6. an absent root defaults to `ready-with-gaps` unless materiality and lack of
   substitute are explicit;
7. every cross-domain request is narrow and uses the configured handoff route;
8. `blocked` always names `minimum_next_input`;
9. no output grants consumer-documentation write authority or triggers a broad
   scan.
