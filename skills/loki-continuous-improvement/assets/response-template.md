# loki-continuous-improvement — Resultado

## Status

<completed | proposed | applied | record-only | needs-input | blocked | stopped>

## Resumo

<resultado da análise, proposta ou promoção>

## Candidatos e classificação

<ids, type, severity, scope, destino, ação e status>

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
- Checks mecânicos: <comandos, resultados e evidência>
- Auditor: <agent, status externo, internal_status e configuração>
- Findings: <critério, evidência, impacto, resolução, confiança; use none>
- Iteração: <número>
- Gates invalidados: <true/false e quais>
- Próximo destino: <writer | technical-review | orchestrator | none>

`completed` ou `applied` neste destino requer auditor `approved`/`pass`, sem
findings, inconclusão, human review ou gate invalidado. Para
`needs-human-review`, use `blocked` com `block_reason: human_review_required`;
depois de correção ou decisão humana, declare rerun obrigatório do auditor.

## Handoffs, gates e approvals

<origem, destino, estado, evidência e controles concluídos/pendentes; não
confundir parecer automatizado do auditor com technical-review ou approval>

## Backlog

<itens record-only ou insuficientes e justificativa; use none>

## Riscos ou blockers

<lacunas, stop conditions e riscos residuais; use none>

## Próximos passos

<ação e owner esperado>

## Resume state

<candidatos, handoffs, gates, validators, status, promotion_execution e
condição para continuar>
