# Response — loki-human-decision-preflight

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: XML valido com raiz `command_response` e filhos `summary`, `status`,
  `artifacts`, `evidence`, `handoff`, `risks` e `next_steps`; nenhuma prosa fora
  da raiz.
- `Humano`: Markdown claro, acionavel e com no maximo 7.000 caracteres.
- `Both`: Markdown legivel por pessoa e retomavel por LLM, sem limite rigido.

## Intermediate Response

Enquanto houver `must_ask_now`, responda somente com status `needs-input`,
`ready_for_next_phase: false`, exatamente uma pergunta objetiva, evidencia e
resume state minimo. Para consentimento de pesquisa, inclua a query exata. Nao
preencha o template terminal nem apresente varias perguntas no mesmo turno.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, classificacoes,
respostas humanas, artefatos, evidencias/validators, handoffs,
gates/approvals, riscos, proximos passos e resume state. Preserve as quatro
categorias, a fonte/impacto/motivo de cada item, pendencias delegadas e o valor
de `ready_for_next_phase`.

Nao declare conclusao ou `ready_for_next_phase: true` com `must_ask_now` sem
resposta, validator falho, gate pendente, handoff aberto ou stop condition ativa.
