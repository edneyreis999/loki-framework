---
name: loki-knowledge-extraction-analysis
description: Orquestra análise Goose-first de artefatos externos para extrair aprendizados rastreáveis para o Loki, auditando impacto antes de consolidar recomendações para continuous improvement, sem promover mudanças diretamente.
---

# loki-knowledge-extraction-analysis

## Objetivo

Use esta skill quando uma Goose Recipe precisar executar o fluxo de `loki:knowledge-extraction-analysis`: mapear artefatos externos, extrair aprendizados sem forçar recomendações, auditar impacto no Loki e consolidar um relatório Markdown consumível por `loki:continuous-improvement`.

## Procedimento

1. Valide que há pelo menos um artefato externo, escopo ou fonte de comparação. Se não houver, pare por stop condition.
2. Confirme o Loki root e leia fontes duráveis mínimas, especialmente `docs/operational-inventory.md`, quando a auditoria de impacto começar.
3. Execute primeiro a fase `external_extraction`:
   - liste artefatos externos considerados;
   - separe observação, interpretação e candidato de aprendizado;
   - classifique cada candidato como `adotar`, `adaptar`, `rejeitar`, `ja contemplado`, `investigar` ou `sem aprendizado util`;
   - aplique o princípio de não-forçamento.
4. Execute depois a fase `impact_audit`:
   - use `docs/operational-inventory.md` para escolher artefatos Loki possivelmente afetados;
   - audite individualmente artefatos com impacto `alto`, `medio` ou `incerto`;
   - registre deltas, lacunas, redundâncias, conflitos, oportunidades, riscos e testes.
5. Consolide os handoffs sem duplicar recomendações equivalentes.
6. Produza o relatório final `# Analise de extracao de conhecimento para o Loki` com as seções exigidas pela recipe principal.
7. Recomende o próximo passo para `loki:continuous-improvement` quando houver aprendizados implementáveis; caso contrário, registre explicitamente a ausência de aprendizado útil.

## Princípio de não-forçamento

Só apresente recomendação quando todos forem verdadeiros:

- resolve problema real ou reduz ambiguidade prática;
- é compatível, adaptável ou conscientemente rejeitável em relação ao Loki;
- pode virar mudança concreta em skill, comando, regra, documentação, template, validator ou teste;
- tem origem rastreável;
- não duplica o Loki sem ganho de clareza, estrutura ou economia.

Se os critérios falharem, classifique como já contemplado, incompatível, irrelevante, específico demais, sem evidência suficiente ou não aplicável.

## Limites

- Não aplicar mudanças em commands, skills, agents, templates, validators, docs consolidados, manifest ou runtime.
- Não usar planos, blueprints, `.agents/**`, `.codex/**` ou `.claude/**` como fonte normativa do pacote.
- Não alegar cobertura do Loki sem arquivo lido ou inventário visível.
- Pesquisa externa exige autorização explícita quando for material.

## Saída esperada

O relatório final deve incluir, no mínimo:

1. Como instruções Loki impactadas foram identificadas.
2. Artefatos Loki selecionados.
3. Impacto em workflows.
4. Auditoria individual de artefatos.
5. Consolidação.
6. Resumo executivo.
7. Artefatos analisados.
8. Resultado geral.
9. Aprendizados identificados.
10. Pontos rejeitados, já cobertos, lacunas e conflitos.
11. Recomendações finais para `loki:continuous-improvement`.
12. Caso de ausência de aprendizado útil, quando aplicável.
