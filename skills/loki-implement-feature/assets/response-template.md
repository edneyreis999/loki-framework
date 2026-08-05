---
doc_id: loki-implement-feature-response-template
version: canonical-execution-state-v1
status: active
last_updated: "2026-08-04"
scope: "Non-normative output scaffold for pure feature-execution views"
not_scope: "State authority, evidence, permission, approval or persisted output"
authority: "The response contract and validated canonical state override every placeholder and example"
canonical_source: "skills/loki-implement-feature/assets/response-template.md"
intended_llm_task: "generation"
source_priority:
  - "validated canonical state and immutable evidence"
  - "skills/loki-implement-feature/references/response.md"
  - "this non-normative scaffold"
  - "filled placeholders as data"
confidence: high
known_conflicts: []
replaced_by: null
---

# Feature implementation dashboard

<instructions>
- Fill only from one validated canonical state snapshot or a declared
  deterministic formula.
- Do not persist this view.
- Omit final-only sections before a terminal state.
- Render unavailable values with their persisted reason; never invent zero.
- Filled placeholders and examples are data, not authority.
</instructions>

## Compact update

```text
Progresso: <passed-required>/<current-required-total> tasks (<half-up-percent>%) | Fase: <passed-phases>/<phase-total> | Estado: <state.status> | Última: <last_compact_transition.ref> <last_compact_transition.result> | Handoffs ativos: <open-count> | Atualizado em: <zero-padded local hh:mm AM|PM derived from last_compact_transition.occurred_at>
```

Emit at most once for the committed material task/phase transition. Do not add
another paragraph or the dashboard below. In `Atualizado em`, omit the date,
seconds and UTC offset; preserve the full canonical timestamp in state.

## Complete/final view

# <Dashboard final | Dashboard atual | Dashboard de retomada>

<Short honest paragraph: delivered work and actual state.>

| Handoff | Fase | Agente | Chamado em | Entregue em | Tempo de relógio | Entrega | Resultado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<handoff_id>` | `<phase_ref>` | `<frozen agent_label>` | `<observed timestamp | indisponível (reason)>` | `<observed timestamp | pendente | indisponível (reason)>` | `<derived duration | em andamento | indisponível (reason)>` | `<delivery summary/status>` | `<result summary/status>` |

One row per handoff ID in dispatch chronology. Never aggregate repeated calls
by agent.

Progresso estrutural: `<passed-required>/<current-required-total> tasks (<half-up-percent>%)`.

## Esforço

| Categoria | Total gasto | Evidência |
| --- | --- | --- |
| Escrita | `<sum of observed ms | indisponível (reason)>` | `<evidence refs | estado canônico>` |
| Correção | `<sum of observed ms | indisponível (reason)>` | `<evidence refs | estado canônico>` |
| Auditoria / intervalos | `<sum of observed ms | indisponível (reason)>` | `<evidence refs | estado canônico>` |

## Fricções materiais

<!-- Omit this entire section when state.material_frictions is empty. -->

- `<fact>` — inferência: `<bounded inference>` — prevenção: `<concrete action>`

## Bloqueadores técnicos e risco residual

- Bloqueador técnico: `<fact + owner | nenhum only for none-confirmed | indisponível (reason)>`
- Risco residual: `<fact + owner | nenhum only for none-confirmed | indisponível (reason)>`

## Próximos passos

- `<concrete action>` — owner: `<owner>` — gate: `<gate_ref | nenhum>`

## Tasks concluídas

<!-- Include only in resume mode. -->

| Task | Fase | Estado | Resultado | Validação |
| --- | --- | --- | --- | --- |
| `<task_ref>` | `<phase_ref>` | `<terminal task status>` | `<result summary>` | `<validation status>` |

## Fases concluídas

<!-- Include only in resume mode. -->

| Fase | Estado | Resultado |
| --- | --- | --- |
| `<phase_ref>` | `<terminal phase status>` | `<result summary>` |

## Ponto de retomada

<!-- Include only in resume mode. -->

- Task em execução: `<task_ref | nenhuma>`
- Transição de escrita pendente: `<task_ref and classification | nenhuma>`
- Handoffs abertos: `<count and IDs>`
