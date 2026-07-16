# Response — loki-generate-action-plan

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `LLM`, use XML valido sob
`command_response` com `summary`, `status`, `artifacts`, `evidence`, `handoff`,
`risks` e `next_steps`, sem prosa externa. Para `Humano`, use Markdown acionavel
com no maximo 7.000 caracteres. Para `Both`, use Markdown legivel e retomavel,
sem limite rigido.

## Intermediate Response

Antes do approval do diretorio, responda `needs-approval` com o path candidato,
`derived_allowed_scope`, fonte/proveniencia, artefatos previstos, riscos e uma
unica decisao solicitada. Para fonte aprovada ou escopo derivado ausente,
ambiguo ou conflitante, responda `needs-input` com uma pergunta direcionada que
solicite a fonte aprovada contendo o escopo positivo inequivoco e o resume
state. Para outra lacuna bloqueante, responda `needs-input` com uma pergunta e
resume state. Nao
crie arquivos nem preencha o template terminal.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, escopo derivado e
proveniencia, diretorio,
artefatos, DAG, owners, validators, handoffs, gates/approvals, riscos, proximos
passos e resume state. Nao declare plano pronto com directory approval ausente,
validator falho, gate pendente, handoff aberto ou stop condition ativa.
