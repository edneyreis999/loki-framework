---
title: "task-2.2 - Fechar política de session evidence"
type: loki-task
status: completed
phase: fase2
task_id: task-2.2
---

# task-2.2 - Fechar política de session evidence

## Objective

Substituir campos negativos legados por um contrato positivo e fechado de evidence-first, preservando as proibições existentes.

## Context

Templates e collector emitem `automatic_agent_retrospective`, `dual_capture` e `legacy_retrospective_fallback`, mas o validator não fecha integralmente esse shape.

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
escalation_reason: "remover campos não pode enfraquecer proibições de evidence"
```

## Requirements

- Definir shape fechado que proíba retrospectiva automática, captura dupla e fallback sem depender de campos `legacy_*`.
- Atualizar collector, validator, contrato, template raiz e mirror.
- Converter shapes antigos e children desconhecidos em casos negativos.

## Out Of Scope

- Alterar TTL, purge, PII hardening ou capabilities dos adapters.

## Dependencies

- task-2.1

## References

- `analise.md#3. Evidência ainda carrega campos de política legada`.
- `skills/lf-agent-execution-evidence/references/evidence-contract.md`.
- `skills/lf-agent-execution-evidence/scripts/capture-session-evidence.py`.
- `skills/lf-agent-execution-evidence/scripts/validate-session-evidence.py`.

## Implementation Steps

1. Definir a política positiva no contrato.
2. Atualizar emissão e validação fechada.
3. Sincronizar templates e executar fixtures positivas/negativas.

## Scoped Write Plan

```yaml
scoped_write:
  owner: technical-implementer
  mode: task_scoped_writer
  target_files: &task_targets
    - skills/lf-agent-execution-evidence/references/evidence-contract.md
    - skills/lf-agent-execution-evidence/references/collector-contract.md
    - skills/lf-agent-execution-evidence/scripts/capture-session-evidence.py
    - skills/lf-agent-execution-evidence/scripts/validate-session-evidence.py
    - templates/agent-session-evidence-template.xml
    - skills/lf-template-library/references/templates/agent-session-evidence-template.xml
    - templates/agentic-run-manifest-template.xml
    - skills/lf-template-library/references/templates/agentic-run-manifest-template.xml
  allowed_writes: *task_targets
  scoped_write_domains: [validators, package-templates, package-skill-contracts]
  required_skills: [lf-agent-execution-evidence, lf-template-library]
  validators: [evidence-validator, xml-parse, mirror-byte-parity, negative-shape-tests]
  human_gates: [approval, technical-review, human-validation]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- Rodar self-tests/fixtures do collector e validator de session evidence.
- Parse XML e `cmp` dos dois pares alterados.
- Scan focado confirma ausência dos três campos legados.

## Observable Validation

O formato atual continua evidence-first; shapes antigos e children não declarados falham explicitamente.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar o write e a regra positiva; registrar `human-validation` como não aplicável sem runtime/consumer output.

## Definition Of Done

- [x] Emissor e validator compartilham um único shape.
- [x] Nenhum campo de política legada permanece.
- [x] Negative fixtures cobrem regressões.
- [x] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["skills/lf-agent-execution-evidence/scripts/capture-session-evidence.py", "skills/lf-agent-execution-evidence/scripts/validate-session-evidence.py", "templates/agent-session-evidence-template.xml"]
  write_owner: technical-implementer
  target_files: ["skills/lf-agent-execution-evidence/references/evidence-contract.md", "skills/lf-agent-execution-evidence/references/collector-contract.md", "skills/lf-agent-execution-evidence/scripts/capture-session-evidence.py", "skills/lf-agent-execution-evidence/scripts/validate-session-evidence.py", "templates/agent-session-evidence-template.xml", "skills/lf-template-library/references/templates/agent-session-evidence-template.xml", "templates/agentic-run-manifest-template.xml", "skills/lf-template-library/references/templates/agentic-run-manifest-template.xml"]
  orchestrator_exception_reason: none
  validation_owner: framework-artifact-quality-auditor
  validations: ["positive and negative session-evidence fixtures: passed", "xml parse and mirror parity: passed", "forbidden-field scan: passed", "write-test-review: clean after template-order correction"]
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-2.2","coverage_digest":"sha256:c77bd3d0fbe8cd6c007e68b74e5855b4e65e088f26afaa9dc545409bb2f07418","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:c77bd3d0fbe8cd6c007e68b74e5855b4e65e088f26afaa9dc545409bb2f07418","reason":None,"next_action":"Execute after task-2.1."}
  next_action: "Task completed; release task-2.3."
  blocked_by: []
```
