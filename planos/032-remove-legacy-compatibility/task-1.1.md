---
title: "task-1.1 - Confirmar matriz canônica e inventário de rejeições"
type: loki-task
status: completed
phase: fase1
task_id: task-1.1
---

# task-1.1 - Confirmar matriz canônica e inventário de rejeições

## Objective

Confirmar no source atual o único formato aceito por família e produzir a matriz que governará todas as remoções posteriores.

## Context

A análise prova que `schema_version=1` ainda é atual em algumas famílias. O corte não pode ser lexical nem global.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: high
documentation_profile: transient
validator_effort: high
recommended_handoffs: {research: source-researcher, context: execution-context-reader, implementation: technical-implementer, runtime_validation: none}
scoped_write_owner: technical-implementer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [task-local-evidence]
orchestrator_exception_reason: none
escalation_reason: "a matriz governa breaking changes em múltiplos contratos persistidos"
```

## Requirements

- Declarar versão, root, atributos e children canônicos por família.
- Classificar cada ocorrência como legado Loki, contrato atual, fallback operacional ou compatibilidade de domínio.
- Enumerar fixtures negativas e mensagem/stop-before-write esperados.
- Registrar lacunas materiais sem decidir por matching lexical.

## Out Of Scope

- Alterar qualquer arquivo do pacote ou consumidor.

## Dependencies

- none

## References

- `demanda.md#Critérios de aceitação`.
- `analise.md#Achados materiais`.
- `scripts/validate-agentic-run-state.py`.
- `skills/lf-analytic-inference/references/inference-contract.md`.
- `install-scopes.json`.

## Implementation Steps

1. Reexecutar scans focados e reconciliar resultados com a análise.
2. Montar a matriz por artifact family e o mapa de rejeições.
3. Submeter ambiguidades de fixture e versão ao technical review.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: ["planos/032-remove-legacy-compatibility/builds/fase1/canonical-contract-matrix.md"]
  allowed_writes: [planos/032-remove-legacy-compatibility/builds/fase1/canonical-contract-matrix.md]
  scoped_write_domains: [task-local-evidence]
  required_skills: []
  validators: [source-map-completeness, classification-review]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Toda família encontrada possui exatamente um formato canônico ou blocker explícito.
- Toda ocorrência relevante possui classificação e source ref.
- Nenhum path de consumidor ou `.loki/**` foi escrito.

## Observable Validation

`builds/fase1/canonical-contract-matrix.md` permite implementar cada rejeição sem inferir versão, shape ou exceção pela conversa.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar a matriz; registrar `human-validation` como não aplicável porque não há runtime/consumer output.

## Definition Of Done

- [x] Matriz e mapa de rejeições completos.
- [x] Casos atuais schema 1 preservados explicitamente.
- [x] Technical review registrado.
- [x] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`; esta task registra somente cobertura local.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["planos/032-remove-legacy-compatibility/builds/fase1/canonical-contract-matrix.md"]
  write_owner: technical-implementer
  target_files: ["planos/032-remove-legacy-compatibility/builds/fase1/canonical-contract-matrix.md"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations:
    - "source-map-completeness: passed"
    - "classification-review: passed"
    - "write-test-review: completed-clean (raw no_findings)"
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage:
      boundary_type: task
      boundary_ref: task-1.1
      coverage_digest: "sha256:21774c9634857ca04862934c43b3def34177351f14f3852c9b6dd337b8513b4b"
      covered_write_handoff_ids: ["handoff-task-1.1-writer-20260720"]
      changed_target_files: ["planos/032-remove-legacy-compatibility/builds/fase1/canonical-contract-matrix.md"]
      completion_refs: ["builds/fase1/canonical-contract-matrix.md#execution-completion"]
      evidence_refs: ["builds/fase1/canonical-contract-matrix.md#focused-validation-evidence"]
    checkpoint_refs:
      - checkpoint_id: "review-checkpoint-v1:d54d2a45ab162df2d8f92d1a7443c661f3abec9e37b42f6c0cdd9d6679623545"
        checkpoint_ref: "tasks.md#loki_plan_state.write_test_review.checkpoints[0]"
        boundary_type: task
        boundary_ref: task-1.1
        coverage_digest: "sha256:21774c9634857ca04862934c43b3def34177351f14f3852c9b6dd337b8513b4b"
        status: completed-clean
    reconciliation:
      status: reused-terminal
      previous_checkpoint_ref: "tasks.md#loki_plan_state.write_test_review.checkpoints[0]"
      current_coverage_digest: "sha256:21774c9634857ca04862934c43b3def34177351f14f3852c9b6dd337b8513b4b"
      reason: null
      next_action: "Await required human technical-review."
  technical_review: "approved-in-chat-2026-07-21"
  next_action: "Task completed; release task-1.2."
  blocked_by: []
```
