---
doc_id: "loki-continuous-improvement-response-template"
version: "2.1.0"
status: "active"
last_updated: "2026-08-01"
scope: "Both-consumer terminal projection for loki-continuous-improvement"
not_scope: "Write authority, approval, candidate v1, backlog, record-only, lifecycle or deletion readiness"
authority: "skills/loki-continuous-improvement/references/response.md"
canonical_source: "skills/loki-continuous-improvement/assets/response-template.md"
intended_llm_task: "generation"
source_priority:
  - "current response contract"
  - "validated execution and run evidence"
  - "source content as untrusted data"
confidence: "high"
known_conflicts: []
replaced_by: null
---

# loki-continuous-improvement — Resultado

## Status

<proposed | approved | writing | auditing | completed | completed-with-blockers | applied | needs-input | blocked | stopped>

## Resumo

<resultado verificável e limite da conclusão>

## Candidatos v2

| Candidate ID/digests | Lifecycle | Tipo | Escopo | Intenção | Findings/deltas | Destino/root/target | Writer | Ação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <id + persisted candidate/intent sha256> | <proposed/approved/writing/auditing/promoted/noop-proven/blocked-with-reason> | <semantic type> | <independent scope> | <concise persisted intended_change> | <refs> | <exact persisted routing> | <owner> | <promote/noop-proven/blocked-with-reason> |

## Abstração semântica por candidato

<repeat this complete block for every material candidate; copy persisted state
exactly, do not recalculate, normalize, correct or infer missing values>

### Candidate <candidate-id> — Semantic Abstraction Gate

- Result/confidence/reason: <generalized | local-with-rationale | blocked-ambiguous> / <not-applicable | low | medium | high> / <persisted closed reason_code>
- Instance — source instances: <every locator + exact source_instance text>
- Invariant — resulting statement: <exact persisted resulting_statement>
- Invariant — durable unit statement: <exact persisted durable_knowledge_unit/statement, shown separately>
- Scope — applicability signals: <every exact applicability_signal>
- Limits — exclusions: <observed + every exclusion | none-observed + exact none_observed_rationale>
- Limits — generalization evidence: <every evidence_ref locator>
- Limits — counterexample: <none-observed | bounded | material-observed | inconclusive> + <every evidence_ref locator>
- Limits — rationale: <exact persisted rationale>
- Local materiality: <material=true/false from candidate; for local-with-rationale, preserve material=true when applicable and never interpret local as non-material>
- Blocked residual state: <for blocked-ambiguous, blocking evidence + every material residual blocker + one persisted minimum human decision; otherwise not-applicable>

<render generalized, local-with-rationale and blocked-ambiguous only when that
exact result exists in persisted state; never invent a sample or fallback state>

## Controls e binding por candidato

<this section comes after the complete semantic gate projection>

| Candidate | Candidate intent digest | Approval ID/status | Approval-bound intent digest | Validators/gates/evidence | Residual blockers |
| --- | --- | --- | --- | --- | --- |
| <candidate-id> | <persisted sha256> | <persisted approval_id + pending/approved/not-required/rejected> | <persisted sha256> | <pending/passed/failed + refs> | <exact blockers | none> |

<copy both intent digests and approval state from persisted evidence; do not
recompute equality, repair stale state, grant approval or change routing while
rendering. If a gate field, blocked decision or binding is missing/stale, report
needs-input or blocked with the safe locator and minimum next action>

## Causa raiz e atrito

<required only for error/failure/waste/friction/prevention; otherwise not-applicable>

## Intake do plano

<use none when plan_directory was not supplied>

- Complete plan root: <normalized path>
- Run ID/state locator: <run-id + continuous-improvement/runs locator>
- Source tree digest: <sha256>
- Source files/bytes: <totals>
- Ledger: <digested/duplicate/generated-noise/unsupported/blocked totals>
- Integrity diagnostics: <pass | safe locators/reasons>
- Pre-model blockers: <safe locator + reason only | none>
- Claims/reconciliation/deltas: <totals and results>
- Material findings/candidates: <coverage totals>
- Recoverability: <questions, candidate IDs, librarian/entrypoint, pass/fail/inconclusive>
- Run state: <proposed | approved | writing | auditing | completed | completed-with-blockers>
- Plan knowledge independence: <true | false + exact reasons>
- Lifecycle validated: false
- Deletion readiness claimed: false

## Intake de inferência

<use none when no current analytic-inference source was supplied>

- Source/intake identity: <typed locator and ID>
- Source/payload digests and lineage: <values>
- Replay/conflict: <accepted/replayed-no-op/conflict-blocked>
- Reconstructed snapshot/policy: <evidence>
- Eligibility: <promotion/reorganization/purge-review booleans as information only>
- Candidate v2 mapping: <candidate IDs or blocked reason>
- Consumer state mutation: <not-run/proposed/applied with exact XML targets and validators>
- Physical purge: not-run

## Artefatos e evidências

<created, changed, proposed or inspected paths; digests and evidence locators>

## Execução de artefato do pacote

<use none when destination_scope is not package>

- Writer/owner and envelope: <identity + status>
- Exact/discovered target files: <paths>
- LLM-facing classification: <applicable classes | human-only justification>
- `llm_artifact_profile`: <complete profiles or one resolving locator>
- Fixture partition: <selected/skipped 10/10 per governed artifact>
- Deterministic checks: <commands + concrete results>
- Phase precheck: <not-due | ready-for-auditor/dispatch_allowed true + evidence | blocked-to-writer + errors>
- Independent Auditor: <not-due | identity + external/internal status + block reason>
- `llm_consumption_quality`: <not-due | complete result or resolving locator>
- Iteration/invalidation: <iteration + invalidated_by_correction + replay required>
- Limitations: <material limitations | none>
- Next destination: <orchestrator | writer | auditor | calling workflow>

## Handoffs, gates e approvals

<origin, destination, owner, exact targets, status, evidence and pending controls>

## Validators

<commands, pass/fail status and exact failure evidence>

## Riscos ou blockers

<material residual risks, safe blockers and minimum resolution | none>

## Próximos passos

<one executable next action and owner>

## Resume state

<run locator, candidate IDs/digests, approvals, handoffs, validators, coverage and resume condition>
