---
title: "task-4.1 - Tornar install-scopes estritamente schema 2"
type: loki-task
status: completed
phase: fase4
task_id: task-4.1
---

# task-4.1 - Tornar install-scopes estritamente schema 2

## Objective

Fazer installer e validator aceitarem somente `install-scopes.json` schema 2 e rejeitarem `artifacts.commands` antes de planejar links.

## Context

Hoje ambos aceitam schema 1/2 e o branch schema 1 pode validar commands sem transformá-los em links atuais.

## Execution Profile

```yaml
model_class: coding
task_effort: high
documentation_profile: none
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: technical-implementer, runtime_validation: none}
scoped_write_owner: technical-implementer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [installation-code, validators, configuration]
orchestrator_exception_reason: none
escalation_reason: "breaking schema cutover deve falhar antes de qualquer write"
```

## Requirements

- Aceitar exatamente schema 2 e o shape atual.
- Rejeitar schema 1, `artifacts.commands` e campos desconhecidos com códigos/mensagens estáveis.
- Provar zero writes no dry-run e no erro.

## Out Of Scope

- Remover ainda o pipeline `--cleanup-legacy-commands` ou alterar consumidores.

## Dependencies

- task-3.4

## References

- `analise.md#6. O instalador contém uma implementação completa de migração`.
- `scripts/install-loki-symlinks.py`.
- `scripts/validate-install-scopes.py`.
- `install-scopes.json`.

## Implementation Steps

1. Fechar os dois parsers no schema 2.
2. Substituir fixtures schema 1 positivas por negativas.
3. Rodar validator, dry-runs e zero-write assertions.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: &task_targets
    - scripts/install-loki-symlinks.py
    - scripts/validate-install-scopes.py
    - install-scopes.json
  allowed_writes: *task_targets
  scoped_write_domains: [installation-code, validators, configuration]
  required_skills: []
  validators: [python-compile, validate-install-scopes, schema1-negative, three-profile-dry-runs]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `python3 scripts/validate-install-scopes.py`
- Schema 1 e `artifacts.commands` falham antes de criar destino.
- Dry-run `consumer`, `package-source` e `all` passa com schema 2.

## Observable Validation

Só schema 2 produz um `InstallScopeConfig`; qualquer formato antigo termina com erro e zero writes.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write e boundary pre-write; registrar `human-validation` como não aplicável porque só dry-runs temporários serão usados.

## Definition Of Done

- [ ] Leitor dual removido.
- [ ] Negativas antigas cobertas.
- [ ] Profiles atuais verdes.
- [ ] Nenhum destino real alterado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["scripts/install-loki-symlinks.py", "scripts/validate-install-scopes.py", "install-scopes.json"]
  write_owner: technical-implementer
  target_files: ["scripts/install-loki-symlinks.py", "scripts/validate-install-scopes.py", "install-scopes.json"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-4.1","coverage_digest":"sha256:aec00253a4e537cc8af4fd7a9545dff6afb1484a21ff7ccb7ac44d0cf5b41046","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:aec00253a4e537cc8af4fd7a9545dff6afb1484a21ff7ccb7ac44d0cf5b41046","reason":None,"next_action":"Cut install scopes to schema 2."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
