# Response — loki-commit

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: XML valido sob `command_response` com `summary`, `status`,
  `artifacts`, `evidence`, `handoff`, `risks` e `next_steps`, sem prosa externa.
- `Humano`: Markdown acionavel com no maximo 7.000 caracteres.
- `Both`: Markdown legivel e retomavel, sem limite rigido.

## Intermediate Response

Antes de stage/commit, mostre branch, arquivos/pathspecs, diff resumido,
mensagem completa, riscos e approval solicitado. Nao use template terminal nem
afirme que indice ou commit foram alterados.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
evidencias/validators, handoffs, gates/approvals, riscos, proximos passos e
resume state. Preserve SHA curto, mensagem final, arquivos incluidos/excluidos,
validators e working tree remanescente.

Nao declare conclusao sem confirmacao do commit, com validator falho,
gate/approval pendente ou handoff aberto.
