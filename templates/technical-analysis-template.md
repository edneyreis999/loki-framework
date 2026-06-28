---
title: "<analysis-title>"
type: loki-technical-analysis
status: draft
created: "<YYYY-MM-DD>"
---

# Analise Tecnica - <analysis-title>

## Objective

<Resultado esperado e como esta analise sera usada.>

## Source Request

- <brief, PRD, NSD, feedback, pedido direto ou decisao humana>

## Execution Effort

```yaml
execution_effort: high
model_class: frontier_reasoning
escalation_reason: "<conflicting evidence | architecture | security | current external research | irreversible decision | none>"
recommended_handoffs:
  research: "<source-researcher|none>"
  planning: "loki:generate-action-plan"
validator_effort: "<low|medium|high>"
```

Analises geradas por `loki:tech-analysis` sao artefatos transientes, mas devem
ser produzidas com high effort por padrao porque orientam decisoes, riscos,
validators e planos futuros.

## Scope

- <superficie, comportamento ou decisao tecnica permitida>

## Out Of Scope

- <superficie, comportamento ou decisao fora desta analise>

## Sources Read

| Source | Kind | Evidence Extracted | Used For |
| --- | --- | --- | --- |
| <path, doc, command, API or URL> | <local/external/user-decision> | <fato extraido> | <decisao, risco ou contrato> |

## Evidence Classification

### Facts

- <fato confirmado e referencia>

### Inferences

- <conclusao inferida a partir dos fatos listados>

### Hypotheses

- <hipotese, status da verificacao e proximo check>

### Open Questions

- <pergunta pendente ou `none`>

## Affected Surfaces

### Runtime, Engine or Framework

- <consumer runtime surface ou `none`>

### Integration Points

- <API, plugin, command, workflow, event, file contract ou `none`>

### State and Data Contracts

- <schema, ID, persistence, generated data, variable, flag ou `none`>

## Research Gate

**Decision:** <not-needed/skipped/performed>
**Reason:** <por que pesquisa externa foi ou nao necessaria>

| Source | Finding | Impact |
| --- | --- | --- |
| <URL, official doc, provider or `none`> | <fato externo> | <decisao afetada> |

## Decision Matrix

| Option | Evidence | Pros | Cons | Decision |
| --- | --- | --- | --- | --- |
| Local/native approach | <referencia> | <beneficio> | <risco> | <use/reject/defer> |
| Dependency/plugin/framework | <referencia> | <beneficio> | <risco> | <use/reject/defer> |
| Custom implementation | <referencia> | <beneficio> | <risco> | <use/reject/defer> |
| Defer or block | <referencia> | <beneficio> | <risco> | <use/reject/defer> |

## Recommendation

<Abordagem recomendada e justificativa tecnica.>

## Risks and Mitigations

| Risk | Evidence | Mitigation | Owner/Gate |
| --- | --- | --- | --- |
| <risco> | <referencia> | <mitigacao> | <validator ou human gate> |

## Validators

- <comando, parser, teste, inspecao estrutural ou `none`>

## Human Gates

- <interview/approval/human-validation/technical-review ou `none`>

## Affected Docs

- <doc duradouro possivelmente afetado ou `none`>

## Stop Conditions

- <condicao que bloqueia plano ou execucao>

## Handoff To Action Plan

- **Recommended next command:** `loki:generate-action-plan`
- **Plan input summary:** <escopo, decisao, riscos e validators que o plano deve preservar>
- **Required skills:** <loki ou technology_required_skills>
- **Downstream execution profile:** <model_class, execution_effort,
  recommended_handoffs e validator_effort que o plano deve preservar>

## Resume State

```yaml
loki_technical_analysis_state:
  status: "draft"
  sources_read: []
  pending_questions: []
  next_action: ""
  blocked_by: []
```
