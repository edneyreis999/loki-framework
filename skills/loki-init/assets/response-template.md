# loki-init — Resultado

## Status

<completed | audited | partial | needs-input | blocked | stopped>

## Resumo

<resultado ou estado atual; inclua o primeiro blocker material, se houver>

## Roots, modo e caller

- `consumer_project_root`: <path>
- `docs_root`: <path>
- `plan_root`: <path>
- `mode`: <full-init | refresh-docs | audit-only | agent-only:agent>
- `calling_workflow`: <loki-init | none em audit-only>
- `write_modes_used`: <init-bootstrap-cataloger | init-publication-batch | init-final-reconciliation | none>

## Artefatos

- Consumer docs: <path; created | updated | audited | blocked; materialization_ref; before_hash; after_hash; use none>
- Plan state/payloads: <path; created | updated | audited | blocked; hash/ref; use none>
- Ausentes ou divergentes: <path/ref, expected state e diagnostico; use none>

## Estado operacional

- `current_phase`: <value>
- `current_checkpoint`: <ref/path>
- `bootstrap_status`: <not-planned | planned | dispatched | write-applied | validated | committed | blocked>
- `final_reconciliation_status`: <not-planned | planned | dispatched | write-applied | validated | committed | blocked>
- `catalogador_active`: <run_id, mode e status | none>
- `completion_record_refs`: <refs e terminal status | none>
- `session_evidence_refs`: <refs e complete | partial | pointer-only | unavailable | unsupported; use none>

## Investigator handoffs

<agent; invocation/handoff IDs; status planned | invoked | continuing | complete | blocked | skipped; pending_requirement_ids; continuation_cursor; completion_record_ref; next destination; use none>

## Packet registry

<kind common | technology | selection | domain; packet_id; revision; hash; investigator; receipt state received | rejected; acceptance_status pending | accepted | rejected | superseded; materialization_status unbatched | batched | materialized | blocked; batch_id; continuation continue | complete | blocked; materialization_refs; blocker/supersedes_ref; use none>

## Publication batches

<todo batch aplicavel: batch_id; calling_workflow; write_mode; idempotency_key/hash; packet_refs; previous_checkpoint_ref; before_state_hash; lifecycle planned | dispatched | write-applied | validated | committed | blocked; catalogador_run_id; targets; before/after hashes; materialization_refs; blocker; recovery_action. Use none somente quando nenhum batch for aplicavel; blocked exige blocker + recovery_action e proibe completed>

## Coverage

<domain_id; requirement_id; required_depth map | deep; state pending | mapped | covered | not_found | not_applicable | deferred | blocked; evidence_packet_refs; materialization_refs; reason; use none>

## Publicacoes do catalogador

<operation bootstrap | publication-batch | final-reconciliation; calling_workflow loki-init; write_mode init-bootstrap-cataloger | init-publication-batch | init-final-reconciliation; operation/batch ID; lifecycle status; checkpoint; packet/ledger refs; targets; before/after hashes; materialization_refs; validators; use none>

## Evidencias e validators

<validator/check; passed | failed | inconclusive | not-applicable; evidence/ref; justificativa de N/A; completion record e session evidence ficam separados; use none>

## Gates e approvals

<gate/approval; granted | passed | pending | rejected; evidence/ref; decisao exata necessaria; use none>

## Riscos ou blockers

<packet orfao/nonterminal, todo batch nao committed incluindo blocked, coverage/depth gap, materializacao/hash ausente, reconciliation, handoff, gate, validator ou stop condition; path/ref, blocker e recovery_action; use none somente quando nenhum risco/blocker existir>

## Proxima acao e retomada

- `next_action`: <acao concreta>
- `owner`: <papel esperado>
- `resume_from`: <checkpoint/ref e primeiro estado nao terminal>
- `resume_condition`: <condicao verificavel>
- `next_recommended_command`: <command | none>

## loki_init_state

<estado resumido suficiente para outra LLM continuar sem memoria da conversa; referencie payloads grandes por path/hash, nao os duplique>
