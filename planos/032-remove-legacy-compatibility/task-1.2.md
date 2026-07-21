---
title: "task-1.2 - Restaurar baseline do validator de upgrade"
type: loki-task
status: completed
phase: fase1
task_id: task-1.2
---

# task-1.2 - Restaurar baseline do validator de upgrade

## Objective

Fazer o validator de upgrade refletir o inventário atual e voltar a passar sem remover ainda nenhum comportamento legacy.

## Context

A suite falha em 6 de 17 testes por contagens e dependências stale. O baseline precisa ficar verde antes do corte para separar regressão de dívida anterior.

## Execution Profile

```yaml
model_class: coding
task_effort: medium
documentation_profile: none
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: technical-implementer, runtime_validation: none}
scoped_write_owner: technical-implementer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [validators]
orchestrator_exception_reason: none
escalation_reason: "baseline deve mudar sem antecipar o comportamento do corte"
```

## Requirements

- Derivar contagens dos profiles em vez de perpetuar constantes stale quando viável.
- Atualizar a expectativa de dependências de `loki-agentic-development`.
- Preservar temporariamente os testes legacy positivos para que esta task seja apenas baseline repair.

## Out Of Scope

- Remover cleanup, schema 1 ou fixtures legacy nesta task.

## Dependencies

- task-1.1

## References

- `analise.md#10. O baseline de instalação já está vermelho`.
- `scripts/validate-install-loki-upgrade.py`.
- `install-scopes.json`.
- `manifest.yaml`.

## Implementation Steps

1. Reproduzir as 6 falhas e identificar a origem de cada expectativa.
2. Substituir expectativas stale por derivação ou valores atuais justificados.
3. Rodar a suite e os três dry-runs sem tocar destino real.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: ["scripts/validate-install-loki-upgrade.py"]
  allowed_writes: [scripts/validate-install-loki-upgrade.py]
  scoped_write_domains: [validators]
  required_skills: []
  validators: [python-compile, upgrade-suite, three-profile-dry-runs]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `python3 -m py_compile scripts/validate-install-loki-upgrade.py`
- `python3 scripts/validate-install-loki-upgrade.py`
- Dry-run dos profiles `consumer`, `package-source` e `all` em diretório temporário.

## Observable Validation

Os 17 testes passam no comportamento pré-corte e as contagens observadas são 99/68/108 ou derivadas diretamente das fontes atuais.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write e confirmar que corrige somente drift; registrar `human-validation` como não aplicável sem destino consumidor.

## Definition Of Done

- [x] Suite verde antes do corte.
- [x] Nenhuma remoção legacy antecipada.
- [x] Dry-runs sem writes reais.
- [x] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`; esta task registra somente cobertura local.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["scripts/validate-install-loki-upgrade.py"]
  write_owner: technical-implementer
  target_files: ["scripts/validate-install-loki-upgrade.py"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations:
    - "python3 -m py_compile scripts/validate-install-loki-upgrade.py: passed"
    - "python3 scripts/validate-install-loki-upgrade.py: passed (17 tests)"
    - "dry-runs consumer/package-source/all: passed with absent destinations"
    - "write-test-review: completed-clean (raw approved)"
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage:
      boundary_type: task
      boundary_ref: task-1.2
      coverage_digest: "sha256:d931e9b6af01c3e0a3b2de6c6de13d32ed5dbad600ea6f55336e5be5c00135c7"
      covered_write_handoff_ids: ["handoff-task-1.2-writer-20260721"]
      changed_target_files: ["scripts/validate-install-loki-upgrade.py"]
      completion_refs: ["task-1.2.md#resume-notes"]
      evidence_refs: ["task-1.2.md#resume-notes"]
    checkpoint_refs:
      - checkpoint_id: "review-checkpoint-v1:1c3632d45b44e675deff6be31dbd595770652d136a428b477ef7a2e9ed3b17de"
        checkpoint_ref: "tasks.md#loki_plan_state.write_test_review.checkpoints[2]"
        boundary_type: task
        boundary_ref: task-1.2
        coverage_digest: "sha256:d931e9b6af01c3e0a3b2de6c6de13d32ed5dbad600ea6f55336e5be5c00135c7"
        status: completed-clean
    reconciliation:
      status: reused-terminal
      previous_checkpoint_ref: "tasks.md#loki_plan_state.write_test_review.checkpoints[2]"
      current_coverage_digest: "sha256:d931e9b6af01c3e0a3b2de6c6de13d32ed5dbad600ea6f55336e5be5c00135c7"
      reason: null
      next_action: "Await required human technical-review."
  technical_review: "completed-by-orchestrator-diff-and-validator-review-2026-07-21; consultive WTR clean"
  next_action: "Task completed; release task-2.1."
  blocked_by: []
```
