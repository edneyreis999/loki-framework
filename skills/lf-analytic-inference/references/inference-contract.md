# Analytic Inference State Contract v2

The active policy keeps `persistent_catalog_limit` exclusively for durable
active catalog occupancy. It cannot limit contextual generation, preparation
selection, or total retrieval. Retrieval uses
`catalog_retrieval_page_size` only to paginate deterministic index-first reads;
generation uses a non-terminal `minimum_candidate_floor` with no ceiling and
ends only at semantic saturation or a resumable context interruption.

Read this contract when validating, interpreting, deriving, or proposing a
change to analytic-inference state. Canonical XML v2 is the only normative
representation for live registry, catalog, record, and event documents. The
control plane remains JSON: policy, request, proposal, approval, target or
migration manifest, digest envelope, and CLI output are not XML state.
Unknown XML elements, attributes, namespaces, mixed content, or ambiguous types
fail closed.

## Consumer root and state layout

`consumer_root` is an internal, auditable boundary for every catalog-backed
operation. Resolve it exactly once from canonical `pwd` at command start. Every
command must be launched from the consumer project root. There is no public
root parameter or adapter-metadata fallback, and Git, environment variables,
source or analysis paths, documentation and `.loki` discovery cannot override
the working-directory boundary. Reports, resume state, write envelopes and
approvals record the canonical root with resolution source `canonical-pwd`.

The only live production state layout is:

```text
<consumer-root>/.loki/analytic-inference/v2/
  registry.xml
  catalogs/
    <technology-id>/
      index.xml
      records/
        <inference-id>/
          rev-<revision>.xml
  events/
    <inference-id>/
      <event-id>.xml
```

The consumer owns all live state. The package contains only immutable,
reusable capability: contracts, schemas, scripts, fixtures, and the default
policy. It contains no production catalog, seed, or overlay. The package
policy therefore declares `consumer_state_required: true`,
`package_catalog: false`, and
`initial_consumer_catalog: "absent-or-empty"`.

The state grammar is
[state-document-v2.xsd](state-document-v2.xsd), namespace
`urn:loki:analytic-inference:state:v2`. It defines exactly four document roots:
`registry`, `catalog`, `record`, and `event`. Element order is the XSD sequence;
arrays use their declared container and repeated `item` or `entry` elements;
nullable values use the declared `<none/> | <value>...</value>` choice. Event
`outcome`, tombstone metadata, and snapshot denominators use the recursive
`JsonValueType` grammar so JSON-compatible values retain string, integer,
decimal, boolean, null, object, and array types without embedding JSON text.
Every logical string uses `StringValueType`: `<text>` when every Unicode scalar
is legal XML 1.0 content, otherwise `<base64Utf8>` containing canonical base64
of strict UTF-8 bytes. Unpaired surrogates are invalid input. This preserves
JSON strings containing XML-forbidden controls without changing their logical
value. The choice is deterministic; a value eligible for `<text>` must never be
encoded as base64. Object entries contain `key` then `value` children and are
ordered by Unicode code-point order of their unique decoded key.
An integer never serializes as `number`; decimal values use non-exponent
`xs:decimal` form; booleans are exactly `true` or `false`. When a JSON control
value uses exponent notation, parse it as a finite `decimal.Decimal`, reject
NaN and infinities, and emit the equivalent non-exponent decimal with no
leading plus, no redundant integer zeroes, and no trailing fractional zeroes
(`0` is the only zero form). This preserves numeric value while giving XML one
canonical lexical representation.

## Canonical XML and parser security

The codec uses Python stdlib `xml.etree.ElementTree` only. Before parsing UTF-8
bytes, reject a BOM, invalid UTF-8, `<!DOCTYPE`, `<!ENTITY`, comments, and any
processing instruction other than the one required XML declaration. Entity
declarations and named entity references other than the five predefined XML
escapes are forbidden. No network, external resolver, XInclude, DTD, or custom
parser target is allowed.

After parsing, require the exact v2 namespace, one declared document root, no
foreign namespace, no mixed content or non-whitespace tail, and only XSD-known
elements. State v2 declares no attributes, so any attribute blocks. XSD
validation is followed by semantic checks for
unique and sorted IDs/aliases/entries/object keys, identity/locator parity,
lineage, and cross-document references; XSD success alone is insufficient.

