# loki-continuous-improvement — Resultado

## Status

<completed | proposed | applied | record-only | needs-input | blocked | stopped>

## Resumo

<resultado da análise, proposta ou promoção>

## Candidatos e classificação

<ids, type, severity, scope, destino, ação e status>

## Intake de inferência

<use none quando a ramificação especializada não estiver ativa>

- Package root: <canonical package root | not-applicable>
- Consumer root/source: <canonical consumer root + canonical-pwd>
- Consumer root source: canonical-pwd
- State root: <consumer-root>/.loki/analytic-inference/v2
- Live serialization/layout: XML v2 (`registry.xml`, `index.xml`, `rev-N.xml`, event `.xml`)
- Registry/catalog locators: <root-bound locators | absent/empty>
- Destination scope: <consumer-operational-state | other classified scope>

| Source type/locator | Intake identity | Source/payload digest | Status | Capture/lineage/provenance | Counted |
| --- | --- | --- | --- | --- | --- |
| <deep-analysis/retrospective + locator> | <event:event_id ou candidate:candidate_id> | <digests> | <accepted/replayed-no-op/conflict-blocked> | <refs> | <yes/no + reason> |

- Replay no-op: <IDs e confirmação de nenhuma dupla contagem | none>
- Conflitos: <ID, payloads/provenances e blocker | none>
- Itens rejeitados no intake: <ID + schema/locator/status/lineage/provenance reason | none>

## Reconciliação, snapshot e elegibilidade

- Policy ID/digest: <analytic-inference-policy-v1 + digest verificado>
- Reducer/validator: <comando/interface, status e diagnostics>
- Snapshot reconstruído: <algorithm, as_of_event, freshness>
- Componentes: <selected, investigated, validated, rejected, material findings, tasks helped, false positives, repeated evidence, stale>
- Denominadores: <unique_events e outros observados>
- Score: <valor + pesos aprovados; selected weight 0>
- Promotion eligible (`score >= 12`): <true/false>
- Reorganization eligible (`score <= 2`): <true/false; informativo>
- Purge-review eligible (`unprotected && score <= -4`): <true/false; protected sempre false; informativo>
- Disposição: <record-only | block | propose-promotion>
- Candidate status: <unreviewed>

## Proposta de promoção de inferência

<use none para record-only/block ou quando a ramificação estiver inativa>

- Targets exatos: <index e record>
- Before/after: <diff esperado>
- Dry validation: <index-record parity, reducer/snapshot e resultados>
- Writer exclusivo de state: <technical-implementer + task_scoped_writer envelope>
- Package writer receives `.loki`: false
- State writer receives package contracts/docs: false
- State validation reviewer: <runtime-qa read-only + status | none>
- Controles antes de durable write: <approval vinculado + fontes + validators>
- Catalog mutation applied: <false for proposal/dry-run; true only after exact gates, index-last write and post-validation>
- Approved lifecycle result: <not-run | index-last applied + post-validation | blocked + exact residue>

## Reorganização de inferência

- Reorganization eligible: <true/false; somente informativo>
- Reorganization proposed: <true/false>
- Allowed operation: <generalize | merge | deduplicate | rewrite | reorder | none>
- Operation ID e targets exatos: <IDs/revisions/paths | none>
- Before/after e lineage: <estado preservado | none>
- Protected/validated knowledge preservation: <validated result | pending | blocked | none>
- Writer: <technical-implementer state writer | none>
- Approval vinculado: <status e fontes | none>
- Deterministic validators: <schema/identity/lineage/parity/snapshot + results | none>
- Reorganization applied: <true somente após todos os controles; senão false>
- Commit point/result: <not-run | technology index published last | blocked + before/after-commit residue>
- Catalog mutation applied: <igual ao efeito observado desta operação; false para eligibility/proposal>
- Semantic similarity used as identity/authority: false

## Purge físico de inferência

- Purge-review eligible: <true/false; necessário, nunca suficiente>
- Purge proposed: <true/false>
- Dry-run: <not-run | valid + operation ID/manifest/digest | blocked + reason>
- Exact JIT approval: <missing | blocked | valid + source/issued_at/expiry/freshness | consumed>
- Execution: <not-run; physical purge reserved to a separate physical-purge workflow>
- External reports/retrospectives/evidence/approval targeted: false
- Semantic similarity used as authority: false
- Catalog mutation applied: false

## Causa raiz e execution friction

<required/status, fontes, causa, regra fortalecida, atritos e minimum next path>

## Artefatos

<criados, alterados, propostos ou analisados; use none>

## Evidências e validators

<fontes, digests, capability preflight, checks e resultados>

## Execução de artefato do pacote

<use none quando destination_scope não for package>

- Writer/owner: <agent e envelope_status>
- Arquivos: <target_files e discovered_target_files>
- Classificação LLM-facing: <applicable + classes | not-applicable + justificativa human-only | none para destino não-package>
- `llm_artifact_profile`: <objeto completo ou evidence locator; inclua selected/skipped partition 10/10>
- Contrato de qualidade: <contract_version llm-artifact-quality-v1 + rubric-v2 + prompt-v2 | not-loaded>
- Checks mecânicos: <comandos, resultados e evidência>
- Auditor: <agent, `status: pending | approved | blocked | not-required`, `internal_status: pending | approved | blocked | needs-human-review | not-applicable | not-required`, `block_reason: finding_open | validation_inconclusive | low_material_confidence | fixture_omitted | bias_check_failed | human_review_required | handoff_incomplete | none` e configuração>
- `llm_consumption_quality`: <objeto completo ou evidence locator; use `none` exclusivamente quando `destination_scope` não for package; package human-only exige parecer independente completo com `status: not-applicable` validado>
- `profile_evidence` / `audit_evidence`: <locators | none>
- `limitations`: <limitações materiais | none>
- `second_family_calibration`: <completed | unavailable | not-run>
- Findings: <critério, evidência, impacto, resolução, confiança; use none>
- `iteration`: <número>
- `invalidated_by_correction` / `correction_replay_required`: <true/false + estado do replay completo>
- `gates_invalidated`: <true/false e quais>
- `next_destination`: <writer | orchestrator | none>

`completed` ou `applied` neste destino é válido somente em um destes casos:

- package aplicável: parecer independente `approved`, sem findings,
  inconclusão, baixa confiança material, fixture aplicável omitido, skip
  injustificado, bias falho, human review ou gate invalidado;
- package human-only: profile com `not-applicable` justificado e dez skips mais
  `llm_consumption_quality.status: not-applicable` validado pelo Auditor
  independente, `second_family_calibration: not-run` e limitation explícita de
  que revisão isolada e segunda família não são requeridas, sempre sujeito aos
  gates existentes e sem fixtures irrelevantes; projete external `approved`,
  internal `not-applicable` e `block_reason: none`.

Para `needs-human-review`, use `blocked` com
`block_reason: human_review_required`; depois de correção ou decisão humana,
declare rerun completo obrigatório do Auditor. Use
`llm_consumption_quality: none` exclusivamente para destino não-package; nesse
caso use `none` nesta seção e preserve routing, owner, validators, gates e
resposta existentes.

## Handoffs, gates e approvals

<origem, destino, estado, evidência e controles concluídos/pendentes; não
confundir parecer automatizado do auditor com approval>

## Backlog

<itens record-only ou insuficientes e justificativa; use none>

## Riscos ou blockers

<lacunas, stop conditions e riscos residuais; use none>

## Próximos passos

<ação e owner esperado>

## Resume state

<candidatos, handoffs, gates, validators, status, promotion_execution e
condição para continuar>
