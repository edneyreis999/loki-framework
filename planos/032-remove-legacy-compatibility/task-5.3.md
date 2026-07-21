---
title: "task-5.3 - Fechar validators de paridade dos adapters"
type: loki-task
status: completed
phase: fase5
task_id: task-5.3
---

# task-5.3 - Fechar validators de paridade dos adapters

## Objective

Implementar checks semânticos para projections Codex custom e cobertura Claude usando os contratos alinhados em task-5.2.

## Context

O validator atual cobre nomes e parte da fonte embutida, mas não prova paridade das quatro projections custom nem a cobertura completa de Claude.

## Execution Profile

```yaml
model_class: coding
task_effort: high
documentation_profile: none
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: technical-implementer, runtime_validation: none}
scoped_write_owner: technical-implementer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [validators]
orchestrator_exception_reason: none
escalation_reason: "paridade entre adapters precisa ser machine-checkable sem depender de equivalência textual falsa"
```

## Requirements

- Validar semanticamente as quatro projections Codex custom.
- Validar nome/fonte dos demais agents e parse de todos os TOMLs.
- Validar cobertura Claude de skills, agents e templates contra manifest/scopes.
- Rejeitar qualquer projection Goose residual.

## Out Of Scope

- Editar agents, TOMLs, manifest, scopes ou destinos instalados nesta task.

## Dependencies

- task-5.2

## References

- `task-5.2.md#Scoped Write Plan`.
- `agents/execution-knowledge-cataloger.md` e projection Codex correspondente.
- `agents/framework-artifact-quality-auditor.md` e projection Codex correspondente.
- `agents/framework-artifact-writer.md` e projection Codex correspondente.
- `agents/session-evidence-auditor.md` e projection Codex correspondente.
- `manifest.yaml` e `install-scopes.json`.

## Implementation Steps

1. Codificar checks semânticos explícitos para projections custom.
2. Adicionar cobertura Claude derivada das fontes machine-readable.
3. Rodar current-tree validation, TOML parse e os três install profiles.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: &task_targets
    - scripts/validate-loki-init-catalogador-contracts.py
    - scripts/validate-install-scopes.py
  allowed_writes: *task_targets
  scoped_write_domains: [validators]
  required_skills: []
  validators: [python-compile, current-tree-check, toml-parse, claude-coverage-check, three-profile-dry-runs]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `python3 -m py_compile scripts/validate-loki-init-catalogador-contracts.py scripts/validate-install-scopes.py`
- `python3 scripts/validate-loki-init-catalogador-contracts.py --enforce-current-tree`
- `python3 scripts/validate-install-scopes.py`
- Parse de todos os TOMLs e dry-run dos três profiles.

## Observable Validation

Drift em qualquer projection Codex custom ou lacuna de cobertura Claude produz falha determinística; ausência Goose permanece obrigatória.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar writes dos validators e registrar `human-validation` como não aplicável enquanto nenhum destino consumidor for exercitado.

## Definition Of Done

- [ ] Projections custom cobertas semanticamente.
- [ ] Cobertura Claude validada.
- [ ] Current-tree e profiles verdes.
- [ ] Nenhum runtime/consumer behavior alegado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["scripts/validate-loki-init-catalogador-contracts.py", "scripts/validate-install-scopes.py"]
  write_owner: technical-implementer
  target_files: ["scripts/validate-loki-init-catalogador-contracts.py", "scripts/validate-install-scopes.py"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-5.3","coverage_digest":"sha256:8f0b316df5f0ba694bee614a9bd3f75f615316fd882ad26057636eab86204d8d","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:8f0b316df5f0ba694bee614a9bd3f75f615316fd882ad26057636eab86204d8d","reason":None,"next_action":"Implement validators after task-5.2 artifacts are final."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
