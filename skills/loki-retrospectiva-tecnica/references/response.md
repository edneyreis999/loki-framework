# Response — loki-retrospectiva-tecnica

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `LLM`, use XML valido sob
`command_response` com `summary`, `status`, `artifacts`, `evidence`, `handoff`,
`risks` e `next_steps`, sem prosa externa. Para `Humano`, use Markdown acionavel
com no maximo 7.000 caracteres. Para `Both`, use Markdown legivel e retomavel,
sem limite rigido.

## Intermediate Response

Quando faltar evidencia, target ou gate, responda `needs-input` ou `blocked`
com uma decisao necessaria, evidencia atual e resume state. Nao materialize
retrospectiva terminal nem promova candidato duradouro.

## Outputs

- `retrospetivas/faseN/retrospectiva-faseN-<slug>.md`; ou
- `retrospetivas/faseN/<agent-name>-retrospectiva.md` quando o chamador fornecer
  esse `target_retrospective` exato.
- Mapa de atritos, caminho minimo, aprendizados e candidatos estruturados para
  melhoria continua, sem promocao aplicada.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
validacoes, decisoes, rastro material, atritos, aprendizados, candidatos,
handoffs, gates/approvals, riscos, proximos passos e resume state. Nao declare
conclusao com validator falho, gate pendente, handoff aberto, evidencia
contraditoria ou stop condition ativa.
