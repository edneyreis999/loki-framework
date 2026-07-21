---
title: "task-2.3 - Remover input retrospectivo legado"
type: loki-task
status: completed
phase: fase2
task_id: task-2.3
---

# task-2.3 - Remover input retrospectivo legado

## Objective

Remover `operational_trace` da interface pública de retrospectiva e aceitar somente `execution_evidence_sources`.

## Context

O input antigo permanece documentado como contextual, criando dois caminhos suportados para a mesma evidência.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: medium
documentation_profile: durable
validator_effort: medium
recommended_handoffs: {research: none, context: execution-context-reader, implementation: framework-artifact-writer, runtime_validation: none}
scoped_write_owner: framework-artifact-writer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [package-command-contracts, command-response-template]
orchestrator_exception_reason: none
escalation_reason: "mudança breaking em input de command público"
```

## Requirements

- Remover o input e toda semântica contextual associada.
- Definir erro explícito para o nome antigo.
- Preservar execution evidence provider-neutral e ausência de fallback retrospectivo.

## Out Of Scope

- Alterar coleta de evidence ou promover retrospectivas automaticamente.

## Dependencies

- task-2.2

## References

- `analise.md#4. A retrospectiva ainda aceita um input público legado`.
- `skills/loki-retrospectiva-tecnica/SKILL.md`.
- `skills/loki-retrospectiva-tecnica/references/execution.md`.

## Implementation Steps

1. Remover o argumento do Input e da execução.
2. Acrescentar rejeição explícita e alinhar response/template quando aplicável.
3. Validar integralmente o bundle.

## Scoped Write Plan

```yaml
scoped_write:
  owner: framework-artifact-writer
  mode: task_scoped_writer
  target_files: &task_targets
    - skills/loki-retrospectiva-tecnica/SKILL.md
    - skills/loki-retrospectiva-tecnica/references/execution.md
    - skills/loki-retrospectiva-tecnica/references/response.md
    - skills/loki-retrospectiva-tecnica/assets/response-template.md
  allowed_writes: *task_targets
  scoped_write_domains: [package-command-contracts, command-response-template]
  required_skills: [lf-command-creator, lf-documentation-writing]
  validators: [command-bundle-24-of-24, forbidden-input-scan, relative-link-check]
  human_gates: [approval, technical-review]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Checklist 24/24 do command bundle.
- Scan dirigido para `operational_trace` no bundle.
- Caso negativo comprova rejeição do input antigo.

## Observable Validation

Somente `execution_evidence_sources` aparece no contrato e o nome antigo produz erro acionável.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write e confirmar o breaking input contract.

## Definition Of Done

- [x] Input antigo removido de todas as superfícies do bundle.
- [x] Rejeição explícita documentada e validada.
- [x] Contrato atual preservado.
- [x] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["skills/loki-retrospectiva-tecnica/SKILL.md", "skills/loki-retrospectiva-tecnica/references/execution.md"]
  write_owner: framework-artifact-writer
  target_files: ["skills/loki-retrospectiva-tecnica/SKILL.md", "skills/loki-retrospectiva-tecnica/references/execution.md", "skills/loki-retrospectiva-tecnica/references/response.md", "skills/loki-retrospectiva-tecnica/assets/response-template.md"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: ["command-contract checklist 24/24: passed", "legacy negative case: passed", "relative links and diff check: passed", "write-test-review: clean"]
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-2.3","coverage_digest":"sha256:c84e977884d804e50d65c5daefe60bd94c92d43357ff5ae7517718f193437bfa","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:c84e977884d804e50d65c5daefe60bd94c92d43357ff5ae7517718f193437bfa","reason":None,"next_action":"Execute after evidence cutover."}
  next_action: "Task completed; release task-3.1."
  blocked_by: []
```
