---
title: Workflow de Execucao de Plano do Loki
type: plan-execution-workflow
status: draft
created: 2026-06-26
self_contained: true
---

# Workflow de Execucao de Plano do Loki

Este e o guia humano canonico para entender como uma descricao pequena do que
deve ser implementado vira plano executavel, depois codigo ou artefato aplicado,
e finalmente evidencia para o [Workflow de Aprendizado do Loki](loki-learning-workflow.md).

![[loki-plan-execution-workflow.excalidraw.md]]

## Ideia central

O Loki nao deve pular de uma frase curta direto para escrita em runtime,
framework, engine ou arquivos sensiveis. O fluxo transforma intencao em
evidencia, evidencia em plano, plano em tasks retomaveis, tasks em escrita
serializada e resultado validado em aprendizado.

A execucao termina quando a fase tem artefatos, validadores, evidencias e
estado atualizado. Aprendizado duradouro nao nasce automaticamente nessa etapa:
ele passa pelo workflow de aprendizado.

## Fluxo

1. O usuario traz uma descricao curta, feedback, PRD, NSD ou pedido direto.
2. Se a entrada vier de observacao humana, bug percebido ou validacao manual,
   use `loki:feedback` antes de propor solucao. Ele investiga uma pergunta por
   vez e registra diagnostico sem escrever automaticamente.
3. Use `loki:tech-analysis` quando a decisao exigir evidencias, hipoteses,
   riscos, superficies afetadas, pesquisa condicionada, validators ou gates.
   Quando as fontes forem ruidosas, desconhecidas ou multi-fonte, acione
   `source-researcher` em modo read-only antes da matriz de decisao.
4. Use `loki:generate-action-plan` para transformar a analise aprovada em
   `tasks.md`, `task-N.M.md`, dependencias, human loops, validators e estado de
   retomada.
5. Antes da execucao, use `loki:enrich-tasks` quando retrospectivas, builds,
   interactions ou aprendizados locais puderem reduzir ambiguidade da fase
   atual. Pesquisa externa continua condicionada: a frase exata deve ser
   mostrada ao usuario antes da busca.
6. Use `loki:run-plan` para executar uma fase ou task aprovada. Ele carrega
   `loki-run-plan-execution`, monta um `Execution Brief`, resolve contexto e
   bloqueia escrita quando faltar decisao, validator, approval ou gate humano.
7. `execution-context-reader` pode ler `DIR_ANALISE`, tasks, docs e fontes
   locais em modo read-only para extrair apenas o que afeta a fase alvo.
8. Skills tecnicas entram somente quando a task, o contexto, o usuario ou uma
   retrospectiva aprovada exigir aquela tecnologia.
9. A implementacao acontece task por task, em ordem segura. Leitura pode ser
   paralela; escrita fica serializada por um unico orquestrador.
10. Quando a task tocar runtime, integracao ativa, estado persistido, asset,
    artefato gerado ou comportamento perceptivel, `runtime-qa` produz checklist
    e evidencia esperada, mas nao substitui validacao humana.
11. Ao concluir, atualize `tasks.md`, `task-N.M.md`, `builds/faseN/`,
    `interaction/faseN/` e status de retomada com arquivos afetados,
    validators, human loops, blockers e proximo passo.
12. Quando a fase terminar, pausar claramente ou uma dificuldade real for
    resolvida, passe para `loki:retrospectiva-tecnica` e siga o
    [Workflow de Aprendizado do Loki](loki-learning-workflow.md).

## Artefatos participantes

### Commands

| Command | Contribuicao no workflow |
| --- | --- |
| `loki:feedback` | Normaliza feedback humano, investiga causas e evita escrever com premissas fracas. |
| `loki:tech-analysis` | Converte demanda em analise baseada em evidencias, riscos, alternativas, validators e gates. |
| `loki:generate-action-plan` | Cria plano faseado retomavel com `tasks.md`, tasks individuais, dependencias e human loops. |
| `loki:enrich-tasks` | Melhora apenas a fase atual usando aprendizados transitorios, sem promover regra duradoura. |
| `loki:run-plan` | Orquestra a execucao da fase aprovada, serializa escrita, registra estado e valida evidencias. |
| `loki:retrospectiva-tecnica` | Captura o que realmente aconteceu depois da execucao para alimentar aprendizado. |

### Skills

| Skill | Contribuicao no workflow |
| --- | --- |
| `loki-feedback` | Define o protocolo de uma pergunta por vez, hipoteses com evidencia e proposta so depois de contexto suficiente. |
| `loki-tech-analysis-authoring` | Padroniza analise tecnica, mapa de fontes, matriz de decisao, pesquisa condicionada e handoff para plano. |
| `loki-action-plan-authoring` | Garante que o plano tenha fases, tasks, dependencias, referencias, validators, gates e retomada por disco. |
| `loki-enrich-tasks` | Injeta aprendizados na task certa do plano ativo, preservando fontes sensiveis e sem criar norma duradoura. |
| `loki-run-plan-execution` | Faz preflight, `Execution Brief`, ordem topologica, contexto read-only, escrita serializada, validators e `LokiRunState`. |
| Skills tecnicas opcionais | Entram apenas quando a superficie exige tecnologia especifica, como runtime, engine, framework, dados ou plugins. |

### Agents

| Agent | Contribuicao no workflow |
| --- | --- |
| `execution-context-reader` | Extrai contexto relevante em modo read-only antes da escrita. |
| `source-researcher` | Mapeia fatos, lacunas e conflitos em pesquisa multi-fonte antes de decisao, plano ou execucao. |
| `technical-implementer` | Propoe mudancas tecnicas em modo `proposal-only` quando a escrita for sensivel ou exigir julgamento especializado. |
| `runtime-qa` | Produz checklist de validacao e evidencia esperada para comportamento perceptivel ou runtime. |
| `bibliotecario` | Localiza a menor documentacao duradoura suficiente no projeto consumidor. |
| `catalogador` | Entra depois da execucao, quando aprendizado `project-specific` precisar virar `/docs` do consumidor. |
| `standards-curator` | Entra depois da retrospectiva, quando houver candidato a regra duradoura ou backlog. |

## Gates e pontos de parada

- Pare antes de escrever se `FASE_ATUAL`, `TASKS_MD`, task alvo, referencias,
  validator, approval ou human loop estiverem ausentes ou ambiguos.
- Nao execute plano inteiro quando o usuario pediu apenas uma fase ou task.
- Nao edite runtime, engine, framework, assets, dados persistidos,
  integracoes ou superficies sensiveis sem plano aprovado, skill tecnica
  aplicavel, validator e gate humano.
- Nao declare comportamento perceptivel como validado sem confirmacao humana.
- Nao transforme resultado de execucao diretamente em regra duradoura. A
  promocao acontece no workflow de aprendizado.

## Resultado esperado

Ao fim da execucao, outra LLM deve conseguir retomar pelo disco:

- qual fase ou task foi executada;
- qual `Execution Brief` guiou a escrita;
- quais fontes foram lidas;
- quais arquivos foram alterados;
- quais validators rodaram ou foram bloqueados;
- qual gate humano ficou pendente ou foi satisfeito;
- quais evidencias foram salvas;
- qual retrospectiva ou proximo passo deve alimentar o aprendizado.
