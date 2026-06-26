---
title: "<task-id> - <task-title>"
type: loki-task
status: pending
phase: "<faseN>"
task_id: "<task-N.M>"
---

# <task-id> - <task-title>

## Objective

<Resultado concreto desta task.>

## Context

<Contexto minimo para outro agente executar sem memoria da conversa.>

## Requirements

- <requisito verificavel>

## Out Of Scope

- <limite explicito>

## Dependencies

- <task-id ou `none`>

## References

- <path, heading, linha, decisao ou `TODO: localizar`>

## Implementation Steps

1. <acao concreta>

## Validators

- <comando, parser, checklist, diff review ou `none` com justificativa>

## Observable Validation

<O que precisa ser observado, testado, revisado ou confirmado para considerar a task validada.>

## Human Loop

- Gate: <none | interview | approval | human-validation | technical-review>
- Required decision: <decisao ou `none`>

## Definition Of Done

- [ ] Requisitos atendidos.
- [ ] Dependencias respeitadas.
- [ ] Validadores executados ou justificativa registrada.
- [ ] Observable validation registrada.
- [ ] Fora de escopo preservado.

## Resume Notes

```yaml
loki_task_state:
  status: "pending"
  files_expected: []
  validations: []
  next_action: ""
  blocked_by: []
```
