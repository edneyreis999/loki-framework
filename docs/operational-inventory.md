---
title: Inventario Operacional do Loki Framework Local
status: completed
created: 2026-06-24
type: operational-inventory
self_contained: true
---

# Inventario Operacional do Loki Framework Local

Este inventario lista os componentes incluidos ou planejados no pacote `loki-framework-local`. As decisoes do blueprint aprovado foram internalizadas aqui; o pacote nao exige leitura de arquivos externos para operar.

Status permitidos nesta fase:

- `mvp`: componente do pacote inicial.
- `optional-extension`: componente especializado carregado apenas quando o
  projeto consumidor exigir aquela tecnologia.
- `backlog`: candidato futuro, fora do primeiro pacote operacional.
- `reference-only`: fonte de inspiracao ou evidencia, sem virar componente instalavel agora.

O relacionamento entre brief, analise, plano, execucao e validacao esta em
[Workflow de Execucao de Plano do Loki](loki-plan-execution-workflow.md). O
relacionamento entre `loki:enrich-tasks`, `loki:retrospectiva-tecnica` e
`loki:continuous-improvement` esta em
[Workflow de Aprendizado do Loki](loki-learning-workflow.md).

## Commands

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `loki:feedback` | `mvp` | Investigar feedback por entrevista, uma pergunta por vez, sem escrita automatica. |
| `loki:tech-analysis` | `mvp` | Produzir analise tecnica agnostica e baseada em evidencias antes de plano ou execucao. |
| `loki:generate-action-plan` | `mvp` | Gerar plano faseado com tasks, dependencias, human loops e estrutura de artefatos. |
| `loki:enrich-tasks` | `mvp` | Revisar tasks usando aprendizados anteriores, interactions e research gate condicionado sem expor fontes internas nem promover regra duradoura diretamente. |
| `loki:run-plan` | `mvp` | Executar fase planejada com leitura paralela, escrita serializada, validators e gates. |
| `loki:retrospectiva-tecnica` | `mvp` | Registrar retrospectiva tecnica reutilizavel ao fim de uma fase ou apos uma dificuldade real ser resolvida de fato. |
| `loki:continuous-improvement` | `mvp` | Promover aprendizados validados para superficies duradouras com fonte, destino, verificacao e aprovacao humana. |
| `loki:criar-nsd` | `backlog` | Conduzir entrevista narrativa quando o contrato de NSD for normalizado. |
| `loki:ai-enemy-optimizer` | `backlog` | Gerar comportamento de inimigos por contrato de dominio especializado. |
| `loki:brainstorm-phase-1-create-boss` | `backlog` | Criar conceito inicial de boss com escopo narrativo/gameplay. |
| `loki:brainstorm-phase-2-detail-boss` | `backlog` | Detalhar boss em especificacao jogavel. |
| `zord:generate-action-plan` | `reference-only` | Base estrutural para o comando Loki equivalente. |
| `zord:run-plan` | `reference-only` | Base estrutural para executor Loki com gates do runtime do consumidor. |
| `zord:troubleshoot` | `reference-only` | Inspiracao para debug iterativo futuro. |
| `zord:entrevistador` | `reference-only` | Inspiracao para entrevistas com uma pergunta por vez. |

