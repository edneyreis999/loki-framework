---
title: "<plan-title>"
type: loki-action-plan
status: draft
created: "<YYYY-MM-DD>"
---

# Plano de Acao - <plan-title>

## Overview

<3-5 linhas sobre objetivo, origem e resultado esperado.>

## Sources

- <path ou decisao usada como fonte>

## Scope

- <superficie ou comportamento permitido>

## Out Of Scope

- <superficie ou comportamento proibido>

## Assumptions

- <premissa verificavel>

## Open Questions

- <pergunta pendente ou `none`>

## Phases

### Fase 1 - <phase-title>

**Objective:** <resultado da fase>
**Observable Validation:** <o que humano, teste, log, output ou runtime deve demonstrar>

| Task | Title | Dependencies | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- |
| task-1.1 | <task-title> | none | 2-4h | <none/interview/approval/human-validation> | <validator> | pending |

## Execution Order

1. task-1.1

## Human Loops

- <gate, fase/task, decisao necessaria>

## Resume State

```yaml
loki_plan_state:
  current_phase: "fase1"
  current_task: "task-1.1"
  status: "pending"
  next_action: ""
  blocked_by: []
```