Canonical bytes are:

1. the exact ASCII declaration
   `<?xml version="1.0" encoding="UTF-8"?>` followed by LF;
2. the UTF-8 result of `xml.etree.ElementTree.canonicalize` using C14N 2.0,
   `with_comments=False`, `strip_text=False`, `rewrite_prefixes=False`;
3. one final LF and no BOM.

Register the v2 namespace as the default namespace before serialization.
Decode `StringValueType` before applying required-nonempty, uniqueness, ID, or
ordering rules; string whitespace is logical data and is never trimmed. Writers construct typed elements,
serialize once, parse and validate the serialized bytes, canonicalize again,
and require byte equality before hashing or publication. Readers canonicalize
valid input and require byte equality; merely equivalent non-canonical XML is
blocked rather than silently rewritten during read-only operations.

## Registry and containment

The root `registry.xml` conforms to `RegistryType` in
[state-document-v2.xsd](state-document-v2.xsd). Its `schemaVersion` is `2` and
its `stateLayout` is `analytic-inference-consumer-v2`; these identify the
storage layout, not a change to catalog, record, event, or policy semantics.
Entries are ordered by `technology`; technologies, aliases, `catalogId` values,
and locators are unique across the registry. Each locator is exactly the relative,
technology-bound `catalogs/<technology-id>/index.xml`. A missing registry is
state `absent`; a valid registry with no entries is state `empty`; one or more
valid entries is `loaded`. Read-only lookup of absent or empty state returns
`insufficient`, `mutation_applied: false`, and creates nothing.

Technology IDs, inference IDs, event IDs, and other identifiers used as path
segments must match `[a-z0-9][a-z0-9._-]*`; invalid input blocks without silent
normalization. Registry, index, record, and event locators are relative,
normalized, identity-consistent, and root-bound to the canonical state root.
Absolute locators, `..`, missing targets, layout mismatch, root mismatch,
symlink escape, or root drift fail closed.

The consumer root must already exist as a directory. Before any mutable or
destructive operation, inspect existing `.loki`, feature-root, catalog-parent,
and target components with `lstat`; an operational symlink ancestor or target
blocks. Immediately before each write or delete, revalidate root identity,
ancestors, targets, hashes, and containment by proving the resolved target is
relative to the state root. An approval, locator, or manifest bound to one
consumer root is invalid for every other root.

## Catalog index document

An index is loaded before records and contains:

- `schemaVersion`: integer `1`, preserving the logical catalog schema across
  the XML layout cutover;
- `catalogId`: stable path-segment ID;
- `technology`: normalized technology or domain ID;
- `aliases`: unique normalized strings;
- `activeLimit`: non-negative integer, normally the approved policy value;
- `entries`: unique summaries ordered by `inferenceId`.

Each entry contains `inferenceId`, positive `revision`, `status`, short
`summary`, arrays `technologies`, `surfaces`, `objectives`, `signals`, and a
relative `locator`. Allowed index statuses are `active`, `protected`,
`redirect`, and `tombstone`. A locator must remain under the canonical state
root, resolve to one record, and agree with its identity and revision.

An empty consumer catalog index is valid. Test fixtures and reports never seed
consumer state implicitly.

## Inference record document

A record is the `record` root and `RecordType` sequence in the XSD. The mapping
is lossless and fixed. `schemaVersion` remains integer `1`, preserving the
logical record schema across the XML layout cutover. The sequence is
`schemaVersion`, `inferenceId`, `revision`, `status`,
`statement`, `applicability`, `investigation`, `provenance`, `lineage`, and
`snapshot`. Camel-case XML names map one-to-one to the existing logical field
names; no field may be omitted or represented as an attribute.

