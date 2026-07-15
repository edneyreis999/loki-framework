# Response — loki-catalogar-docs

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: XML valido, estavel e parseavel com raiz `command_response` e filhos
  `summary`, `status`, `artifacts`, `evidence`, `handoff`, `risks` e
  `next_steps`; nao inclua prosa fora da raiz.
- `Humano`: Markdown claro, conciso e acionavel com no maximo 7.000 caracteres.
- `Both`: Markdown legivel por pessoa e estruturado para retomada por LLM, sem
  limite rigido de tamanho.

## Intermediate Response

Quando faltar input, approval, confirmation, gate ou decisao humana, responda
com status `needs-input`, `approval-required`, `validation-pending` ou
`blocked`. Comunique a pergunta ou acao unica necessaria, o motivo, a evidencia
disponivel e o resume state minimo. Nao preencha o template terminal nem
declare catalogacao concluida.

## Terminal Response

Preencha `../assets/response-template.md`. Comunique obrigatoriamente status,
resumo, diretorios catalogados/pulados e exclusoes, artefatos criados,
alterados, movidos ou removidos, evidencia e validators, handoffs do
`catalogador`, gates e approvals, falhas/lacunas/riscos, proximos passos com
owner e resume state. Resuma logs de handoff; nao reproduza output bruto longo.

Inclua a arvore e os batches apenas no nivel necessario para auditar ordem
bottom-up, disjuncao e consolidacao serial de `docs/index.xml`. Identifique
documentos obsoletos ou lacunas que ainda exijam decisao humana.

Nao declare conclusao se houver validator falho ou inconclusivo, gate ou
approval pendente, handoff aberto, conflito de owner ou stop condition ativa.
