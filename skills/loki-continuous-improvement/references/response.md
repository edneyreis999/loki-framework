# Response — loki-continuous-improvement

## Response

Use este contrato para respostas intermediárias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: XML válido, estável e parseável, sem prosa fora de
  `command_response`, com `summary`, `status`, `artifacts`, `evidence`,
  `handoff`, `risks` e `next_steps`.
- `Humano`: Markdown claro, conciso e acionável, com no máximo 7.000
  caracteres; priorize resultado, decisão, risco e próximo passo.
- `Both`: Markdown legível por pessoa e recuperável por outra LLM, sem limite
  rígido.

Se outro consumidor for escolhido, aplique seu formato. Se estiver indefinido e
a escolha alterar o formato, resolva antes de responder.

## Intermediate Response

Para `interview`, `research-consent`, gate, approval ou stop condition, responda
com status, pergunta/decisão/query exata, evidências disponíveis, candidatos já
seguros, handoffs, riscos, próximo passo e resume state mínimo. Não materialize
resposta terminal nem declare promoção concluída.

Para candidato com `destination_scope: package`, inclua Writer/owner, arquivos
alterados e descobertos, checks mecânicos, status externo e interno do auditor,
`llm_artifact_profile` completo ou seu locator de evidência, partição de
fixtures, `llm_consumption_quality` completo ou seu locator de evidência,
configuração `llm-artifact-quality-v1`/`rubric-v2`/`prompt-v2`,
`profile_evidence`, `audit_evidence`, findings, confiança, `limitations`,
`second_family_calibration`, `iteration`, `invalidated_by_correction`,
`correction_replay_required`, `gates_invalidated` e `next_destination`. Projete
`needs-human-review` como `blocked` com
`block_reason: human_review_required`. Após correção ou decisão humana, declare
o rerun obrigatório do auditor; não o confunda com `technical-review` ou
`approval`.

Se o package target for human-only, reporte `not-applicable` com justificativa,
profile completo e dez skips; use `second_family_calibration: not-run`, registre
como limitation que revisão isolada e segunda família não são requeridas e não
alegue execução de fixtures irrelevantes. Projete o Auditor como external
`approved`, internal `not-applicable`, `block_reason: none`, com
`llm_consumption_quality.status: not-applicable`; os gates existentes continuam
obrigatórios. Para
qualquer `destination_scope` não-package, mantenha esta seção `none`, preserve a
resposta preexistente e não projete profile, fixtures ou parecer v2.

Projete `promotion_execution.auditor.internal_status` exatamente como
`pending | approved | blocked | needs-human-review | not-applicable | not-required`.
Não use os estados legados `pass`, `finding` ou `inconclusive` nesse campo;
detalhes de findings permanecem nos resultados do parecer.
Projete `second_family_calibration` exatamente como
`completed | unavailable | not-run`; para human-only use `not-run` com a
limitation já exigida.

Com intake de inferência ativo, inclua source locator, intake identity,
payload/source digests, resultado `accepted`, `replayed-no-op` ou
`conflict-blocked`, itens não contados novamente, policy ID/digest, reducer e
validator, snapshot reconstruído, componentes, denominadores, último evento,
freshness, score, elegibilidades e disposição `record-only`, `block` ou
`propose-promotion`. Conflito de ID/payload é `blocked` e não escolhe vencedor.
Inclua `package_root` e o `consumer_root` interno como campos distintos, a fonte
`canonical-pwd`, state root e registry/catalog locators. Para state proposal,
declare `destination_scope: consumer-operational-state`, writer
`technical-implementer`, targets root-bound e package writes proibidos.
Quando manutenção estiver em avaliação, diferencie
`reorganization_eligible` (informativo), `reorganization_proposed` (proposta
gated) e `reorganization_applied` (resultado validado), liste operações
`generalize|merge|deduplicate|rewrite|reorder` e reporte separadamente
`catalog_mutation_applied`. Similaridade semântica não altera nenhum estado.
Para purge, separe eligibility e proposal/dry-run; execution permanece
`not-run`, mutation false e reservada a um workflow separado de purge físico.
Registre a approval JIT exata
que seria exigida, sem consumi-la ou alegar exclusão.

## Terminal Response

Para `Both`, preencha integralmente `../assets/response-template.md`. Para
qualquer consumidor, comunique resumo, status, candidatos/classificação,
root-cause results, artefatos criados/alterados/analisados, evidence/digests,
validators, handoffs, gates/approvals, backlog, riscos, próximos passos/owner e
resume state.

Para intake especializado, acrescente ledger, replay/conflitos, snapshot/score,
elegibilidade, target exato com before/after/dry validation quando proposto,
Writer/auditor/gates e estado de mutação. Preserve status `unreviewed` até
promoção posterior realmente aprovada e validada. Reorganização pode aparecer
como proposta gated e somente como aplicada após targets/before-after/lineage
exatos, Writer, auditor, `technical-review`, approval e validators. Purge pode
aparecer somente como proposal/dry-run sem mutação; nunca reporte purge físico
nesta task. Nunca trate elegibilidade ou
similaridade como autoridade e sempre reporte `catalog_mutation_applied`.

Não declare conclusão com validator falho, gate/approval pendente, handoff
aberto ou stop condition ativa.

Para promoção de pacote, `completed` ou `applied` exige auditor externo
`approved`, `llm_consumption_quality.status: approved` quando aplicável,
ausência de finding/inconclusão/baixa confiança material/fixture omitido/skip
injustificado/bias falho/human review e nenhum gate invalidado. Correção invalida
o parecer anterior e exige replay completo antes de qualquer terminal. Finding
corrigível, human review ou gate invalidado é `blocked` e precisa de destino
executável; somente o cenário `approved`, ou human-only `not-applicable`
validado sujeito aos gates existentes, pode ser terminal.

## XML Shape For LLM

```xml
<command_response>
  <summary></summary>
  <status></status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <risks></risks>
  <next_steps></next_steps>
</command_response>
```

No XML, mantenha esse shape e serialize os dados de promoção dentro de
`artifacts`, `evidence`, `handoff`, `risks` e `next_steps`; não crie outro nó
raiz.
