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

## Downstream Execution Profile

```yaml
downstream_execution_profile:
  model_class: "<frontier_reasoning|coding|generalist|long_context|fast_low_cost|specialist_generalist_human_like>"
  execution_effort: "<low|medium|high|xhigh>"
  escalation_reason: "<por que o plano exige esse effort>"
  recommended_handoffs:
    research: "<source-researcher|none>"
    context: "<execution-context-reader|none>"
    implementation: "<technical-implementer|none>"
    runtime_validation: "<runtime-qa|none>"
  validator_effort: "<low|medium|high>"
```

Planos gerados por `loki:generate-action-plan` sao transientes, mas devem usar
`execution_effort: high` por padrao. Ajustes task-level podem reduzir effort
para notas locais, validadores simples ou documentacao transiente.

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
