# Response — loki-deep-research

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `LLM`, responda em XML valido sob
`command_response` com `summary`, `status`, `artifacts`, `evidence`, `handoff`,
`risks` e `next_steps`, sem prosa externa. Para `Humano`, use Markdown acionavel
com no maximo 7.000 caracteres. Para `Both`, use Markdown legivel e retomavel,
sem limite rigido.

## Intermediate Response

Em entrevista/approval, mostre pergunta/escopo/plano/custo, uma decisao
necessaria, fontes previstas, riscos e resume state. Nao use template terminal
nem apresente conclusoes antes da pesquisa e validacao.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
evidencias/validators, handoffs, gates/approvals, riscos, proximos passos e
resume state. Preserve relatorio, metodologia/queries/filtros, achados por
classe, fontes com URLs/datas/tipo/credibilidade/uso, consenso, divergencias,
lacunas, assumptions e proximo workflow. Nao conclua com alegacao sem
fonte/classificacao, validator falho, gate pendente ou handoff aberto.
