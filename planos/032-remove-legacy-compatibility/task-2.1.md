---
title: "task-2.1 - Fechar schemas agentic e sincronizar templates"
type: loki-task
status: completed
phase: fase2
task_id: task-2.1
---

# task-2.1 - Fechar schemas agentic e sincronizar templates

## Objective

Aceitar somente manifest 4, report 5 e digest 4, remover `legacy_reader_optional` e converter fixtures antigas em rejeições explícitas.

## Context

O validator aceita múltiplos schemas e contém fixture schema 1 positiva. Os mirrors atuais estão byte-identical e devem continuar assim.

## Execution Profile

```yaml
model_class: coding
task_effort: high
documentation_profile: durable
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: technical-implementer, runtime_validation: none}
scoped_write_owner: technical-implementer
scoped_write_mode: task_scoped_writer
scoped_write_domains: [validators, package-templates, package-skill-contracts]
orchestrator_exception_reason: none
escalation_reason: "cutover atômico de validator, templates e contrato persistido"
```

## Requirements

- Rejeitar qualquer root schema não canônico antes de checks condicionais.
- Remover `legacy_reader_optional` de validator, templates e mirrors.
- Corrigir o contrato de orchestration para as versões realmente emitidas.
- Preservar write-test-review schema 1, que permanece atual.

## Out Of Scope

- Alterar session evidence policy ou retrospective inputs.

## Dependencies

- task-1.2

## References

- `analise.md#2. O validator agentic mantém leitores legados`.
- `scripts/validate-agentic-run-state.py`.
- `skills/lf-agentic-orchestration/references/agentic-orchestration-contract.md`.
- `templates/agentic-run-manifest-template.xml` e mirrors.

## Implementation Steps

1. Introduzir rejeição fechada e fixtures negativas para schemas antigos/desconhecidos.
2. Remover atributos e branches legados.
3. Sincronizar os quatro pares de templates afetados e o contrato.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: &task_targets
    - scripts/validate-agentic-run-state.py
    - skills/lf-agentic-orchestration/SKILL.md
    - skills/lf-agentic-orchestration/references/agentic-orchestration-contract.md
    - templates/agentic-run-manifest-template.xml
    - templates/agent-run-report-template.xml
    - templates/agentic-run-digest-template.xml
    - templates/agentic-backlog-template.md
    - skills/lf-template-library/references/templates/agentic-run-manifest-template.xml
    - skills/lf-template-library/references/templates/agent-run-report-template.xml
    - skills/lf-template-library/references/templates/agentic-run-digest-template.xml
    - skills/lf-template-library/references/templates/agentic-backlog-template.md
  allowed_writes: *task_targets
  scoped_write_domains: [validators, package-templates, package-skill-contracts]
  required_skills: [lf-agentic-orchestration, lf-template-library]
  validators: [agentic-self-test, xml-parse, mirror-byte-parity]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `python3 scripts/validate-agentic-run-state.py --self-test`
- Parse XML dos templates e `cmp` de cada par raiz/mirror.
- Scan focado para `legacy_reader_optional`, positive legacy fixture e multi-schema roots.

## Observable Validation

Os formatos atuais passam e schemas antigos/desconhecidos falham com diagnóstico explícito sem bypass condicional.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write e confirmar schemas atuais; registrar `human-validation` como não aplicável sem runtime/consumer output.

## Definition Of Done

- [x] Roots agentic fechados nas versões canônicas.
- [x] Fixtures positivas legadas substituídas.
- [x] Mirrors byte-identical.
- [x] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["scripts/validate-agentic-run-state.py", "templates/agentic-run-manifest-template.xml", "templates/agent-run-report-template.xml", "templates/agentic-run-digest-template.xml", "templates/agentic-backlog-template.md"]
  write_owner: technical-implementer
  target_files: ["scripts/validate-agentic-run-state.py", "skills/lf-agentic-orchestration/SKILL.md", "skills/lf-agentic-orchestration/references/agentic-orchestration-contract.md", "templates/agentic-run-manifest-template.xml", "templates/agent-run-report-template.xml", "templates/agentic-run-digest-template.xml", "templates/agentic-backlog-template.md", "skills/lf-template-library/references/templates/agentic-run-manifest-template.xml", "skills/lf-template-library/references/templates/agent-run-report-template.xml", "skills/lf-template-library/references/templates/agentic-run-digest-template.xml", "skills/lf-template-library/references/templates/agentic-backlog-template.md"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations:
    - "agentic-self-test: passed"
    - "xml-parse: passed"
    - "mirror-byte-parity: passed (4 pairs)"
    - "focused legacy scan: passed"
    - "technical-review: completed-by-orchestrator-diff-and-validator-review-2026-07-21"
    - "write-test-review: completed-clean (raw clean)"
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage:
      boundary_type: task
      boundary_ref: task-2.1
      coverage_digest: "sha256:39e821f868d50f7f7604f1a7fef21871ee28c61bd7a7b070652cc6f6e84a5cb6"
      covered_write_handoff_ids: ["handoff-task-2.1-writer-20260721"]
      changed_target_files: ["scripts/validate-agentic-run-state.py", "skills/lf-agentic-orchestration/SKILL.md", "skills/lf-agentic-orchestration/references/agentic-orchestration-contract.md", "skills/lf-template-library/references/templates/agent-run-report-template.xml", "skills/lf-template-library/references/templates/agentic-run-digest-template.xml", "skills/lf-template-library/references/templates/agentic-run-manifest-template.xml", "templates/agent-run-report-template.xml", "templates/agentic-run-digest-template.xml", "templates/agentic-run-manifest-template.xml"]
      completion_refs: ["task-2.1.md#resume-notes"]
      evidence_refs: ["task-2.1.md#resume-notes"]
    checkpoint_refs:
      - checkpoint_id: "review-checkpoint-v1:79447b64b2f0d077446e3eb2fa087faeaa06d4b37cbbced37e6308ee13c204b8"
        checkpoint_ref: "tasks.md#loki_plan_state.write_test_review.checkpoints[1]"
        boundary_type: task
        boundary_ref: task-2.1
        coverage_digest: "sha256:39e821f868d50f7f7604f1a7fef21871ee28c61bd7a7b070652cc6f6e84a5cb6"
        status: completed-clean
    reconciliation:
      status: reused-terminal
      previous_checkpoint_ref: "tasks.md#loki_plan_state.write_test_review.checkpoints[1]"
      current_coverage_digest: "sha256:39e821f868d50f7f7604f1a7fef21871ee28c61bd7a7b070652cc6f6e84a5cb6"
      reason: null
      next_action: "Task completed; release task-2.2."
  next_action: "Task completed; release task-2.2."
  blocked_by: []
```
