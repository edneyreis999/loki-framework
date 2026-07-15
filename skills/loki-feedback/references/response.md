# Response — loki-feedback

## Response

Use este contrato para respostas intermediarias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: XML valido com raiz `command_response` e filhos `summary`, `status`,
  `artifacts`, `evidence`, `handoff`, `risks` e `next_steps`; nenhuma prosa fora
  da raiz.
- `Humano`: Markdown acionavel com no maximo 7.000 caracteres.
- `Both`: Markdown legivel por pessoa e retomavel por LLM, sem limite rigido.

## Intermediate Response

Enquanto houver entrevista/gate, responda apenas com status `needs-input`, uma
unica pergunta objetiva ou consentimento com query exata, evidencias atuais e
resume state minimo. Nao preencha o template terminal nem conclua prematuramente.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
evidencias/validators, handoffs, gates/approvals, riscos, proximos passos e
resume state. Preserve diagnostico; perguntas/respostas; proposta sem escrita;
estado do research gate; e separacao de fatos, inferencias, hipoteses e lacunas.

Nao declare conclusao enquanto houver duvida critica, gate/validator pendente,
handoff aberto ou stop condition ativa.