## Skills

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `loki-command-workflows` | `mvp` | Skill agregadora para carregar contratos `loki:*` a partir de `commands/` no Codex. |
| `loki-feedback` | `mvp` | Procedimento de diagnostico de feedback antes de propor escrita. |
| `loki-tech-analysis` | `mvp` | Wrapper Codex para executar o workflow `loki:tech-analysis`. |
| `loki-generate-action-plan` | `mvp` | Wrapper Codex para executar o workflow `loki:generate-action-plan`. |
| `loki-enrich-tasks` | `mvp` | Procedimento de enriquecimento cirurgico de tasks com retrospectivas, builds, interactions, resolucao de ambiguidades e research gate condicionado sem handoff normativo direto. |
| `loki-run-plan` | `mvp` | Wrapper Codex para executar o workflow `loki:run-plan`. |
| `loki-run-plan-execution` | `mvp` | Procedimento de preflight e execucao de fase com Execution Brief, dependencias, contexto read-only, escrita serializada, validators e estado retomavel. |
| `loki-retrospectiva-tecnica` | `mvp` | Procedimento de retrospectiva tecnica apos fase concluida, pausada claramente ou dificuldade resolvida de fato. |
| `loki-continuous-improvement` | `mvp` | Wrapper Codex para executar o workflow `loki:continuous-improvement`. |
| `loki-template-library` | `mvp` | Expor templates do pacote como referencias instalaveis por skill. |
| `loki-index-navigator` | `mvp` | Navegar `docs/index.xml` do projeto consumidor com fallback controlado para `index.md` legado. |
| `loki-tech-analysis-authoring` | `mvp` | Criar e revisar analises tecnicas Loki baseadas em evidencias, com mapa de fontes, pesquisa condicionada, matriz de decisao, validators e handoff para plano. |
| `loki-action-plan-authoring` | `mvp` | Criar e revisar planos Loki executaveis por outro agente, com fases, tasks, dependencias, referencias, validators e validacao observavel. |
| `loki-command-creator` | `mvp` | Skill operacional para criar ou revisar commands quando `loki:continuous-improvement` direcionar mudanca para `commands/`. |
| `loki-agent-creator` | `mvp` | Skill operacional para criar ou revisar agents quando `loki:continuous-improvement` direcionar mudanca para `agents/`. |
| `loki-skill-creator` | `mvp` | Skill operacional para criar ou revisar skills quando `loki:continuous-improvement` direcionar mudanca para `skills/`. |
| `task-onboarding` | `reference-only` | Inspiracao historica internalizada em `loki-run-plan-execution`. |
| `brainstorm-character` | `backlog` | Apoio futuro para design de personagens e bosses. |

## Agents

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `standards-curator` | `mvp` | Avaliar promocao de aprendizados validados para pacote Loki, documentacao duradoura do consumidor ou backlog. |
| `runtime-qa` | `mvp` | Avaliar feedback, checklist de validacao humana e evidencias perceptiveis como proposta. |
| `execution-context-reader` | `mvp` | Extrair contexto read-only de `DIR_ANALISE`, tasks, docs e fontes locais para alimentar `loki:run-plan` sem escrever. |
| `source-researcher` | `mvp` | Mapear fatos, lacunas e conflitos em pesquisa multi-fonte antes de analise, plano, feedback, enriquecimento ou promocao. |
| `technical-implementer` | `mvp` | Propor mudancas tecnicas em modo `proposal-only`; nao escreve diretamente no MVP. |
| `bibliotecario` | `mvp` | Navegar a documentacao duradoura do consumidor via `docs/index.xml`, recomendando a menor leitura suficiente. |
| `catalogador` | `mvp` | Manter `docs/**/*.md`, `docs/index.xml` e sincronizacao minima em `AGENTS.md` e `CLAUDE.md` do consumidor. |
| `narrative-designer` | `backlog` | Apoiar NSD, dialogo e integracao narrativa em escopo futuro. |
| `prompt-engineer` | `reference-only` | Apoiar consolidacao de instrucoes reutilizaveis em comandos depois que contratos existirem. |
| `context-engineer-optimization` | `reference-only` | Inspirar melhoria continua e promocao de contexto sem copiar estruturas externas literalmente. |

## Codex Agents

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `codex/agents/*.toml` | `mvp` | Fonte versionada derivada de `agents/*.md` para custom agents Codex em `.codex/agents/`. |

## Scripts

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `scripts/install-loki-symlinks.py` | `mvp` | Instalar skills, commands, agents, templates e TOMLs Codex em destino consumidor por symlink, com `--dry-run`, `--yes`, conflito seguro, `--replace` controlado e manifest de instalacao. |

## Templates

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `tasks-template.md` | `mvp` | Registrar fases, objetivos, validacao observavel, dependencias, human loops, validators e estado de retomada. |
| `task-template.md` | `mvp` | Detalhar objetivo, contexto, requisitos, referencias, passos, validators, human loop, Definition of Done e resume notes de cada task. |
| `technical-analysis-template.md` | `mvp` | Padronizar analise tecnica com fontes, fatos, inferencias, hipoteses, research gate, matriz de decisao, validators e handoff. |
| `interaction/faseN/*.md` | `mvp` | Registrar perguntas, recomendacoes, decisoes e pendencias humanas. |
| `retrospetivas/faseN/*.md` | `mvp` | Registrar aprendizados tecnicos pos-fase. |
| `builds/faseN/*` | `mvp` | Guardar evidencias e scripts auditaveis quando houver escrita automatizada. |
| `command-contract-template.md` | `mvp` | Padronizar frontmatter, entradas, saidas, skills, gates e handoffs de comandos. |
| `component-contract-template.md` | `mvp` | Padronizar descricao operacional de agents, commands e skills. |
| `project-doc-index-template.xml` | `mvp` | Base para criar `docs/index.xml` no projeto consumidor e catalogar documentacao duradoura. |
| `templates-xml-zord` | `reference-only` | Referencia estrutural, sem formato obrigatorio no MVP Loki. |

