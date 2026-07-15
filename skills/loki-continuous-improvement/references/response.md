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

## Terminal Response

Para `Both`, preencha integralmente `../assets/response-template.md`. Para
qualquer consumidor, comunique resumo, status, candidatos/classificação,
root-cause results, artefatos criados/alterados/analisados, evidence/digests,
validators, handoffs, gates/approvals, backlog, riscos, próximos passos/owner e
resume state.

Não declare conclusão com validator falho, gate/approval pendente, handoff
aberto ou stop condition ativa.

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
