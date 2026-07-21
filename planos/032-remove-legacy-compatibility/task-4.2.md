---
title: "task-4.2 - Remover cleanup e converter testes para rejeição"
type: loki-task
status: completed
phase: fase4
task_id: task-4.2
---

# task-4.2 - Remover cleanup e converter testes para rejeição

## Objective

Remover planejamento/aplicação de cleanup, `--cleanup-legacy-commands`, `removed_legacy_links` e migração de layouts antigos.

## Context

A suite atual prova remoção bem-sucedida de links antigos; a demanda exige rejeição explícita sem tocar conteúdo consumer-owned.

## Execution Profile

```yaml
model_class: coding
task_effort: high
documentation_profile: none
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: technical-implementer, runtime_validation: none}
scoped_write_owner: technical-implementer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [installation-code, validators]
orchestrator_exception_reason: none
escalation_reason: "remoção de código destrutivo exige negativas de non-interference"
```

## Requirements

- Remover flag, data classes, planners, apply, revalidation e manifest history de cleanup.
- Rejeitar command tree, skill-file symlink, parent symlink e previous manifest antigos.
- Preservar casos que provam não tocar arquivo real, link divergente ou path externo.

## Out Of Scope

- Limpar qualquer instalação real ou aceitar `--replace` como autorização substituta.

## Dependencies

- task-4.1

## References

- `analise.md#6. O instalador contém uma implementação completa de migração`.
- `scripts/install-loki-symlinks.py`.
- `scripts/validate-install-loki-upgrade.py`.
- `builds/fase1/canonical-contract-matrix.md`.

## Implementation Steps

1. Introduzir negativas para todos os layouts antigos e zero writes.
2. Remover o pipeline de cleanup/migration e o histórico do manifest.
3. Reescrever a suite de upgrade para rejection/non-interference.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: &task_targets
    - scripts/install-loki-symlinks.py
    - scripts/validate-install-loki-upgrade.py
    - scripts/validate-install-scopes.py
  allowed_writes: *task_targets
  scoped_write_domains: [installation-code, validators]
  required_skills: []
  validators: [python-compile, upgrade-suite, negative-layout-matrix, non-interference]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Upgrade suite verde com rejeições para todos os layouts antigos.
- Destinos temporários permanecem byte-identical após cada erro.
- CLI não aceita `--cleanup-legacy-commands`; `--replace` não migra layout antigo.

## Observable Validation

Nenhum branch detecta para migrar/remover legado; a única resposta é erro explícito antes de mutation.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar a deleção do pipeline; registrar `human-validation` como não aplicável sem instalação real.

## Definition Of Done

- [ ] Cleanup/migration removidos.
- [ ] Manifest não carrega histórico legado.
- [ ] Testes antigos convertidos para rejeição.
- [ ] Arquivos consumer-owned protegidos.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["scripts/install-loki-symlinks.py", "scripts/validate-install-loki-upgrade.py", "scripts/validate-install-scopes.py"]
  write_owner: technical-implementer
  target_files: ["scripts/install-loki-symlinks.py", "scripts/validate-install-loki-upgrade.py", "scripts/validate-install-scopes.py"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-4.2","coverage_digest":"sha256:97132ff8ef3e225d6dabbb0d396644bd3e7a7937eb738061c60acea28f5c0c0f","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:97132ff8ef3e225d6dabbb0d396644bd3e7a7937eb738061c60acea28f5c0c0f","reason":None,"next_action":"Remove cleanup after schema 2 cutover."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
