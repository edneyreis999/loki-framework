# Response — loki-criar-branch

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `LLM`, responda em XML valido sob
`command_response` com `summary`, `status`, `artifacts`, `evidence`, `handoff`,
`risks` e `next_steps`, sem prosa externa. Para `Humano`, use Markdown acionavel
com no maximo 7.000 caracteres. Para `Both`, use Markdown legivel e retomavel,
sem limite rigido.

## Intermediate Response

Antes de criar/trocar/stash, mostre estado, branch atual, base, nome proposto,
mudancas locais, comando e uma decisao solicitada. Nao use template terminal nem
declare branch criada.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
evidencias/validators, handoffs, gates/approvals, riscos, proximos passos e
resume state. Preserve branch anterior/nova, base, stash/restauracao, decisoes e
validators; confirme que nao houve commit/push/PR. Nao conclua com validator
falho, gate pendente, branch nao confirmada ou handoff aberto.
