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

## Execution Profile

```yaml
model_class: "<frontier_reasoning|coding|generalist|long_context|fast_low_cost|specialist_generalist_human_like>"
task_effort: "<low|medium|high|xhigh>"
documentation_profile: "<none|transient|durable|human_like>"
validator_effort: "<low|medium|high>"
recommended_handoffs:
  research: "<source-researcher|none>"
  context: "<execution-context-reader|none>"
  implementation: "<technical-implementer|none>"
  runtime_validation: "<runtime-qa|none>"
scoped_write_owner: "<orchestrator|agent-name|none>"
scoped_write_mode: "<none|task_scoped_writer>"
scoped_write_domains: []
escalation_reason: "<none ou motivo verificavel>"
```

Use `coding` com effort medio para implementacao normal. Use effort alto para
politica duravel, contratos/templates, analise tecnica, plano de acao, risco
arquitetural, evidencia conflitante ou validacao dificil.

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

## Scoped Write Plan

```yaml
scoped_write:
  owner: "<orchestrator|agent-name|none>"
  mode: "<none|task_scoped_writer>"
  target_files: []
  allowed_writes: []
  scoped_write_domains: []
  required_skills: []
  validators: []
  human_gates: []
```

Use `task_scoped_writer` quando a task atribuir escrita a um agente
especialista. Liste arquivos exatos em `target_files`; nao use diretorios
amplos quando a task puder nomear arquivos.

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
  write_owner: "<orchestrator|agent-name|none>"
  target_files: []
  validations: []
  next_action: ""
  blocked_by: []
```
