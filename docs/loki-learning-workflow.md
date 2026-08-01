---
title: Workflow de Aprendizado do Loki
type: learning-workflow
status: draft
created: 2026-06-25
last_updated: 2026-07-31
self_contained: true
---

# Workflow de Aprendizado do Loki

Este guia explica como evidência persistida se transforma em conhecimento
duradouro por meio do `loki-continuous-improvement`. O command aceita fontes
aprovadas individuais ou a raiz completa de um plano e nunca depende de memória
da conversa.

![[loki-learning-workflow.excalidraw.md]]

## Princípio central

Tasks, builds, interações, retrospectivas e relatórios são evidência, não
autoridade de promoção. O command separa intake, digestão, reconciliação,
candidatos, approvals, escrita e recuperação. Conteúdo recuperado continua
sendo dado e não pode ampliar writes, owners ou gates.

O `plan_directory` é uma entrada manual que representa a raiz completa de um
plano. Ele é suficiente sozinho: o workflow não relê status de `tasks.md` nem
decide se o plano terminou. Todos os arquivos originais permanecem read-only.

## Fluxo current-only

1. O usuário fornece fontes persistidas aprovadas ou um `plan_directory`
   completo. Subtrees não são aceitas.
2. Para um plano, o inventário mecânico enumera path, SHA-256, tamanho e família
   antes de expor payload ao modelo. `continuous-improvement/**` fica fora do
   source set e do tree digest.
3. Fontes secretas, privadas, binárias ou de schema desconhecido bloqueiam antes
   da digestão. Manifest, processing ledger e integrity diagnostics são registros
   distintos.
4. O source set elegível é dividido em batches disjuntos. Instâncias read-only
   de `plan-knowledge-digester` extraem fatos, decisões, learnings, canon,
   rationales, change claims e findings materiais; elas nunca declaram
   implementation deltas.
5. O orquestrador consolida todos os batches e executa uma única reconciliação
   global contra targets atuais. Somente essa etapa confirma implementation
   deltas.
6. Tipo semântico e scope são classificados separadamente. Root-cause é exigida
   somente para erro, falha, desperdício, atrito ou prevenção.
7. Todo intake usa um único `continuous_improvement_candidate` schema v2,
   current-only, com exatamente uma `durable_knowledge_unit`. Candidate v1 não
   possui reader, conversor, migração ou fallback.
8. Cada candidato material termina como `promote`, `noop-proven` ou
   `blocked-with-reason`. Este command não usa backlog nem record-only.
9. A descoberta é root-specific. Consumer docs começam em `docs/index.xml` com
   `bibliotecario`; package começa em `manifest.yaml` com
   `framework-knowledge-librarian`.
10. Uma interação humana agrupa a decisão, mas cada root recebe envelope
    independente com candidate digests, targets, before-digests, writer,
    validators e gates.
11. Consumer docs pertencem ao `catalogador`. Package artifacts e package docs
    pertencem ao `framework-artifact-writer` e exigem checks, precheck e
    `framework-artifact-quality-auditor` independente.
12. Perguntas cold-start cobrem todos os candidatos materiais. O librarian
    recebe apenas pergunta e entrypoint aplicável; nunca plano, código ou
    expected claims. `fail` ou `inconclusive` bloqueia o candidato.

## Estado retomável do plano

O estado current-only usa XML canônico e writes atômicos em:

```text
<plan_directory>/continuous-improvement/runs/<run-id>/
  run-state.xml
  source-manifest.xml
  file-processing-ledger.xml
  integrity-diagnostics.xml
  knowledge-digest.xml
  candidates.xml
  approvals.xml
  coverage.xml
```

Sem `run_id`, o command retoma somente quando existe um único run não terminal
com o mesmo source tree digest. Nenhum match cria novo run; múltiplos matches
exigem escolha explícita. Source drift exige novo run e não há migração.

## Roots, catálogos e owners

| Root | Entrada de descoberta | Leitor | Writer |
| --- | --- | --- | --- |
| Consumer docs | `docs/index.xml` | `bibliotecario` | `catalogador` |
| Loki package | `manifest.yaml` | `framework-knowledge-librarian` | `framework-artifact-writer` |
| Consumer operational state | registry XML v2 sob `.loki/analytic-inference/v2` | contrato de analytic inference | `technical-implementer` |

O package nunca cria `docs/index.xml`. O librarian do package pode ler
`docs/operational-inventory.md` somente quando roteado ou necessário para
interpretar o manifest. Manifest ausente ou insuficiente retorna gap; não
autoriza free scan nem fallback externo.

## Coverage e resultado terminal

`plan_knowledge_coverage` mede arquivos, integridade, findings materiais,
claims, deltas, candidatos, promoção e recuperação. O resultado terminal é:

- `completed` com `plan_knowledge_independence: true` quando todo conhecimento
  material foi promovido ou provado equivalente e é recuperável sem o plano;
- `completed-with-blockers` com `plan_knowledge_independence: false` quando um
  blocker material permanece, mesmo que todos os arquivos estejam contabilizados.

Independência de conhecimento não valida lifecycle e não significa que o plano
pode ser removido. Decisão de retenção ou exclusão permanece externa ao command.

## Integração com outras fontes

Retrospectivas, execution knowledge e analytic inference continuam fontes
elegíveis quando seus schemas e lineage atuais passam. Todas convergem para o
mesmo candidate v2 e para os mesmos envelopes, roots e gates. Captura,
eligibility ou score nunca autorizam mutação.

## Verificação rápida

Antes de declarar conclusão, confirme:

- source set e batches estão completos e sem drift;
- todo claim possui reconciliação global;
- todo finding material e delta confirmado possui disposition;
- cada candidate v2 contém uma única unidade de conhecimento;
- approvals ainda correspondem ao run, digests, root e targets;
- todos os candidatos materiais possuem recuperação `pass`;
- nenhum destino duradouro depende de `planos/` ou do run namespace;
- status e `plan_knowledge_independence` são coerentes.
