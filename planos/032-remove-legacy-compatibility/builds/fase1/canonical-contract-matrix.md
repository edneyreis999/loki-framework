# Canonical contract matrix — remove legacy compatibility

Scope: task 1.1 source-map confirmation. This is an evidence artifact, not a
contract change. “Current” means the source currently identifies that format as
the canonical form for its own family; schema numbers are not comparable across
families.

| Family | Canonical format/layout | Sources and paths | Classification | Negative inputs/fixtures that must fail before a write | Pending decision / risk |
| --- | --- | --- | --- | --- | --- |
| Agentic run manifest | XML `agentic_run_manifest`, `schema_version="4"` | `scripts/validate-agentic-run-state.py` (manifest checks and self-tests); `templates/agentic-run-manifest-template.xml`; `skills/lf-template-library/references/templates/agentic-run-manifest-template.xml`; `../../analise.md` | Current canonical contract; schemas 1–3 are Loki legacy compatibility | Manifest schema 1/2/3, unknown root schema, or manifest 4 paired with report other than 5 or digest other than 4 | Validator still contains legacy readers/positive fixture paths; task 2.1 must close acceptance to the canonical grammar. |
| Agent run report | XML `agent_run_report`, `schema_version="5"` | `scripts/validate-agentic-run-state.py` (manifest/report pairing); `templates/agent-run-report-template.xml`; `skills/lf-template-library/references/templates/agent-run-report-template.xml`; `../../analise.md` | Current canonical contract; prior report schemas are Loki legacy compatibility | Report schema 4 or any non-5 report when a schema-4 manifest has a report | `legacy_reader_optional="true"` remains in current templates and must be removed with the legacy reader in task 2.1. |
| Agentic run digest | XML `agentic_run_digest`, `schema_version="4"` | `scripts/validate-agentic-run-state.py` (digest checks and self-tests); `templates/agentic-run-digest-template.xml`; `skills/lf-template-library/references/templates/agentic-run-digest-template.xml`; `../../analise.md` | Current canonical contract; digest schema 3 is Loki legacy compatibility | Digest schema 3 or any non-4 digest when a schema-4 manifest has a digest; a consultive checkpoint without digest 4 | Legacy success fixtures and optional-reader markers must become negative coverage in task 2.1. |
| Write-test review (WTR) | Nested XML `write_test_review`, `schema_version="1"`; coverage manifest is also schema 1 | `scripts/validate-agentic-run-state.py: validate_manifest_wtr_shape, validate_projection_wtr_shape`; `scripts/validate-run-plan-review-state.py`; `templates/agentic-run-*-template.xml`; `skills/lf-run-plan-execution/SKILL.md` (`WTR-*`); `../../analise.md` | Current, family-specific schema 1 — **not legacy** | Missing/extra fields, invalid digest/enum/identity, or a schema other than 1 where the WTR contract requires 1 | The current validator accepts and the three agentic templates emit optional `legacy_reader_optional="true"`. It is legacy compatibility to remove in task 2.1, while WTR schema 1 remains canonical. |
| Session evidence | XML `agent_session_evidence`, `schema_version="1"` | `templates/agent-session-evidence-template.xml`; `skills/lf-template-library/references/templates/agent-session-evidence-template.xml`; `skills/lf-agent-execution-evidence/scripts/validate-session-evidence.py`; `../../analise.md` | Current, family-specific schema 1 — **not legacy** | Root other than `agent_session_evidence`, schema other than 1, malformed/sensitive evidence per its validator | Legacy retrospective policy fields are the removal target, not the evidence schema version; task 2.2 must preserve the closed positive policy. |
| Execution knowledge | XML `execution_knowledge_entry`, `schema_version="1"` | `templates/execution-knowledge-entry-template.xml`; `skills/lf-template-library/references/templates/execution-knowledge-entry-template.xml`; `scripts/validate-execution-knowledge.py`; `agents/execution-knowledge-cataloger.md`; `../../analise.md` | Current, family-specific schema 1 — **not legacy** | Root other than `execution_knowledge_entry`, schema other than 1, invalid provenance/lineage | Do not remove this format while eliminating agentic reader compatibility. |
| Technical retrospective input | `execution_evidence_sources` as the current public evidence input | `skills/loki-retrospectiva-tecnica/SKILL.md`; `skills/loki-retrospectiva-tecnica/references/execution.md`; `../../analise.md` | `operational_trace` is Loki legacy public compatibility; evidence sources are current | Supplying `operational_trace` must fail explicitly before retrospective processing/write | Task 2.3 owns the public-input cut and its negative fixture; source currently still documents the legacy input. |
| Analytic inference persisted state | XML v2 under `<consumer-root>/.loki/analytic-inference/v2/`: `registry.xml`, technology `index.xml`, record revisions and events; registry `schemaVersion=2`, `stateLayout=analytic-inference-consumer-v2` | `skills/lf-analytic-inference/references/inference-contract.md`; `skills/lf-analytic-inference/references/state-document-v2.xsd`; `skills/lf-analytic-inference/scripts/state_xml.py`; `../../analise.md` | XML v2 layout is current; `.loki/analytic-inference/v1/**`, JSON registry/catalog/event readers and `migration-dry-run` are Loki legacy compatibility | v1 layout, JSON persisted state, wrong namespace/root, unknown XML member/attribute, noncanonical bytes, locator escape, invalid layout/version | Catalog, record and event XML subdocuments deliberately retain logical `schemaVersion=1`; they are current subdocument schemas, not v1 layout. Ambiguous analytic fixtures (including JSON fixtures) are intentionally deferred to task 3.1 for individual classification. |
| Installation scopes | JSON `schema_version: 2`, scoped artifact declarations without `artifacts.commands` | `install-scopes.json`; `scripts/install-loki-symlinks.py`; `scripts/validate-install-scopes.py`; `scripts/validate-install-loki-upgrade.py`; `../../analise.md` | Schema 2 is current; schema 1, `artifacts.commands`, cleanup planning/application, legacy command links and `removed_legacy_links` are Loki legacy compatibility | Scope schema 1, schema 2 with `artifacts.commands`, `--cleanup-legacy-commands`, parent symlink, real file, or consumer-owned destination must block before mutation | Task 4.1 removes the migration surface but retains safety/non-interference cases as negative tests. |
| Documentation index navigation | Consumer `docs/index.xml` | `skills/lf-index-navigator/SKILL.md`; `skills/lf-index-navigator/references/index-xml-contract.md`; `../../analise.md` | `docs/index.xml` is current; consumer fallback to `index.md` is Loki legacy operational fallback | Missing `docs/index.xml` must produce explicit failure rather than read a consumer `index.md` | Root package `index.md` remains canonical package content and is out of scope for deletion. |
| Goose projection | No surviving Goose projection | `../../analise.md` (authority finding); tracked `goose/**` inventory; approved user decision recorded in `../../tasks.md` | Approved removal, not a replacement compatibility contract | Any reference that assumes a Goose source/projection after deletion must fail validation before package publication | Removal is approved; task 5.1 owns deletion and reference validation. This task does not modify Goose. |

