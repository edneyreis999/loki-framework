---
title: "task-6.1 - Consolidar inventário, guardrails e documentação"
type: loki-task
status: completed
phase: fase6
task_id: task-6.1
---

# task-6.1 - Consolidar inventário, guardrails e documentação

## Objective

Publicar uma descrição única do estado pós-corte em manifest, inventory, source boundaries, README, usage e guardrails.

## Context

As fases anteriores alteram contratos distribuídos; esta task remove drift residual sem reabrir decisões funcionais.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: high
documentation_profile: durable
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: framework-artifact-writer, runtime_validation: none}
scoped_write_owner: framework-artifact-writer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [package-documentation, package-manifest, install-scopes]
orchestrator_exception_reason: none
escalation_reason: "consolidação normativa final de breaking change transversal"
```

## Requirements

- Documentar a matriz canônica por família e a política rejection-only.
- Remover texto residual que prometa legacy readers, migration, cleanup ou Goose.
- Preservar explicitamente domain compatibility e fallbacks operacionais atuais.
- Atualizar manifest na mesma mudança quando paths/status/artefatos mudarem.

## Out Of Scope

- Adicionar funcionalidade nova, instalar ou alterar consumidores.

## Dependencies

- task-5.3

## References

- `builds/fase1/canonical-contract-matrix.md`.
- `TODO: localizar` completion/evidence refs de tasks 2.1–5.3 no `tasks.md` e nos checkpoints persistidos antes de iniciar esta task.
- `docs/package-authoring-guardrails.md`.
- `docs/source-boundaries.md`.

## Implementation Steps

1. Reconciliar documentação contra código e validators finais.
2. Atualizar manifest/inventory/scopes quando requerido pelos artefatos reais.
3. Executar links, scans e quality profile antes da auditoria.

## Scoped Write Plan

```yaml
scoped_write:
  owner: framework-artifact-writer
  mode: task_scoped_writer
  target_files: &task_targets
    - README.md
    - docs/usage-guide.md
    - docs/operational-inventory.md
    - docs/source-boundaries.md
    - docs/package-authoring-guardrails.md
    - docs/loki-installation-workflow.md
    - docs/loki-learning-workflow.md
    - docs/loki-plan-execution-workflow.md
    - manifest.yaml
    - install-scopes.json
  allowed_writes: *task_targets
  scoped_write_domains: [package-documentation, package-manifest, install-scopes]
  required_skills: [lf-documentation-writing]
  validators: [relative-link-check, manifest-path-check, focused-forbidden-scan, documentation-consistency]
  human_gates: [approval, technical-review]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Links relativos e paths do manifest existem.
- Scan focado de referências proibidas conforme guardrails.
- Scan semântico não encontra promessas legacy, mas preserva usos classificados como atuais/domínio.

## Observable Validation

Código, validators, manifest, scopes e documentos descrevem o mesmo conjunto de contratos e adapters suportados.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write, a redação normativa e a classificação dos usos residuais.

## Definition Of Done

- [ ] Inventário e docs convergentes.
- [ ] Manifest/scopes sincronizados.
- [ ] Nenhuma promessa legacy residual.
- [ ] Preservações explícitas mantidas.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["README.md", "docs/usage-guide.md", "docs/operational-inventory.md", "docs/source-boundaries.md", "docs/package-authoring-guardrails.md", "manifest.yaml", "install-scopes.json"]
  write_owner: framework-artifact-writer
  target_files: ["README.md", "docs/usage-guide.md", "docs/operational-inventory.md", "docs/source-boundaries.md", "docs/package-authoring-guardrails.md", "docs/loki-installation-workflow.md", "docs/loki-learning-workflow.md", "docs/loki-plan-execution-workflow.md", "manifest.yaml", "install-scopes.json"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-6.1","coverage_digest":"sha256:12cedac22feac47dfd61fa04cd651ae036c486e6a739544f3b74bca6f1553b42","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:12cedac22feac47dfd61fa04cd651ae036c486e6a739544f3b74bca6f1553b42","reason":None,"next_action":"Consolidate docs after all behavior/projection cuts."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
