# Response — loki-self-healing

## Response

Use este contrato para respostas intermediárias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `Humano`, responda em Markdown acionável com
no máximo 7.000 caracteres. Para `LLM`, use XML válido com `summary`, `status`,
`artifacts`, `evidence`, `handoff`, `risks`, `next_steps`. Para `Both`, use
Markdown legível por pessoa e recuperável por LLM, sem limite rígido. Resolva a
escolha antes de responder quando ela alterar o formato.

## Intermediate Response

Em stop/gate, informe status, pergunta/decisão, escopo e evidência já seguros,
handoffs, riscos, próxima ação e resume state; não declare correção concluída.

## Terminal Response

Preencha `../assets/response-template.md`: escopo, fontes, arquivos, install
scopes, achados, correções, alterações, validators, não alterados, handoffs,
riscos e próximo passo de revisar o diff e stagear manualmente. Inclua score
24/24 por command bundle. Não conclua com validator, gate, handoff ou stop aberto.

## XML Shape For LLM

```xml
<command_response><summary></summary><status></status><artifacts></artifacts><evidence></evidence><handoff></handoff><risks></risks><next_steps></next_steps></command_response>
```
