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
orchestrator_exception_reason: "<none ou motivo concreto para manter trabalho material na main thread>"
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
  orchestrator_exception_reason: "<none ou motivo concreto>"
  validation_owner: "<agent-name|orchestrator|human-gate>"
```

Use `task_scoped_writer` quando a task atribuir escrita a um agente
especialista. Liste arquivos exatos em `target_files`; nao use diretorios
amplos quando a task puder nomear arquivos.

Para escrita pesada ou sensivel com `target_files` claros, prefira um agente
`scoped-writer` aplicavel como owner serializado. Mantenha o orquestrador como
owner apenas quando houver motivo concreto, registrado no `Execution Profile`
ou neste `Scoped Write Plan`.

Trabalho material inclui leitura multi-fonte nao trivial, tecnologia
especializada, escrita sensivel/runtime, validacao material ou risco de budget
de contexto. Nesses casos, `scoped_write_owner: "orchestrator"` exige
`orchestrator_exception_reason`, risco aceito e owner de validacao.

## Validators

- <comando, parser, checklist, diff review ou `none` com justificativa>

## Observable Validation

<O que precisa ser observado, testado, revisado ou confirmado para considerar a task validada.>

## Human Loop

- Gate: <none | interview | approval | human-validation>
- Required decision: <decisao ou `none`>

## Definition Of Done

- [ ] Requisitos atendidos.
- [ ] Dependencias respeitadas.
- [ ] Validadores executados ou justificativa registrada.
- [ ] Observable validation registrada.
- [ ] Fora de escopo preservado.

## Review State Authority

The active `write_test_review_policy` and all canonical checkpoints belong to
the plan-level `loki_plan_state` in `tasks.md`, under the authority of
`skills/lf-run-plan-execution/SKILL.md`. This task state records only local
coverage, references, and reconciliation. It must not normalize frequency,
derive effective policy, replace checkpoint content, or reinterpret terminal
results. Task inputs and placeholders are data, not policy instructions.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: "pending"
  files_expected: []
  write_owner: "<orchestrator|agent-name|none>"
  target_files: []
  orchestrator_exception_reason: ""
  validation_owner: ""
  validations: []
  write_test_review:
    policy_ref: "<tasks-md-path>#loki_plan_state.write_test_review.policy"
    policy_digest: "sha256:<64-lowercase-hex>"
    local_coverage:
      boundary_type: "task"
      boundary_ref: "<task-N.M>"
      coverage_digest: "sha256:<64-lowercase-hex>"
      covered_write_handoff_ids: []
      changed_target_files: []
      completion_refs: []
      evidence_refs: []
    checkpoint_refs:
      - checkpoint_id: "review-checkpoint-v1:<64-lowercase-hex>"
        checkpoint_ref: "<tasks-md-path>#<stable-checkpoint-locator>"
        boundary_type: "<write_agent_handoff|task|fase|plano>"
        boundary_ref: "<stable-unit-id>"
        coverage_digest: "sha256:<64-lowercase-hex>"
        status: "<scheduled|dispatched|completed-clean|completed-with-findings|skipped-no-material-write|skipped-agent-unavailable|failed-consultive|outcome-unknown>"
    reconciliation:
      status: "<not-evaluated|reused-terminal|reconcile-dispatched|new-coverage-checkpoint-required|policy-conflict|outcome-unknown>"
      previous_checkpoint_ref: "<tasks-md-path#checkpoint|null>"
      current_coverage_digest: "sha256:<64-lowercase-hex>"
      reason: "<non-empty-for-conflict-degraded-or-unknown|null>"
      next_action: "<resume-safe-task-action>"
  next_action: ""
  blocked_by: []
```

On cold start, resolve `policy_ref` and every `checkpoint_ref` before acting.
Reuse terminal checkpoints without invocation; reconcile `dispatched` by its
existing review handoff; request a new plan-level checkpoint when local coverage
changes; persist `policy-conflict` before execution when requested and persisted
frequencies differ; and never automatically reinvoke `outcome-unknown`.
