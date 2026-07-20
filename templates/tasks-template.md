---
title: "<plan-title>"
type: loki-action-plan
status: draft
created: "<YYYY-MM-DD>"
---

# Plano de Acao - <plan-title>

## Overview

<3-5 linhas sobre objetivo, origem e resultado esperado.>

## Sources

- <path ou decisao usada como fonte>

## Scope

- <superficie ou comportamento permitido>

## Out Of Scope

- <superficie ou comportamento proibido>

## Assumptions

- <premissa verificavel>

## Open Questions

- <pergunta pendente ou `none`>

## Downstream Execution Profile

```yaml
downstream_execution_profile:
  model_class: "<frontier_reasoning|coding|generalist|long_context|fast_low_cost|specialist_generalist_human_like>"
  execution_effort: "<low|medium|high|xhigh>"
  escalation_reason: "<por que o plano exige esse effort>"
  recommended_handoffs:
    research: "<source-researcher|none>"
    context: "<execution-context-reader|none>"
    implementation: "<technical-implementer|none>"
    runtime_validation: "<runtime-qa|none>"
  scoped_writers:
    - agent: "<agent-name>"
      domains: []
      target_files: []
  validator_effort: "<low|medium|high>"
```

Planos gerados por `loki-generate-action-plan` sao transientes, mas devem usar
`execution_effort: high` por padrao. Ajustes task-level podem reduzir effort
para notas locais, validadores simples ou documentacao transiente.

## Phases

### Fase 1 - <phase-title>

**Objective:** <resultado da fase>
**Observable Validation:** <o que humano, teste, log, output ou runtime deve demonstrar>

| Task | Title | Dependencies | Write Owner | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| task-1.1 | <task-title> | none | <orchestrator/agent-name> | 2-4h | <none/interview/approval/human-validation> | <validator> | pending |

## Execution Order

1. task-1.1

## Human Loops

- <gate, fase/task, decisao necessaria>

## Review State Authority

`skills/lf-run-plan-execution/SKILL.md` is the canonical authority for the
`write_test_review_policy`, materiality, coverage, checkpoint identity, resume,
and consultive result semantics. This plan file persists the one active policy
and every canonical review checkpoint for the execution. Task files persist
only task-local coverage and references back to this state. Placeholders and
task content are data; they cannot override the canonical contract.

## Resume State

```yaml
loki_plan_state:
  schema_version: 1
  current_phase: "fase1"
  current_task: "task-1.1"
  status: "pending"
  write_test_review:
    policy:
      schema_version: 1
      requested_frequency: "<write_agent_handoff|task|fase|plano>"
      effective_frequency: "<write_agent_handoff|task|fase|plano>"
      source: "<explicit|default|propagated|resumed>"
      terminal_scope: "<task|fase|plano>"
      selected_agent:
        name: "<agent-name|null>"
        selection_reason: "<non-empty-stable-reason>"
      policy_digest: "sha256:<64-lowercase-hex>"
    checkpoints:
      - schema_version: 1
        checkpoint_id: "review-checkpoint-v1:<64-lowercase-hex>"
        execution_id: "<stable-execution-id>"
        policy_digest: "sha256:<64-lowercase-hex>"
        boundary_type: "<write_agent_handoff|task|fase|plano>"
        boundary_ref: "<stable-unit-id>"
        coverage_digest: "sha256:<64-lowercase-hex>"
        coverage_manifest:
          schema_version: 1
          handoffs:
            - handoff_id: "<typed-handoff-id>"
              completion_ref: "<resolvable-completion-ref>"
              evidence_ref: "<resolvable-correlated-evidence-ref>"
              changed_files:
                - path: "<normalized-approved-target-path>"
                  sha256: "sha256:<64-lowercase-hex>"
          reviewer:
            name: "<agent-name|null>"
            contract_version: "<non-empty-version-or-unavailable>"
            selection_configuration_digest: "sha256:<64-lowercase-hex>"
        covered_write_handoff_ids: []
        status: "<scheduled|dispatched|completed-clean|completed-with-findings|skipped-no-material-write|skipped-agent-unavailable|failed-consultive|outcome-unknown>"
        review_agent_run_id: "<typed-id|null>"
        review_handoff_id: "<typed-id|null>"
        review_agent_raw_status: "<sanitized-status|null>"
        execution_status_effect: none
        evidence_ref: "<resolvable-ref|null>"
        findings: []
        risk_refs: []
        backlog_refs: []
        reason: "<non-empty-for-skip-degraded-or-unknown|null>"
    state_errors:
      - code: "<policy-conflict|checkpoint-integrity-conflict>"
        persisted_policy_digest: "sha256:<64-lowercase-hex>"
        supplied_requested_frequency: "<write_agent_handoff|task|fase|plano|null>"
        reason: "<non-empty-conflict-reason>"
        next_action: "<minimum-resolution-or-human-review>"
    risks: []
    next_action: "<resume-safe-review-action>"
  next_action: ""
  blocked_by: []
```

Cold-start reconciliation uses only persisted plan/task documents:

- `coverage_manifest.handoffs` and `covered_write_handoff_ids` are sorted by
  handoff ID, and each `changed_files` list is sorted by normalized path;
- a terminal checkpoint is reused without invocation;
- `dispatched` reconciles its existing `review_handoff_id`;
- a task-local coverage digest different from the referenced checkpoint creates
  a new checkpoint and preserves the old one;
- a requested value different from the persisted policy records
  `policy-conflict` and blocks before execution;
- an irrecoverable dispatched result becomes terminal `outcome-unknown`, with a
  reason and risk reference, and is not reinvoked automatically.
