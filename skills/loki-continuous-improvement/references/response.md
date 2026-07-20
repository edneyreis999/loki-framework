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
findings, confiança, iteração, gates invalidados e próximo destino. Projete
`needs-human-review` como `blocked` com
`block_reason: human_review_required`. Após correção ou decisão humana, declare
o rerun obrigatório do auditor; não o confunda com `technical-review` ou
`approval`.

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
`approved`, interno `pass`, ausência de finding/inconclusão/human review e
nenhum gate invalidado. Finding corrigível, human review ou gate invalidado é
`blocked` e precisa de destino executável; somente o cenário `approved` pode
ser terminal.

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
