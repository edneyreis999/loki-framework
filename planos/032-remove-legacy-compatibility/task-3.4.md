---
title: "task-3.4 - Remover fallback consumer index.md"
type: loki-task
status: completed
phase: fase3
task_id: task-3.4
---

# task-3.4 - Remover fallback consumer index.md

## Objective

Fazer `lf-index-navigator` exigir `docs/index.xml` no consumidor e preservar o `index.md` canônico da raiz do pacote.

## Context

O fallback consumer confunde duas superfícies com autoridades distintas.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: medium
documentation_profile: durable
validator_effort: medium
recommended_handoffs: {research: none, context: execution-context-reader, implementation: framework-artifact-writer, runtime_validation: none}
scoped_write_owner: framework-artifact-writer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [package-skill-contracts, package-documentation, package-manifest]
orchestrator_exception_reason: none
escalation_reason: "mudança de discovery contract do consumidor"
```

## Requirements

- Remover lookup e instruções de fallback consumer.
- Documentar falha explícita quando `docs/index.xml` estiver ausente.
- Preservar a autoridade de `index.md` na raiz do pacote.

## Out Of Scope

- Criar `docs/index.xml` em consumidor ou alterar o `index.md` do pacote.

## Dependencies

- task-3.3

## References

- `analise.md#7. O fallback documental do consumidor ainda é público`.
- `skills/lf-index-navigator/SKILL.md`.
- `skills/lf-index-navigator/references/index-xml-contract.md`.
- `docs/source-boundaries.md`.

## Implementation Steps

1. Remover o branch e o texto de fallback.
2. Declarar erro e minimum next path para catálogo ausente.
3. Validar source boundaries e ausência do fallback.

## Scoped Write Plan

```yaml
scoped_write:
  owner: framework-artifact-writer
  mode: task_scoped_writer
  target_files: &task_targets
    - skills/lf-index-navigator/SKILL.md
    - skills/lf-index-navigator/references/index-xml-contract.md
    - docs/source-boundaries.md
    - docs/operational-inventory.md
    - docs/package-authoring-guardrails.md
    - manifest.yaml
  allowed_writes: *task_targets
  scoped_write_domains: [package-skill-contracts, package-documentation, package-manifest]
  required_skills: [lf-documentation-writing]
  validators: [relative-link-check, index-fallback-negative, manifest-path-check]
  human_gates: [approval, technical-review]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Scan dirigido confirma ausência de `index.md` como fallback consumer.
- Links e paths do manifest continuam válidos.
- `index.md` raiz permanece presente e documentado como source do pacote.

## Observable Validation

Consumidor sem `docs/index.xml` recebe falha explícita e nenhuma leitura de `index.md` é tentada.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write e a separação entre consumer navigation e package index.

## Definition Of Done

- [ ] Fallback consumer removido.
- [ ] Falha explícita definida.
- [ ] Package `index.md` preservado.
- [ ] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["skills/lf-index-navigator/SKILL.md", "skills/lf-index-navigator/references/index-xml-contract.md"]
  write_owner: framework-artifact-writer
  target_files: ["skills/lf-index-navigator/SKILL.md", "skills/lf-index-navigator/references/index-xml-contract.md", "docs/source-boundaries.md", "docs/operational-inventory.md", "docs/package-authoring-guardrails.md", "manifest.yaml"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-3.4","coverage_digest":"sha256:c6f2e3bbb6c2da6326cb7644ce6ee45fe030997f0b62256d601f55cfae317d08","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:c6f2e3bbb6c2da6326cb7644ce6ee45fe030997f0b62256d601f55cfae317d08","reason":None,"next_action":"Remove the consumer fallback after inference cutover."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
