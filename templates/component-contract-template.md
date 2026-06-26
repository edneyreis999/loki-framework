---
name: "<component-name>"
type: "<agent | skill | dependency | template>"
status: draft
---

# <component-name>

## Purpose

<Responsabilidade do componente.>

## When To Use

<Gatilhos para usar o componente.>

## Inputs

- <Entrada exigida>

## Outputs

- <Saida esperada>

## Allowed Writes

- <Se nao puder escrever, declarar `none` ou `proposal-only`.>

## Forbidden Writes

- <Superficies proibidas.>

## Gates

- <Gates obrigatorios.>

## Dependencies

- <Skills, commands, agents, docs ou templates relacionados.>

## Packaging Checks

- <Se o componente fizer parte do pacote, declarar path final, impacto no manifest, docs afetados e validacoes objetivas.>

## Response Format

```yaml
component_response:
  summary: ""
  evidence: []
  risks: []
  recommended_next_step: ""
```
