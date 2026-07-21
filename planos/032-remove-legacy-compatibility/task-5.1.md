---
title: "task-5.1 - Remover a árvore Goose rastreada"
type: loki-task
status: completed
phase: fase5
task_id: task-5.1
---

# task-5.1 - Remover a árvore Goose rastreada

## Objective

Excluir os 20 artefatos Goose rastreados, conforme decisão humana, e provar que nenhuma fonte normativa continua dependendo deles.

## Context

Goose não está no manifest/install scopes e conflita com a autoridade do package root. A deleção é intencional, destrutiva e deve usar targets resolvidos antes do write.

## Execution Profile

```yaml
model_class: frontier_reasoning
task_effort: high
documentation_profile: durable
validator_effort: high
recommended_handoffs: {research: none, context: execution-context-reader, implementation: none, runtime_validation: none}
scoped_write_owner: orchestrator
scoped_write_mode: none
scoped_write_domains: [adapter-projection-removal]
orchestrator_exception_reason: "nenhum scoped writer instalado possui domínio para remover uma árvore de adapter não governada como unidade atômica"
escalation_reason: "deleção material de 20 arquivos rastreados"
```

## Requirements

- Revalidar `git ls-files goose` e comparar exatamente com os 20 targets.
- Parar se surgir arquivo rastreado novo, symlink, target fora da árvore ou referência normativa inesperada.
- Remover somente os arquivos rastreados aprovados; ignorados locais não são autoridade nem target automático.
- Registrar a decisão humana e o scan pós-deleção.

## Out Of Scope

- Remover root skills/agents equivalentes ou ampliar a deleção para outro adapter.

## Dependencies

- task-4.3

## References

- Decisão humana de 2026-07-20: remover `goose/**` como superfície transicional/histórica.
- `analise.md#9. Goose é uma projection transicional sem autoridade definida`.
- `docs/source-boundaries.md`.

## Implementation Steps

1. Resolver e comparar o tracked set sem deletar.
2. Executar a deleção somente se o conjunto for idêntico ao envelope.
3. Rodar scans de referências e package integrity.

## Scoped Write Plan

```yaml
scoped_write:
  owner: orchestrator
  mode: none
  target_files: &task_targets
    - goose/agents/bibliotecario.md
    - goose/agents/catalogador.md
    - goose/agents/retrospective-digester.md
    - goose/agents/source-researcher.md
    - goose/agents/standards-curator.md
    - goose/recipes/loki-continuous-improvement.yaml
    - goose/recipes/loki-deep-research.yaml
    - goose/recipes/loki-feedback.yaml
    - goose/recipes/loki-knowledge-extraction-analysis.yaml
    - goose/recipes/loki-migrate-command-to-recipe.yaml
    - goose/recipes/loki-retrospectiva-tecnica.yaml
    - goose/recipes/loki-self-healing.yaml
    - goose/skills/lf-agent-creator/SKILL.md
    - goose/skills/lf-command-creator/SKILL.md
    - goose/skills/lf-external-knowledge-extraction/SKILL.md
    - goose/skills/lf-framework-impact-audit/SKILL.md
    - goose/skills/lf-skill-creator/SKILL.md
    - goose/skills/loki-knowledge-extraction-analysis/SKILL.md
    - goose/skills/loki-retrospectiva-tecnica/SKILL.md
    - goose/skills/loki-self-healing/SKILL.md
  allowed_writes: *task_targets
  scoped_write_domains: [adapter-projection-removal]
  required_skills: []
  validators: [tracked-set-equality, goose-reference-scan, package-integrity]
  human_gates: [approval, technical-review]
  orchestrator_exception_reason: "no installed writer covers atomic removal of ungoverned Goose adapter artifacts"
  validation_owner: framework-artifact-quality-auditor
```

## Validators

- `git ls-files goose` é idêntico ao target set antes da deleção e vazio depois.
- Scan em fontes normativas não encontra referência ativa a `goose/**`, Goose-first, migration recipe ou deprecation bridge.
- Nenhum arquivo fora do target set foi removido.

## Observable Validation

A árvore Goose rastreada deixa de existir e a autoridade do pacote continua exclusivamente nas superfícies root/Codex/Claude declaradas.

## Human Loop

- Gate: approval, technical-review
- Required decision: aprovar a deleção do tracked set exato; qualquer diferença exige novo approval.

## Definition Of Done

- [ ] Tracked set confirmado antes do write.
- [ ] Exatamente 20 arquivos removidos.
- [ ] Nenhuma referência normativa residual.
- [ ] Nenhum root artifact equivalente removido.

## Review State Authority

Política e checkpoints pertencem a `tasks.md`.

## Resume Notes

```yaml
loki_task_state:
  schema_version: 1
  status: completed
  files_expected: ["20 tracked Goose deletions"]
  write_owner: orchestrator
  target_files: ["goose/agents/bibliotecario.md", "goose/agents/catalogador.md", "goose/agents/retrospective-digester.md", "goose/agents/source-researcher.md", "goose/agents/standards-curator.md", "goose/recipes/loki-continuous-improvement.yaml", "goose/recipes/loki-deep-research.yaml", "goose/recipes/loki-feedback.yaml", "goose/recipes/loki-knowledge-extraction-analysis.yaml", "goose/recipes/loki-migrate-command-to-recipe.yaml", "goose/recipes/loki-retrospectiva-tecnica.yaml", "goose/recipes/loki-self-healing.yaml", "goose/skills/lf-agent-creator/SKILL.md", "goose/skills/lf-command-creator/SKILL.md", "goose/skills/lf-external-knowledge-extraction/SKILL.md", "goose/skills/lf-framework-impact-audit/SKILL.md", "goose/skills/lf-skill-creator/SKILL.md", "goose/skills/loki-knowledge-extraction-analysis/SKILL.md", "goose/skills/loki-retrospectiva-tecnica/SKILL.md", "goose/skills/loki-self-healing/SKILL.md"]
  orchestrator_exception_reason: "atomic removal has no applicable installed scoped writer"
  validation_owner: framework-artifact-quality-auditor
  validations: []
  write_test_review:
    policy_ref: tasks.md#loki_plan_state.write_test_review.policy
    policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    local_coverage: {"boundary_type":"task","boundary_ref":"task-5.1","coverage_digest":"sha256:02946f01ca799903461f98d9f9c3d9fc6039eb2a2993b5266202ab2b0370cfa3","covered_write_handoff_ids":[],"changed_target_files":[],"completion_refs":[],"evidence_refs":[]}
    checkpoint_refs: []
    reconciliation: {"status":"not-evaluated","previous_checkpoint_ref":None,"current_coverage_digest":"sha256:02946f01ca799903461f98d9f9c3d9fc6039eb2a2993b5266202ab2b0370cfa3","reason":None,"next_action":"Resolve tracked set before any deletion."}
  next_action: "Completed; authoritative plan state is tasks.md."
  blocked_by: []
```