## Docs

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `docs/source-boundaries.md` | `mvp` | Declarar fonte canonica, limites e politica de conflito do pacote. |
| `docs/operational-inventory.md` | `mvp` | Listar componentes operacionais a gerar. |
| `docs/usage-guide.md` | `mvp` | Explicar uso do framework em ate 2000 tokens. |
| `docs/loki-plan-execution-workflow.md` | `mvp` | Explicar o workflow canonico de execucao de plano, da descricao curta ate codigo, validacao e handoff para aprendizado. |
| `docs/loki-plan-execution-workflow.excalidraw.md` | `mvp` | Ilustrar a participacao de commands, skills e agents no workflow de execucao. |
| `docs/loki-learning-workflow.md` | `mvp` | Explicar o workflow canonico de aprendizado, retrospectiva e promocao de contexto duradouro. |
| `docs/loki-learning-workflow.excalidraw.md` | `mvp` | Ilustrar a participacao de commands, skills e agents no workflow de aprendizado. |
| `docs/package-authoring-guardrails.md` | `mvp` | Registrar preflight, regras estruturais, classificacao de referencias e validacoes para evoluir o pacote. |
| `docs/project-context-catalog.md` | `mvp` | Definir como o Loki usa `/docs` e `docs/index.xml` do projeto consumidor sem contaminar o pacote. |
| `README.md` | `mvp` | Explicar instalacao local em Claude Code e Codex. |
| `manifest.yaml` | `mvp` | Declarar pacote, versao, componentes e destinos locais. |
| Fontes historicas externalizadas | `reference-only` | Usadas como origem antes da publicacao do pacote; nao sao dependencias operacionais. |

## Extensoes Opcionais: RPG Maker MZ

Os itens abaixo sao exemplos de especializacao por tecnologia. Eles nao fazem
parte do fluxo obrigatorio do core Loki e devem ser carregados somente quando o
projeto consumidor declarar RPG Maker MZ.

### Commands

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `loki:implementar-enemy` | `optional-extension` | Implementar inimigos em database RPG Maker MZ depois de validar gates da tecnologia. |
| `loki:action-sequence-generator` | `optional-extension` | Gerar Action Sequences VisuStella por contrato especializado. |
| `loki:visustella-add-postmortem` | `optional-extension` | Promover aprendizados VisuStella com gate de aprovacao. |

### Skills

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `loki-rpg-maker-mz-data-json` | `optional-extension` | Skill especializada para superficies de dados, Database, Common Events ou mapas RPG Maker MZ. |
| `loki-rpg-maker-mz-plugin-workflow` | `optional-extension` | Skill especializada para criar, editar, validar ou ativar plugins RPG Maker MZ. |
| `notetag-filler` | `optional-extension` | Apoio futuro para notetags RPG Maker MZ/VisuStella. |
| `visustella-analyst` | `optional-extension` | Apoio futuro para analise tecnica/debug em projetos com VisuStella. |

## Pendencias Futuras Registradas

| Pendencia | Status | Motivo |
| --- | --- | --- |
| Escrita direta por `technical-implementer` | `backlog` | MVP permite apenas `proposal-only`; escrita sensivel exigira aprovacao humana futura. |
| Politica de alocacao em superficies runtime especializadas | `backlog` | Nao necessaria para pacote documental; exigira decisao antes de alterar runtime. |
| Renomeacao de namespaces antigos | `backlog` | Nao renomear comandos historicos automaticamente. |

## Conclusao

O inventario operacional separa `agents`, `commands`, `skills`, `templates` e `docs`. O pacote deve permanecer autocontido para instalacao em outros projetos.