Required statistics derived in `snapshot.components` are
`selectedCount`, `investigatedCount`, `validatedCount`, `rejectedCount`,
`materialFindingsCount`, `tasksHelpedCount`, `falsePositiveCount`,
`repeatedEvidenceCount`, and `staleCount`. They map exactly to the unchanged
logical snake-case counters used by the JSON policy/reducer. Preserve rejection
reasons,
agent capabilities used, observed context/tool cost, most recent evidence,
technologies, versions, and surfaces in the event-derived view. Cost may be
`observed`, `unknown`, or `unsupported`; never infer zero.

Compatible editorial changes increment `revision`. A semantic identity change
creates a new ID and lists the old ID in `supersedes`. An N-to-1 merge lists
every parent in `merged_from`; redirects point to the surviving ID. All lineage
graphs must be acyclic and resolvable while the records exist.

## Immutable inference event document

Every event contains:

- `schemaVersion`: integer `1`, preserving the logical event schema across the
  XML layout cutover;
- stable `eventId`, used as the idempotency key;
- `source.analysisRef`, `source.runId`, `source.handoffId`, and
  `source.evidenceRefs`;
- `inferenceId` and positive `inferenceRevision`;
- `stage`: `selected`, `investigated`, `validated`, `rejected`,
  `material-finding`, `task-helped`, `false-positive`, `repeated-evidence`, or
  `stale`;
- typed `outcome`, observable `reason`, and `agentCapability`;
- `cost.context` and `cost.tools`, each observed value, `unknown`, or
`unsupported`. Observed values are finite non-negative decimals; NaN and
infinities block.

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

Read-only operations and installation lifecycle operations perform zero state
writes. The first approved promotion or reorganization may bootstrap the state
root, empty registry, and required technology catalog. Bootstrap prepares
temporary files inside the same consumer `.loki`, validates the complete
proposed state, atomically publishes files, and publishes the registry last.
An identical retry is a no-op; a divergent collision blocks.

Exactly one `technical-implementer` consumer-state writer may operate on the
state root at a time, in `task_scoped_writer` mode with canonical root, exact
targets, validators, and gates in its envelope. New revisions and events use
create-if-absent and never overwrite a divergent identity. Promotion and
reorganization publish new immutable revisions and events before publishing
the technology index last as commit point. Failure before the commit point
preserves the previously visible catalog and reports staging residue; failure
after it blocks for audit and never claims rollback.

Package-contract writes use `framework-artifact-writer`, which never writes
`.loki`. The consumer-state writer never changes package contracts in the same
envelope. Installation, upgrade, uninstall, cleanup, and dry-run never create,
remove, or migrate `.loki`. Any unsupported legacy layout is rejected before
every read or write; this contract prescribes no reader, converter, migration,
or future cutover. Whether `.loki` is ignored or versioned remains a consumer
decision.

Promotion, reorganization, rewrite, deduplication, and merge require evidence,
lineage, deterministic validation, and applicable human approval. Score only
establishes eligibility.

A physical purge is terminal and irreversible. Its deterministic, zero-write
dry-run records canonical consumer and state roots, technology/catalog IDs,
inference IDs and revisions, every catalog-owned target and selector, prior
hashes, policy ID/digest, and a manifest digest. Only a subsequent, single-use
JIT approval bound exactly to those values authorizes deletion. Before the
first delete, revalidate containment, root and ancestors, hashes, eligibility,
target completeness, and approval.

Purge publishes the technology index without purged references before deleting
the now-unreferenced record, snapshot, events, aliases, redirects, tombstones,
and identifiers enumerated by the approved manifest. Each delete names one
exact target. Never delete `.loki`, the feature root, or a broad recursive
subtree; remove only known empty directories that are part of the target set.
Partial failure reports `failed` or `blocked` and all residue, and never claims
rollback or zero traces. Post-validation proves the approved catalog-owned
traces absent, the remaining catalog valid, and external reports,
retrospectives, evidence, and sources byte-identical.

## Validation outcomes

- `valid`: all required schema and integrity checks pass.
- `partial`: usable state exists but freshness, cost, or optional evidence is
  unavailable and explicitly typed.
- `insufficient`: evidence cannot support interpretation or eligibility.
- `blocked`: schema, identity, locator, lineage, event, policy, or approval
  integrity fails.

Validation must report object locators, policy ID/digest, diagnostics, rejected
items, and whether derived state was reconstructed or merely observed.
