---
title: "task-3.2 - Remover reader e operação de migração v1"
type: loki-task
status: completed
phase: fase3
task_id: task-3.2
---

# task-3.2 - Remover reader e operação de migração v1

## Objective

Eliminar do runtime local o reader JSON v1, `migration-dry-run`, schemas legados e fixtures aprovadas para remoção.

## Context

`manage_consumer_state.py` contém validação e proposta copy-only completa para `.loki/analytic-inference/v1/**`.

## Execution Profile

```yaml
model_class: coding
task_effort: high
documentation_profile: durable
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: technical-implementer, runtime_validation: none}
scoped_write_owner: technical-implementer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [implementation-code, validators, package-skill-contracts]
orchestrator_exception_reason: none
escalation_reason: "remoção de parser, CLI e schemas com preservação do XML v2"
```

## Requirements

- Remover `LEGACY_STATE_PARTS`, parser, validators e proposal builders v1.
- Remover a opção `migration-dry-run` e flags exclusivas da operação.
- Excluir somente schemas/fixtures aprovados em task-3.1.
- Adicionar rejeição explícita para operação e layout antigos.

## Out Of Scope

- Alterar registry/index/records/events XML v2, policy v1 atual ou `.loki/**` real.

## Dependencies

- task-3.1

## References

- `builds/fase3/inference-fixture-classification.md`.
- `skills/lf-analytic-inference/scripts/manage_consumer_state.py`.
- `skills/lf-analytic-inference/references/state-document-v2.xsd`.

## Implementation Steps

1. Aplicar o delete-set aprovado e remover o código de leitura/cópia.
2. Implementar negativas para layout/operation antigos.
3. Rodar validators XML, lifecycle, purge, replay e isolation atuais.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: &task_targets
    - skills/lf-analytic-inference/scripts/manage_consumer_state.py
    - skills/lf-analytic-inference/references/registry-schema.json
    - skills/lf-analytic-inference/references/catalog-schema.json
    - skills/lf-analytic-inference/references/event-schema.json
    - skills/lf-analytic-inference/references/fixtures/catalog-empty.json
    - skills/lf-analytic-inference/references/fixtures/catalog-invalid.json
    - skills/lf-analytic-inference/references/fixtures/catalog-limit.json
  allowed_writes: *task_targets
  scoped_write_domains: [implementation-code, validators, package-skill-contracts]
  required_skills: [lf-analytic-inference]
  validators: [python-compile, catalog-validation, current-fixture-suite, migration-negative]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `python3 -m py_compile skills/lf-analytic-inference/scripts/*.py`
- `python3 skills/lf-analytic-inference/scripts/validate_catalog.py --technology loki-framework --policy skills/lf-analytic-inference/references/policy-v1.json`
- Current XML codec/control-plane fixtures passam; migration CLI/layout falham.

## Observable Validation

Nenhum código alcançável lê v1 JSON e o estado XML v2 atual permanece válido e imutável.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write/delete-set; registrar `human-validation` como não aplicável porque consumer state não será exercitado.

## Definition Of Done

- [ ] Reader/CLI v1 removidos.
- [ ] Somente fixtures aprovadas removidas/convertidas.
- [ ] XML v2 validado.
- [ ] `.loki/**` permaneceu intocado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["skills/lf-analytic-inference/scripts/manage_consumer_state.py"]
  write_owner: technical-implementer
  target_files: ["skills/lf-analytic-inference/scripts/manage_consumer_state.py", "skills/lf-analytic-inference/references/registry-schema.json", "skills/lf-analytic-inference/references/catalog-schema.json", "skills/lf-analytic-inference/references/event-schema.json", "skills/lf-analytic-inference/references/fixtures/catalog-empty.json", "skills/lf-analytic-inference/references/fixtures/catalog-invalid.json", "skills/lf-analytic-inference/references/fixtures/catalog-limit.json"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-3.2","coverage_digest":"sha256:69ec0b2e45b875017532e29cab6a744dba3f7bdf5c2e93a92eab735a6d25944e","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:69ec0b2e45b875017532e29cab6a744dba3f7bdf5c2e93a92eab735a6d25944e","reason":None,"next_action":"Execute the approved fixture/code cut."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
