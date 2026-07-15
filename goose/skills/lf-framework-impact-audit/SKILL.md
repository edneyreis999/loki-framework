---
name: lf-framework-impact-audit
description: Audita como aprendizados externos extraídos impactam artefatos, workflows e contratos do Loki usando o inventário operacional antes de recomendações finais.
---

# lf-framework-impact-audit

## Objetivo

Use esta skill depois de receber um handoff `external_extraction`. Ela identifica artefatos Loki potencialmente afetados, audita impactos de forma independente e devolve um handoff `impact_audit` para consolidação.

## Procedimento

1. Leia `docs/operational-inventory.md` antes de selecionar artefatos Loki. Se estiver ausente ou insuficiente, declare limitação.
2. Use `external_extraction` como entrada; não reextraia artefatos externos salvo lacuna ou contradição material.
3. Liste artefatos Loki considerados e classifique impacto como `alto`, `medio`, `baixo`, `incerto` ou `nenhum impacto relevante`.
4. Audite individualmente apenas impactos `alto`, `medio` ou `incerto`; mencione baixo impacto só quando útil.
5. Para cada auditoria, registre:
   - função do artefato no Loki;
   - parte impactada;
   - delta identificado;
   - lacunas, redundâncias e conflitos;
   - oportunidade concreta;
   - recomendação por artefato;
   - risco, prioridade e teste de validação.
6. Consolide achados sem apagar rastreabilidade por artefato.
7. Retorne `impact_audit` para o orquestrador principal.

## Limites

- Não promover nem aplicar mudanças.
- Não inventar arquivos, workflows ou relações não visíveis no inventário ou em arquivos lidos.
- Não tratar popularidade externa como prova de adequação ao Loki.
- Não colapsar conclusões de artefatos diferentes sem evidência.

## Handoff esperado

```yaml
impact_audit:
  inventory_status: "read | unavailable | incomplete | insufficient"
  loki_artifacts_considered: []
  workflow_impacts: []
  individual_reports: []
  consolidated_findings:
    gaps: []
    redundancies: []
    conflicts: []
    opportunities: []
    no_change_reasons: []
```
