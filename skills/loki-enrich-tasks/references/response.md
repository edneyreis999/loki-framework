# Response — loki-enrich-tasks

## Response

Use este contrato para respostas intermediárias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: responda em XML válido, estável e parseável, sem prosa fora da raiz
  `command_response`, com os filhos `summary`, `status`, `artifacts`,
  `evidence`, `handoff`, `risks` e `next_steps`.
- `Humano`: responda em Markdown claro, conciso e acionável, com no máximo
  7.000 caracteres. Priorize resultado, status, decisões necessárias, riscos e
  próximos passos.
- `Both`: responda em Markdown legível por pessoa e recuperável por outra LLM,
  sem limite rígido de tamanho. Use títulos e listas somente quando melhorarem
  leitura e recuperação.

Se outro consumidor for explicitamente escolhido, aplique o formato
correspondente. Se estiver indefinido e a escolha mudar o formato, resolva-o
antes de responder.

## Intermediate Response

Quando houver pergunta, gate ou stop condition, responda com status
`needs-input` ou `blocked`, decisão exata necessária, evidências disponíveis e
resume state mínimo. Não materialize resultado terminal nem declare conclusão.

## Terminal Response

Para o consumidor padrão `Both`, preencha integralmente
`../assets/response-template.md`. Para qualquer consumidor, comunique:

- resumo e status final ou atual;
- artefatos alterados, propostos ou analisados;
- evidências, validators e resultado do Research Gate;
- handoffs concluídos ou pendentes;
- gates e approvals concluídos ou pendentes;
- decisões e observações locais para retrospectiva;
- falhas, lacunas, backlog e riscos residuais;
- próximos passos, responsável esperado e resume state.

Não exponha nomes, links, datas ou conteúdo desnecessário das fontes internas
transitórias. Não declare conclusão enquanto houver gate/approval pendente,
validator falho, handoff aberto ou condição de parada ativa.

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
