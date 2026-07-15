---
name: lf-external-knowledge-extraction
description: Extrai observações e aprendizados candidatos de artefatos externos com rastreabilidade e não-forçamento, antes de qualquer auditoria de impacto no Loki.
---

# lf-external-knowledge-extraction

## Objetivo

Use esta skill na primeira fase de análises de conhecimento externo. Ela transforma artefatos externos em um handoff `external_extraction` sem decidir destino de mudança no Loki.

## Procedimento

1. Mapeie cada artefato externo: identificador, tipo, propósito aparente, relevância para Loki e limitações de contexto.
2. Extraia apenas observações que possam afetar o Loki.
3. Ignore detalhes específicos demais, exceto quando revelarem princípio transferível.
4. Separe claramente:
   - observação do artefato;
   - interpretação para Loki;
   - candidato de aprendizado;
   - critério de rejeição.
5. Classifique candidatos como `adotar`, `adaptar`, `rejeitar`, `ja contemplado`, `investigar` ou `sem aprendizado util`.
6. Aplique os critérios de não-forçamento. Não crie recomendações para preencher o relatório.
7. Registre força da evidência, risco, prioridade, custo, ganho esperado e ideia de validação.
8. Retorne handoff compacto para a fase de auditoria.

## O que procurar

- Clareza e economia de instrução.
- Tratamento de ambiguidade e incerteza.
- Critérios verificáveis de validação e rejeição.
- Estrutura de comandos, skills, agentes, templates ou relatórios.
- Lacunas, redundâncias, conflitos e padrões recorrentes.
- Exemplos positivos ou negativos transferíveis.

## Limites

- Não compare profundamente contra o Loki nesta fase.
- Não escolha destino duradouro.
- Não escreva mudanças.
- Não assuma cobertura do Loki que não foi fornecida ou lida.

## Handoff esperado

```yaml
external_extraction:
  external_artifacts: []
  observations: []
  candidate_learnings: []
  no_useful_learning:
    conclusion: false
    reason: ""
```
