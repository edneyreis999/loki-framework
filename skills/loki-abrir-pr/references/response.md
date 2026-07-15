# Response — loki-abrir-pr

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: XML valido sob `command_response` com `summary`, `status`,
  `artifacts`, `evidence`, `handoff`, `risks` e `next_steps`, sem prosa externa.
- `Humano`: Markdown acionavel com no maximo 7.000 caracteres.
- `Both`: Markdown legivel e retomavel, sem limite rigido.

## Intermediate Response

Em approval/gate, mostre estado, base/head/remote, titulo e corpo completos
quando aplicavel, uma decisao solicitada, riscos e resume state. Nao use template
terminal nem declare PR criado.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
evidencias/validators, handoffs, gates/approvals, riscos, proximos passos e
resume state. Preserve PR criado ou proposta pronta, URL, base/head,
remote/provider, titulo, corpo, draft/ready, commits e validators.

Nao declare conclusao se push/PR nao foi confirmado, validator falhou,
approval/gate esta pendente ou handoff permanece aberto.
