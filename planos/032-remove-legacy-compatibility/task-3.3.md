---
title: "task-3.3 - Remover contratos e roteamentos de copy migration"
type: loki-task
status: completed
phase: fase3
task_id: task-3.3
---

# task-3.3 - Remover contratos e roteamentos de copy migration

## Objective

Remover de skills, commands e docs operacionais todas as instruções que ainda tratam v1 JSON como fonte de migração.

## Context

Após task-3.2, qualquer instrução de inventory/copy v1 vira referência quebrada e contrato contraditório.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: high
documentation_profile: durable
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: framework-artifact-writer, runtime_validation: none}
scoped_write_owner: framework-artifact-writer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [package-skill-contracts, package-command-contracts, package-documentation]
orchestrator_exception_reason: none
escalation_reason: "contratos normativos multi-command devem convergir com o runtime removido"
```

## Requirements

- Remover copy migration de `lf-analytic-inference` e seus callers.
- Preservar policy-v1 atual, XML v2 e regras de zero catalog mutation.
- Atualizar docs que descrevem layout e lifecycle atuais.

## Out Of Scope

- Mudar scoring, ranking, lifecycle ou continuous-improvement fora da remoção v1.

## Dependencies

- task-3.2

## References

- `analise.md#5. Analytic inference ainda possui leitor v1 executável`.
- `skills/lf-analytic-inference/SKILL.md`.
- `skills/loki-deep-analysis/references/execution.md`.
- `docs/loki-learning-workflow.md`.

## Implementation Steps

1. Remover contratos v1/copy-only do core.
2. Alinhar deep analysis, continuous improvement e retrospectiva.
3. Atualizar docs e executar scan focado de referências.

## Scoped Write Plan

```yaml
scoped_write:
  owner: framework-artifact-writer
  mode: task_scoped_writer
  target_files: &task_targets
    - skills/lf-analytic-inference/SKILL.md
    - skills/lf-analytic-inference/references/inference-contract.md
    - skills/loki-deep-analysis/SKILL.md
    - skills/loki-deep-analysis/references/execution.md
    - skills/loki-continuous-improvement/SKILL.md
    - skills/loki-continuous-improvement/references/execution.md
    - skills/loki-retrospectiva-tecnica/references/execution.md
    - docs/loki-learning-workflow.md
    - docs/loki-plan-execution-workflow.md
    - docs/operational-inventory.md
    - docs/usage-guide.md
  allowed_writes: *task_targets
  scoped_write_domains: [package-skill-contracts, package-command-contracts, package-documentation]
  required_skills: [lf-analytic-inference, lf-command-creator, lf-documentation-writing]
  validators: [bundle-validation, relative-link-check, v1-copy-reference-scan]
  human_gates: [approval, technical-review]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Scan para `.loki/analytic-inference/v1`, `migration-dry-run`, `copy migration` e `v1-to-v2` nas fontes normativas.
- Validar links e bundles `loki-*` alterados.
- `validate_catalog.py` permanece verde.

## Observable Validation

Nenhum caller ou documento normativo promete a capacidade removida, e o fluxo XML v2 continua retomável.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write e confirmar que somente compatibilidade v1 foi removida.

## Definition Of Done

- [ ] Core, callers e docs convergentes.
- [ ] Nenhuma referência normativa de copy migration.
- [ ] Catálogo atual validado.
- [ ] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["skills/lf-analytic-inference/SKILL.md", "skills/lf-analytic-inference/references/inference-contract.md"]
  write_owner: framework-artifact-writer
  target_files: ["skills/lf-analytic-inference/SKILL.md", "skills/lf-analytic-inference/references/inference-contract.md", "skills/loki-deep-analysis/SKILL.md", "skills/loki-deep-analysis/references/execution.md", "skills/loki-continuous-improvement/SKILL.md", "skills/loki-continuous-improvement/references/execution.md", "skills/loki-retrospectiva-tecnica/references/execution.md", "docs/loki-learning-workflow.md", "docs/loki-plan-execution-workflow.md", "docs/operational-inventory.md", "docs/usage-guide.md"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-3.3","coverage_digest":"sha256:fc1ee992b84ec5069c8b0485ac83280038cd52cf53ff92fa1f824e9b57651ea2","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:fc1ee992b84ec5069c8b0485ac83280038cd52cf53ff92fa1f824e9b57651ea2","reason":None,"next_action":"Align contracts after code removal."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
