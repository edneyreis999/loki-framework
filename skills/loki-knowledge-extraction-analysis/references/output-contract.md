# Knowledge Extraction Analysis Output Contract

Use this reference after `lf-external-knowledge-extraction` and
`lf-framework-impact-audit` have produced their handoffs.

## Consolidation Rules

- Combine equivalent learnings identified across multiple artifacts.
- Avoid duplicate recommendations.
- Highlight recurring patterns, but separate useful patterns from superficial
  coincidences.
- Identify conflicts between recommendations.
- State which changes belong in specific artifacts, global rules, docs,
  templates, validators, tests, or backlog.
- State which changes should be rejected or investigated further.
- If one learning affects multiple Loki artifacts, produce one consolidated
  recommendation and list all likely application locations.

Do not transform similar observations into redundant recommendations.

## Required Output

Produce a Markdown report titled:

```markdown
# Analise de extracao de conhecimento para o Loki
```

The report must include these sections:

1. How impacted Loki instructions were identified.
2. Selected Loki artifacts potentially affected.
3. Impact of external artifacts on Loki workflows.
4. Individual audit of affected artifacts.
5. Individual impact reports.
6. Consolidation of individual reports.
7. Executive summary.
8. Artifacts analyzed.
9. General result.
10. Identified learnings.
11. Rejected points.
12. Points already covered by Loki.
13. Identified gaps.
14. Identified conflicts.
15. Final recommendations for `loki-continuous-improvement`.
16. No-useful-learning case, when applicable.

## General Result Values

Use one of:

- `ha aprendizados implementaveis`;
- `ha aprendizados apenas conceituais`;
- `ha pontos ja contemplados pelo Loki`;
- `ha pontos incompativeis com o Loki`;
- `nao ha aprendizado util`;
- `contexto insuficiente para recomendacao confiavel`.

Explain the classification.

## Learning Entry Template

For each consolidated learning, use:

```markdown
### Aprendizado [n]: [titulo curto]

**Classificacao:**
adotar | adaptar | rejeitar | ja contemplado | investigar | sem aprendizado util

**Categoria:**
clareza de instrucao | seguranca | autonomia | validacao | reducao de ruido | qualidade de implementacao | consistencia entre artefatos | prevencao de comportamento indesejado | documentacao | estrutura de skill | formato de saida | tratamento de incerteza | priorizacao | outra

**Origem externa:**

**Artefatos do Loki impactados:**

**Relatorios individuais relacionados:**

**Observacao:**

**Interpretacao:**

**Delta em relacao ao Loki:**

**Problema que resolve:**

**Recomendacao para o Loki:**

**Mudanca sugerida:**

**Local provavel de aplicacao:**

**Texto sugerido:**

**Riscos de adocao:**

**Criterios de rejeicao aplicaveis:**

**Prioridade:**
obrigatoria | recomendada | experimental | baixa | rejeitada

**Custo de implementacao:**
baixo | medio | alto

**Ganho esperado:**
baixo | medio | alto

**Teste de validacao:**
```

## Final Recommendation Buckets

Separate recommendations into:

- `Implementar agora`;
- `Adaptar com cautela`;
- `Investigar melhor`;
- `Rejeitar`;
- `Nao alterar`.

Each actionable item must include related learning, affected artifacts, concrete
change, suggested text when applicable, and validation test.

## No Useful Learning Case

When no useful learning exists, answer with:

```markdown
**Conclusao:**
nao ha aprendizado util a incorporar.

**Motivo principal:**

**Artefatos do Loki verificados:**

**Workflows avaliados:**

**O que foi verificado:**

**Explicacao:**

**Recomendacao ao `loki-continuous-improvement`:**
```

Allowed reasons include already covered by Loki, incompatible with Loki,
irrelevant to Loki, too specific to the source artifact, insufficient context,
no practical change, would add noise or complexity, no relevant Loki artifact was
impacted, or `docs/operational-inventory.md` indicates no affected workflow.
