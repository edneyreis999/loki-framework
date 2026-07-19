# Analytic Inference Contract v1

Read this contract when validating, interpreting, deriving, or proposing a
change to analytic-inference state. JSON is the normative representation.
Unknown keys fail closed unless a later schema version explicitly permits them.

## Catalog index

An index is loaded before records and contains:

- `schema_version`: integer `1`;
- `catalog_id`: stable non-empty string;
- `technology`: normalized technology or domain ID;
- `aliases`: unique normalized strings;
- `active_limit`: non-negative integer, normally the approved policy value;
- `entries`: unique summaries ordered by `inference_id`.

Each entry contains `inference_id`, positive `revision`, `status`, short
`summary`, arrays `technologies`, `surfaces`, `objectives`, `signals`, and a
relative `locator`. Allowed index statuses are `active`, `protected`,
`redirect`, and `tombstone`. A locator must remain under the approved catalog
root, resolve to one record, and agree with its identity and revision.

The v1 package catalog starts with no entries. An empty index is valid. Test
fixtures and reports never seed it implicitly.

## Inference record

A record contains:

```json
{
  "schema_version": 1,
  "inference_id": "<stable-id>",
  "revision": 1,
  "status": "active",
  "statement": "<testable statement or question>",
  "applicability": {
    "technologies": [],
    "versions": [],
    "surfaces": [],
    "objectives": [],
    "signals": [],
    "exclusions": []
  },
  "investigation": {
    "demand_relation": "<observable relation>",
    "confirm_or_reject_evidence": [],
    "potential_impact": "<impact>",
    "cost": "low",
    "stop_condition": "<observable condition>",
    "suggested_capabilities": []
  },
  "provenance": {
    "source_refs": [],
    "accepted_evidence_refs": [],
    "freshness": "current"
  },
  "lineage": {
    "supersedes": [],
    "merged_from": [],
    "redirect_to": null,
    "tombstone": null
  },
  "snapshot": {
    "algorithm_version": "analytic-inference-score-v1",
    "components": {},
    "score": 0,
    "as_of_event": null,
    "freshness": "current",
    "denominators": {}
  }
}
```

Required statistics derived in `snapshot.components` are
`selected_count`, `investigated_count`, `validated_count`, `rejected_count`,
`material_findings_count`, `tasks_helped_count`, `false_positive_count`,
`repeated_evidence_count`, and `stale_count`. Preserve rejection reasons,
agent capabilities used, observed context/tool cost, most recent evidence,
technologies, versions, and surfaces in the event-derived view. Cost may be
`observed`, `unknown`, or `unsupported`; never infer zero.

Compatible editorial changes increment `revision`. A semantic identity change
creates a new ID and lists the old ID in `supersedes`. An N-to-1 merge lists
every parent in `merged_from`; redirects point to the surviving ID. All lineage
graphs must be acyclic and resolvable while the records exist.

## Immutable inference event

Every event contains:

- `schema_version`: integer `1`;
- stable `event_id`, used as the idempotency key;
- `source.analysis_ref`, `source.run_id`, `source.handoff_id`, and
  `source.evidence_refs`;
- `inference_id` and positive `inference_revision`;
- `stage`: `selected`, `investigated`, `validated`, `rejected`,
  `material-finding`, `task-helped`, `false-positive`, `repeated-evidence`, or
  `stale`;
- typed `outcome`, observable `reason`, and `agent_capability`;
- `cost.context` and `cost.tools`, each observed value, `unknown`, or
  `unsupported`.

An identical `event_id` and canonical payload replays as a no-op. The same ID
with a different payload is a conflict and blocks reconciliation. Stage
transitions are independent: selection does not imply investigation;
investigation does not imply validation; validation does not imply a material
finding; and a material finding does not imply that a task was helped.

Order events deterministically by their explicit sequence/timestamp when the
schema supplies one and then by `event_id`. Reject an ambiguous ordering if it
would change state. A retry after partial failure must converge to the same
canonical snapshot.

## Score and eligibility

`policy-v1.json` activates the approved candidate through its outer policy
status and exact candidate digest. The nested candidate retains its original
`proposed` status because that field is part of the approved, immutable digest;
it does not make the packaged outer policy inactive.

With policy weights `w`, derive:

```text
score = investigated_count       * w.investigated
      + validated_count          * w.validated
      + material_findings_count  * w.material_finding
      + tasks_helped_count        * w.task_helped
      + false_positive_count      * w.false_positive
      + repeated_evidence_count   * w.repeated_evidence
      + stale_count               * w.stale
      + selected_count            * w.selected
```

The packaged v1 policy assigns selection weight zero. Eligibility comparisons
are inclusive:

- promotion: `score >= promotion_min`;
- reorganization: `score <= reorganization_max`;
- purge review: unprotected record and `score <= purge_review_max`.

These booleans are classifications only. They cannot mutate state, satisfy a
gate, or make similarity evidence sufficient. Protected records are never
purge-review eligible.

## Lifecycle and maintenance boundary

Preserve origin and lifecycle states `catalogued`, `generated`, `rejected`,
`selected`, `investigated`, `validated`, and `promoted`. New or retrospective
inferences enter downstream continuous improvement as `unreviewed` candidates.
Only that workflow may reconcile events and propose durable catalog writes.

Promotion, reorganization, rewrite, deduplication, and merge require evidence,
lineage, deterministic validation, `technical-review`, and applicable human
approval. Score only establishes eligibility.

A physical purge is terminal and irreversible. It may remove only the exact
catalog-owned record, index entry, snapshot, events, aliases, redirects,
tombstones, and identifiers bound to an independently approved dry-run digest.
It must fail closed on any ID, canonical-path, target-set, or digest mismatch.
External reports, retrospectives, and evidence sources remain intact.

## Validation outcomes

- `valid`: all required schema and integrity checks pass.
- `partial`: usable state exists but freshness, cost, or optional evidence is
  unavailable and explicitly typed.
- `insufficient`: evidence cannot support interpretation or eligibility.
- `blocked`: schema, identity, locator, lineage, event, policy, or approval
  integrity fails.

Validation must report object locators, policy ID/digest, diagnostics, rejected
items, and whether derived state was reconstructed or merely observed.
