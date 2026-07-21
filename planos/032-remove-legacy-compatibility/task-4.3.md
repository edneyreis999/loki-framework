---
title: "task-4.3 - Alinhar manifest e documentação de instalação"
type: loki-task
status: completed
phase: fase4
task_id: task-4.3
---

# task-4.3 - Alinhar manifest e documentação de instalação

## Objective

Remover promessas de migração/cleanup e documentar somente o fluxo schema 2 com rejeição de instalações antigas.

## Context

README, usage guide, workflow, guardrails e inventário ainda ensinam `--cleanup-legacy-commands` e layouts antigos.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: high
documentation_profile: durable
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: framework-artifact-writer, runtime_validation: none}
scoped_write_owner: framework-artifact-writer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [package-manifest, install-scopes, package-documentation]
orchestrator_exception_reason: none
escalation_reason: "docs e inventário devem corresponder exatamente ao installer breaking contract"
```

## Requirements

- Remover flags, exemplos e expectativas de cleanup/migração.
- Atualizar contagens e cobertura Claude a partir de fontes machine-readable.
- Fazer manifest, scopes, README e docs concordarem sobre templates e profiles.

## Out Of Scope

- Instalar em `.agents/**`, `.codex/**` ou `.claude/**`.

## Dependencies

- task-4.2

## References

- `README.md`, seção de instalação Codex/Claude.
- `docs/loki-installation-workflow.md`.
- `docs/usage-guide.md`.
- `docs/package-authoring-guardrails.md#Codex Symlink Installer`.
- `manifest.yaml` e `install-scopes.json`.

## Implementation Steps

1. Atualizar inventário e metadados de instalação.
2. Reescrever documentação para rejection-only.
3. Validar links, contagens, manifest e dry-runs.

## Scoped Write Plan

```yaml
scoped_write:
  owner: framework-artifact-writer
  mode: task_scoped_writer
  target_files: &task_targets
    - README.md
    - docs/loki-installation-workflow.md
    - docs/usage-guide.md
    - docs/package-authoring-guardrails.md
    - docs/operational-inventory.md
    - manifest.yaml
    - install-scopes.json
  allowed_writes: *task_targets
  scoped_write_domains: [package-manifest, install-scopes, package-documentation]
  required_skills: [lf-documentation-writing]
  validators: [manifest-path-check, validate-install-scopes, three-profile-dry-runs, relative-link-check]
  human_gates: [approval, technical-review]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `python3 scripts/validate-install-scopes.py`
- Três dry-runs em destino temporário.
- Scan focado para flag, cleanup history e instruções de migração removidas.

## Observable Validation

Um leitor encontra um único fluxo schema 2 e nenhuma instrução para migrar ou limpar formatos antigos.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write, breaking-change messaging e cobertura Claude.

## Definition Of Done

- [ ] Docs e código descrevem o mesmo fluxo.
- [ ] Contagens não estão stale.
- [ ] Manifest/scopes coerentes.
- [ ] Nenhuma instalação real executada.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["README.md", "docs/loki-installation-workflow.md", "docs/usage-guide.md", "docs/package-authoring-guardrails.md", "docs/operational-inventory.md", "manifest.yaml", "install-scopes.json"]
  write_owner: framework-artifact-writer
  target_files: ["README.md", "docs/loki-installation-workflow.md", "docs/usage-guide.md", "docs/package-authoring-guardrails.md", "docs/operational-inventory.md", "manifest.yaml", "install-scopes.json"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-4.3","coverage_digest":"sha256:47580edd5e1c29971a5f585a9e339464d8c9f7393e96dbd46d26b4214bb790c3","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:47580edd5e1c29971a5f585a9e339464d8c9f7393e96dbd46d26b4214bb790c3","reason":None,"next_action":"Align docs after installer behavior is final."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
