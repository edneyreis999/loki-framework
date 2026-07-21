---
title: "task-3.1 - Classificar fixtures de inferência"
type: loki-task
status: completed
phase: fase3
task_id: task-3.1
---

# task-3.1 - Classificar fixtures de inferência

## Objective

Classificar cada JSON fixture de analytic inference como control plane atual, codec XML atual, legado removível ou rejeição a conservar.

## Context

JSON não implica legado: fixtures de purge, replay, isolation e codec continuam exercitando o layout XML v2.

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
escalation_reason: "deleção errada de fixture pode apagar cobertura do contrato atual"
```

## Requirements

- Mapear consumer-state, purge, replay, codec e catalog fixtures até seus scripts.
- Marcar delete/retain/convert-to-negative com evidência por arquivo.
- Bloquear qualquer deleção sem consumidor/validator identificado.

## Out Of Scope

- Editar schemas, scripts ou fixtures.

## Dependencies

- task-2.3

## References

- `analise.md#5. Analytic inference ainda possui leitor v1 executável`.
- `skills/lf-analytic-inference/references/fixtures/**`.
- `skills/lf-analytic-inference/scripts/*.py`.

## Implementation Steps

1. Rastrear referências de cada fixture.
2. Executar validators atuais para identificar cobertura observável.
3. Publicar classificação e delete-set exato para task-3.2.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: ["planos/032-remove-legacy-compatibility/builds/fase3/inference-fixture-classification.md"]
  allowed_writes: [planos/032-remove-legacy-compatibility/builds/fase3/inference-fixture-classification.md]
  scoped_write_domains: [task-local-evidence]
  required_skills: [lf-analytic-inference]
  validators: [fixture-reference-map, current-catalog-validator]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Cada fixture possui source consumer ou justificativa de ausência.
- `validate_catalog.py` continua verde sem mutação do catálogo.

## Observable Validation

O relatório contém um delete-set fechado e um retain-set fechado, sem classificação baseada apenas na extensão ou no número v1.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o delete-set; registrar `human-validation` como não aplicável porque não há runtime/consumer output.

## Definition Of Done

- [ ] Todas as fixtures classificadas.
- [ ] Delete-set e retain-set explícitos.
- [ ] Validator atual registrado.
- [ ] Nenhuma fonte alterada.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["planos/032-remove-legacy-compatibility/builds/fase3/inference-fixture-classification.md"]
  write_owner: technical-implementer
  target_files: ["planos/032-remove-legacy-compatibility/builds/fase3/inference-fixture-classification.md"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-3.1","coverage_digest":"sha256:608bb3641620fd8801d85034df54a6c61410c770402ca511f56298d1d91832c1","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:608bb3641620fd8801d85034df54a6c61410c770402ca511f56298d1d91832c1","reason":None,"next_action":"Classify fixtures after phase 2."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