## Classification review result

- A `schema_version=1` value is **not** classified as legacy merely by its
  number. WTR, session evidence, and execution knowledge are canonical schema-1
  families; analytic catalog/record/event subdocuments likewise retain logical
  `schemaVersion=1` within the canonical XML v2 layout.
- Legacy classification is therefore source-and-family based: old agentic
  reader schemas, retrospective `operational_trace`, analytic persisted v1 and
  migration reader, install schema 1/cleanup, and consumer index fallback.
- The matrix has a source for each required family from the demand/analysis and
  a current implementation or contract source. No package artifact was changed
  during this confirmation.

## Canonical shape and pre-write rejection map

The following is the shape-level source map required for removal work. A
listed locator is authoritative when listing every repeated member here would
obscure the grammar. Each rejection is tied to the preceding shape, so it must
be evaluated before a writer accepts or mutates state.

### Agentic manifest, report, digest, and WTR

| Family | Root, version/layout, attributes/keys and canonical children/members | Shape locator and pre-write rejection |
| --- | --- | --- |
| Manifest | Root `agentic_run_manifest`; sole root attribute `schema_version="4"`. Canonical top-level layout is emitted by `templates/agentic-run-manifest-template.xml`; current WTR projection is `write_test_review schema_version="1"` with `request`, `plan_executor_handoff`, `reconciled_policy`, `checkpoints`, `risks`, `state_errors`, and `next_action`. Checkpoint attribute is `checkpoint_id`; coverage manifest attribute is `schema_version="1"`. | `scripts/validate-agentic-run-state.py: validate_manifest_review` plus `validate_manifest_wtr_shape`. Reject non-4 manifest, missing/non-1 WTR, unexpected attributes/children, invalid checkpoint identity/digest/frequency, or incompatible report/digest pairing before write. |
| Report | Root `agent_run_report`; sole root attribute `schema_version="5"`. WTR projection is `write_test_review schema_version="1"`, with exact children `policy_ref`, `policy_digest`, `execution_id`, `checkpoint_ref`, `coverage_digest`, `covered_write_handoff_ids`, `review_lineage`, `outcome`, `findings`, `risk_refs`, `backlog_refs`; `checkpoint_ref` carries `checkpoint_id`; lineage contains `review_handoff_id`, `review_agent_run_id`, `evidence_ref`. | `scripts/validate-agentic-run-state.py: validate_report_review`. Reject non-5 root, non-1 WTR, extra/missing members, invalid locator attribute, or value mismatch against the manifest checkpoint before write. |
| Digest | Root `agentic_run_digest`; sole root attribute `schema_version="4"`; `digest` contains `run_id` and `status`. Its WTR projection is schema 1 with exact children `policy_ref`, `policy_digest`, `requested_frequency`, `effective_frequency`, `checkpoints`, `findings`, `execution_status_effect`, `state_errors`; digest checkpoint attribute is `checkpoint_id`. | `scripts/validate-agentic-run-state.py: validate_digest` (schema-4 branch). Reject schema 3/non-4 for the current contract, missing/non-1 WTR, extra/missing projection members, invalid checkpoint identity/digest, or `execution_status_effect` other than `none` before write. |
| WTR v1 | The current WTR root is the nested `write_test_review schema_version="1"`; it is projection-specific. Manifest shape is the one above; report and digest use their respective exact child sets. The shared coverage-manifest shape is `coverage_manifest schema_version="1"` containing `handoffs` and `reviewer`; each handoff has a `handoff_id`, completion/evidence references, and changed-file hashes. WTR currently permits optional `legacy_reader_optional="true"`: `validate_manifest_wtr_shape` and `validate_projection_wtr_shape` allow it, and the manifest/report/digest templates emit it. | `scripts/validate-agentic-run-state.py: validate_manifest_wtr_shape`, `validate_projection_wtr_shape`, and coverage validators; `templates/agentic-run-manifest-template.xml`, `templates/agent-run-report-template.xml`, `templates/agentic-run-digest-template.xml`; run-plan state grammar: `scripts/validate-run-plan-review-state.py`. Reject a schema other than 1, wrong projection members, unknown attributes other than current `legacy_reader_optional`, invalid enum/digest/coverage identity, or any attempt to infer that WTR v1 is legacy. Task 2.1 removes this optional compatibility attribute without changing WTR v1. |

