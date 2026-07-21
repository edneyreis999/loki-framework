---
title: "task-6.2 - Executar aceite integral e revisão independente"
type: loki-task
status: completed
phase: fase6
task_id: task-6.2
---

# task-6.2 - Executar aceite integral e revisão independente

## Objective

Executar a matriz completa de validators e consolidar evidence suficiente para technical review final sem alegar runtime consumer validado.

## Context

Esta task não corrige produção. Findings voltam ao owner da task correspondente e invalidam o parecer anterior após qualquer correção.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: high
documentation_profile: transient
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: none, runtime_validation: none}
scoped_write_owner: orchestrator
scoped_write_mode: none
scoped_write_domains: [task-local-evidence]
orchestrator_exception_reason: "orquestrador consolida evidence; auditor independente permanece read-only"
escalation_reason: "aceite transversal com validator histórico e deleções materiais"
```

## Requirements

- Executar validators focados e checks de integridade do pacote.
- Executar scan literal e classificação semântica dos hits residuais.
- Obter auditoria independente de `framework-artifact-quality-auditor` sobre o patch real.
- Registrar technical review humano; finding material impede conclusão.

## Out Of Scope

- Corrigir arquivos de produção nesta task, instalar, commitar ou alegar comportamento de consumidor.

## Dependencies

- task-6.1

## References

- `demanda.md#Critérios de aceitação`.
- `analise.md#Validators executados`.
- `docs/package-authoring-guardrails.md#Validações Mínimas`.
- `TODO: localizar` completion/evidence refs de tasks 1.1–6.1 no `tasks.md` e nos checkpoints persistidos antes de iniciar esta task.

## Implementation Steps

1. Executar a matriz automatizada e registrar comandos/outputs.
2. Verificar DAG, targets, mirrors, manifest, scopes, bundles e ausência Goose.
3. Despachar auditor independente e registrar technical review final.

## Scoped Write Plan

```yaml
scoped_write:
  owner: orchestrator
  mode: none
  target_files:
    - planos/032-remove-legacy-compatibility/builds/fase6/full-validation-report.md
    - planos/032-remove-legacy-compatibility/interaction/fase6/technical-review.md
  allowed_writes:
    - planos/032-remove-legacy-compatibility/builds/fase6/full-validation-report.md
    - planos/032-remove-legacy-compatibility/interaction/fase6/technical-review.md
  scoped_write_domains: [task-local-evidence]
  required_skills: []
  validators: [full-package-matrix, action-plan-resume-check]
  human_gates: [technical-review]
  orchestrator_exception_reason: "evidence consolidation and human-decision recording are orchestrator-owned"
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `python3 scripts/validate-agentic-run-state.py --self-test`
- Session evidence validators e analytic-inference catalog validator.
- `python3 scripts/validate-install-scopes.py`
- `python3 scripts/validate-install-loki-upgrade.py`
- `python3 scripts/validate-loki-init-catalogador-contracts.py --enforce-current-tree`
- `python3 scripts/validate-run-plan-review-state.py tasks.md` com todos os `--task-file` do plano.
- Dry-run dos três install profiles em diretório temporário.
- Parse YAML/frontmatter, TOML e XML; `cmp` dos 18 template mirrors.
- Integrity commands e forbidden-reference scan dos guardrails.
- `git ls-files goose` vazio e scan legacy residual classificado.

## Observable Validation

Todos os critérios da demanda possuem evidência mecânica ou technical review explícito; nenhum validator material está falho ou inconclusivo.

## Human Loop

- Gate: technical-review
- Required decision: aprovar ou rejeitar o patch integral com base no relatório e auditoria independente.

## Definition Of Done

- [ ] Matriz integral verde.
- [ ] Auditoria independente sem finding material.
- [ ] Technical review registrado.
- [ ] Nenhuma alegação de runtime/consumer validation.
- [ ] Fora de escopo preservado.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`; reviewer outcomes são consultivos e não substituem validators ou technical review.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["planos/032-remove-legacy-compatibility/builds/fase6/full-validation-report.md", "planos/032-remove-legacy-compatibility/interaction/fase6/technical-review.md"]
  write_owner: orchestrator
  target_files: ["planos/032-remove-legacy-compatibility/builds/fase6/full-validation-report.md", "planos/032-remove-legacy-compatibility/interaction/fase6/technical-review.md"]
  orchestrator_exception_reason: "evidence consolidation and human gate recording"
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-6.2","coverage_digest":"sha256:649a0d9b0c2f6f22104737adbb500302963b912a1bfb9043895b6059de32d472","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:649a0d9b0c2f6f22104737adbb500302963b912a1bfb9043895b6059de32d472","reason":None,"next_action":"Run the full acceptance matrix after documentation convergence."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
