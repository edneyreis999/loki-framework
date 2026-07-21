---
title: "task-5.2 - Alinhar artefatos Codex e cobertura Claude"
type: loki-task
status: completed
phase: fase5
task_id: task-5.2
---

# task-5.2 - Alinhar artefatos Codex e cobertura Claude

## Objective

Corrigir drift Codex conhecido e alinhar manifest/scopes para que a cobertura Claude seja declarada a partir das fontes canônicas.

## Context

Dois TOMLs Codex têm drift textual e quatro projections custom passam checks superficiais. Claude não possui validator equivalente nem cobertura de templates coerente no manifest.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: high
documentation_profile: durable
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: framework-artifact-writer, runtime_validation: none}
scoped_write_owner: framework-artifact-writer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [codex-agent-projections, package-manifest, install-scopes]
orchestrator_exception_reason: none
escalation_reason: "paridade entre adapters precisa ser semântica e machine-checkable"
```

## Requirements

- Corrigir drift em retrospective-digester e standards-curator.
- Preparar contratos observáveis para as quatro projections custom.
- Declarar cobertura Claude de skills, agents e templates em manifest/scopes.
- Não reintroduzir Goose como terceira projection.

## Out Of Scope

- Escrever em destinos `.codex/**` ou `.claude/**` de consumidor.

## Dependencies

- task-5.1

## References

- `analise.md#8. Codex e Claude não têm a mesma cobertura observável`.
- `agents/*.md` como fontes de agent contract.
- `codex/agents/*.toml` como projections.
- `scripts/validate-loki-init-catalogador-contracts.py`.
- `manifest.yaml` e `install-scopes.json`.

## Implementation Steps

1. Reconciliar os dois drifts contra as fontes Markdown.
2. Alinhar contratos custom e cobertura Claude em manifest/scopes.
3. Rodar TOML parse e checks existentes antes do handoff à task-5.3.

## Scoped Write Plan

```yaml
scoped_write:
  owner: framework-artifact-writer
  mode: task_scoped_writer
  target_files: &task_targets
    - codex/agents/retrospective-digester.toml
    - codex/agents/standards-curator.toml
    - codex/agents/execution-knowledge-cataloger.toml
    - codex/agents/framework-artifact-quality-auditor.toml
    - codex/agents/framework-artifact-writer.toml
    - codex/agents/session-evidence-auditor.toml
    - manifest.yaml
    - install-scopes.json
  allowed_writes: *task_targets
  scoped_write_domains: [codex-agent-projections, package-manifest, install-scopes]
  required_skills: [lf-documentation-writing]
  validators: [toml-parse, current-tree-check, manifest-scope-consistency]
  human_gates: [approval, technical-review]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Parse de todos os TOMLs com `tomllib` e paridade de nomes 25/25.
- Current-tree check existente executado como baseline para task-5.3.
- Cobertura Claude declarada em manifest/scopes sem contagens hard-coded.
- Scan confirma ausência de projection Goose.

## Observable Validation

Os artefatos Codex/Claude estão alinhados e oferecem fontes explícitas para os validators da task-5.3.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar as alterações de projection e a declaração de cobertura Claude.

## Definition Of Done

- [ ] Drifts conhecidos corrigidos.
- [ ] Contratos custom preparados para validação semântica.
- [ ] Cobertura Claude declarada.
- [ ] Goose não reintroduzido.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["codex/agents/retrospective-digester.toml", "codex/agents/standards-curator.toml", "manifest.yaml", "install-scopes.json"]
  write_owner: framework-artifact-writer
  target_files: ["codex/agents/retrospective-digester.toml", "codex/agents/standards-curator.toml", "codex/agents/execution-knowledge-cataloger.toml", "codex/agents/framework-artifact-quality-auditor.toml", "codex/agents/framework-artifact-writer.toml", "codex/agents/session-evidence-auditor.toml", "manifest.yaml", "install-scopes.json"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-5.2","coverage_digest":"sha256:9a35b7132567073ad829d750c1db41cda4536511323b6f5132a6ca7c6db9624c","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:9a35b7132567073ad829d750c1db41cda4536511323b6f5132a6ca7c6db9624c","reason":None,"next_action":"Validate remaining adapters after Goose removal."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