### Evidence and retrospective input

| Family | Root, version/layout, attributes/keys and canonical children/members | Shape locator and pre-write rejection |
| --- | --- | --- |
| Session evidence | Root `agent_session_evidence schema_version="1"`. Canonical ordered sections are `identity`, `runtime`, `locator`, `snapshot`, `evidence_completeness`, `usage`, `security`, `integrity`, `completion_record`, and `retrospective_policy`. Identity child attributes are typed IDs; every `dimension` has `name` in the exact five-member set; checksum nodes use `algorithm="sha-256"`. | `templates/agent-session-evidence-template.xml`; `skills/lf-agent-execution-evidence/scripts/validate-session-evidence.py: validate`. Reject different root/schema, wrong typed IDs, a non-exact dimension set, invalid locator/snapshot/usage shape, private reasoning, or checksum mismatch before write. The legacy policy fields are a separate task-2.2 removal concern, not a reason to reject schema 1. |
| Execution knowledge | Root `execution_knowledge_entry schema_version="1"`. Canonical sections: `identity`, `lineage`, `materiality`, `capture`, `knowledge`, `security`, `promotion`. `lineage/source_refs/source_ref` has `type` and `authorization`; `knowledge/claims/claim` has `type` and `confidence`; `resolution` and `cause` each have `status` and `confidence`. | `templates/execution-knowledge-entry-template.xml`; `scripts/validate-execution-knowledge.py: validate_entry`. Reject a different root/schema, unknown source/claim/status/confidence enum, escaping lineage, unsanitized/raw/private-reasoning marker, or invalid capture/materiality state before write. |
| Retrospective public input | Canonical request key is `execution_evidence_sources`, an evidence-source collection consumed by the technical-retrospective workflow; it is not persisted XML state. | `skills/loki-retrospectiva-tecnica/SKILL.md: Input`; `skills/loki-retrospectiva-tecnica/references/execution.md` (evidence-source routing). Reject public key `operational_trace` before task processing/write; it is legacy compatibility and has no canonical fallback. |

