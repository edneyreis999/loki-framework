# Response — loki-knowledge-extraction-analysis

## Response

Use este contrato para respostas intermediárias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `LLM`, produza XML válido e parseável com
`summary`, `status`, `artifacts`, `evidence`, `handoff`, `risks` e `next_steps`.
Para `Humano`, use Markdown acionável com no máximo 7.000 caracteres. Para
`Both`, use Markdown legível por pessoa e recuperável por LLM, sem limite rígido.
Resolva o consumidor antes de responder se a escolha alterar o formato.

## Required Sixteen Sections

A resposta `Both` deve preencher exatamente as 16 seções preservadas em
`knowledge-extraction-analysis-contract.md`: identificação das instruções Loki;
seleção dos artefatos impactados; impacto em workflows; auditoria individual;
relatórios individuais; consolidação; resumo executivo; artefatos analisados;
resultado geral; aprendizados; pontos rejeitados; pontos já contemplados;
lacunas; conflitos; recomendações finais; e caso sem aprendizado útil. Aplique
também os valores, entry template e buckets de `output-contract.md`.

## Intermediate Response

Para interview, consentimento, gate, approval ou stop condition, responda com
status, pergunta/decisão/query exata, evidência disponível, handoffs, riscos,
próximo passo e resume state. Não materialize resposta terminal nem declare
análise concluída.

## Terminal Response

Preencha `../assets/response-template.md`. Comunique status, resumo, artefatos,
evidências, handoffs, riscos e próximos passos, além das 16 seções. Se nenhum
aprendizado confiável existir, use explicitamente a estrutura sem aprendizado
útil; não force conteúdo. Não conclua com validator, gate, handoff ou stop
condition pendente.

## XML Shape For LLM

```xml
<command_response><summary></summary><status></status><artifacts></artifacts><evidence></evidence><handoff></handoff><risks></risks><next_steps></next_steps></command_response>
```