### Analytic state, installation, navigation, and Goose

| Family | Root, version/layout, attributes/keys and canonical children/members | Shape locator and pre-write rejection |
| --- | --- | --- |
| Analytic inference persisted state | Only live layout: `.loki/analytic-inference/v2/` with `registry.xml`, `catalogs/<technology-id>/index.xml`, `records/<inference-id>/rev-<revision>.xml`, and `events/<inference-id>/<event-id>.xml`. Every document uses namespace `urn:loki:analytic-inference:state:v2`, no attributes, and one root from `registry`, `catalog`, `record`, `event`. Registry has `schemaVersion=2`, `stateLayout=analytic-inference-consumer-v2`, and `entries`; catalog/record/event intentionally have logical `schemaVersion=1`. | `skills/lf-analytic-inference/references/inference-contract.md: Consumer root and state layout; Registry and containment; Catalog index document; Inference record document; Immutable inference event document`; full grammar `skills/lf-analytic-inference/references/state-document-v2.xsd`. Reject v1 layout, JSON state reader input, wrong namespace/root, attributes/unknown members, noncanonical bytes, invalid locator/containment, and wrong registry layout before write. |
| Analytic subdocuments | `catalog` members are the contract’s `schemaVersion`, `catalogId`, `technology`, `aliases`, `activeLimit`, `entries`; record sequence is `schemaVersion`, `inferenceId`, `revision`, `status`, `statement`, `applicability`, `investigation`, `provenance`, `lineage`, `snapshot`; event members include `schemaVersion`, `eventId`, source identity, inference identity/revision, stage, outcome, reason, agent capability, and cost. | `inference-contract.md` sections above and `state-document-v2.xsd` define exact child sequence/type. Reject any missing/reordered/unknown member, invalid `schemaVersion`, path-segment ID, ordering/uniqueness, cross-reference, or canonical-byte failure before write. JSON fixtures are not collectively legacy; task 3.1 classifies them individually. |
| Install scopes | JSON object with top-level keys `schema_version: 2`, `profiles`, `artifact_identity_policy`, `artifacts`; canonical artifact families are `agents`, `codex_agents`, `docs`, and `skills`. Schema 2 must not contain `artifacts.commands`. | `install-scopes.json`; `scripts/validate-install-scopes.py: validate_scope`. Reject schema 1, missing/unknown shape that violates schema-2 validation, `artifacts.commands`, cleanup flag `--cleanup-legacy-commands`, and unsafe parent symlink/real-file/consumer-owned target before mutation. |
| Navigator index | Consumer root is `docs/index.xml`; canonical XML index grammar is specified by `skills/lf-index-navigator/references/index-xml-contract.md`. The package-root `index.md` is unrelated and remains package content. | `skills/lf-index-navigator/SKILL.md: Execution` and `references/index-xml-contract.md`. Reject a consumer request with no `docs/index.xml` explicitly; do not read consumer `index.md` as a fallback. |
| Goose | There is no canonical root, version, layout, key or member after the approved deletion: Goose is an approved removal, not a projection to migrate. | Decision evidence: `../../analise.md`; execution scope: `../../tasks.md` task 5.1. Reject any residual package reference/import/install entry that names `goose/**` before publication validation; task 1.1 does not alter that tree. |

## Focused validation evidence

1. Source-map completeness: directed searches across the required validator,
   analytic contract, install scopes, templates and analysis located every
   requested family and its canonical version/layout.
2. Classification review: the validator and templates explicitly require
   schema 1 for WTR/session-evidence/execution-knowledge families, while the
   analytic contract explicitly says XML v2 is the only live layout and that
   its catalog/record/event logical schema remains 1. This rejects the invalid
   “all schema 1 is legacy” classification before any compatibility-removal
   write.

## Execution completion

```yaml
completion_record:
  task_id: task-1.1
  handoff_id: handoff-task-1.1-writer-20260720
  writer: technical-implementer
  terminal_status: completed
  changed_target_files:
    - planos/032-remove-legacy-compatibility/builds/fase1/canonical-contract-matrix.md
  validators:
    source-map-completeness: passed
    classification-review: passed
  human_validation: not-applicable
  approval:
    execution: approved
  evidence_ref: builds/fase1/canonical-contract-matrix.md#focused-validation-evidence
  next_destination: human technical-review
```
