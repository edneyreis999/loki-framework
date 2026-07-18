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
relacionamento entre `loki-enrich-tasks`, `loki-retrospectiva-tecnica` e
`loki-continuous-improvement` esta em
[Workflow de Aprendizado do Loki](loki-learning-workflow.md).
As regras de classe de modelo, effort e projecao por adaptador estao em
[Model and Effort Guidance for Loki Artifacts](model-effort-guidance.md).

## Command Bundles And Command Backlog

Os componentes `loki-*` ativos abaixo são commands operacionais serializados em
`skills/loki-<stem>/`. Cada bundle reúne entrypoint, execution, response e asset;
não existe projection ou command físico separado.

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `loki-init` | `mvp` | Inicializar docs do consumidor com `init_inventory_domain_investigator` read-only/proposal-only, packets schema v1 e materializacao serial exclusiva por `catalogador` em bootstrap, publication batch e final reconciliation, com cobertura e retomada. |
| `loki-catalogar-docs` | `mvp` | Catalogar documentacao duradoura do consumidor em `/docs` com validacao de caminho, limites de recursao, bottom-up e fan-out disjunto via envelopes do `catalogador`, consolidando `docs/index.xml` de forma serial. |
| `loki-criar-branch` | `mvp` | Criar branch Git local com base, nome, colisao e mudancas locais validadas antes de qualquer escrita. |
| `loki-commit` | `mvp` | Criar commit local com staging explicito, mensagem convencional, bloqueio de branch default e validacao de diff/status. |
| `loki-abrir-pr` | `mvp` | Abrir Pull Request a partir da branch atual usando GitHub MCP quando disponivel ou `gh` autenticado como fallback, com push e PR aprovados. |
| `loki-feedback` | `mvp` | Investigar feedback por entrevista, uma pergunta por vez, sem escrita automatica. |
| `loki-demand-text-improver` | `mvp` | Enriquecer uma demanda inicial em um unico Markdown antes de analise ou planejamento, com planning state confirmado por metadata confiavel, destination existente e gravavel, naming deterministico e nenhum workflow posterior automatico. |
| `loki-tech-analysis` | `mvp` | Produzir analise tecnica agnostica e baseada em evidencias antes de plano ou execucao. |
| `loki-human-decision-preflight` | `mvp` | Classificar decisoes humanas pendentes antes do plano como perguntar agora, delegar ao plano, validar depois ou responder por fonte local. |
| `loki-agentic-development` | `mvp` | Executar o caminho integrado v2: receber demanda simples, conduzir analise agentica, resolver gates materiais antes do plano, gerar plano, executar fases autonomamente, registrar evidencias, digest e backlog, preservando `loki-run-plan` como executor manual. |
| `loki-generate-action-plan` | `mvp` | Gerar plano faseado com tasks, dependencias, human loops e estrutura de artefatos. |
| `loki-enrich-tasks` | `mvp` | Revisar tasks usando aprendizados anteriores, interactions e research gate condicionado sem expor fontes internas nem promover regra duradoura diretamente. |
| `loki-run-plan` | `mvp` | Executar fase planejada com preflight pessoal de contexto, escrita serializada, `catalogador` exclusivo para docs do consumidor, validators, gates e retomada. |
| `loki-retrospectiva-tecnica` | `mvp` | Registrar retrospectiva tecnica reutilizavel ao fim de uma fase ou apos uma dificuldade real ser resolvida de fato. |
| `loki-continuous-improvement` | `mvp` | Promover aprendizados validados para superficies duradouras com fonte, destino, verificacao e aprovacao humana. |
| `loki-knowledge-extraction-analysis` | `mvp` | Analisar artefatos externos e extrair aprendizados rastreaveis, nao forcados e consumiveis por `loki-continuous-improvement`. |
| `loki-deep-research` | `mvp` | Conduzir pesquisa profunda multiagentica na internet, com uma trilha `source-researcher` por subpesquisa em modo deep/deeper, fontes citadas, verificacao cruzada, contradicoes, assumptions e handoff compacto para analise, plano ou decisao. |
| `loki-self-healing` | `mvp` | Auditar artefatos internos do pacote pelos contratos canonicos dos tres creators e aplicar correcoes escopadas no working tree sem stage ou commit automatico. |
| `loki-criar-nsd` | `backlog` | Conduzir entrevista narrativa quando o contrato de NSD for normalizado. |
| `loki-ai-enemy-optimizer` | `backlog` | Gerar comportamento de inimigos por contrato de dominio especializado. |
| `loki-brainstorm-phase-1-create-boss` | `backlog` | Criar conceito inicial de boss com escopo narrativo/gameplay. |
| `loki-brainstorm-phase-2-detail-boss` | `backlog` | Detalhar boss em especificacao jogavel. |
| `zord:generate-action-plan` | `reference-only` | Base estrutural para o comando Loki equivalente. |
| `zord:run-plan` | `reference-only` | Base estrutural para executor Loki com gates do runtime do consumidor. |
| `zord:troubleshoot` | `reference-only` | Inspiracao para debug iterativo futuro. |
| `zord:entrevistador` | `reference-only` | Inspiracao para entrevistas com uma pergunta por vez. |

A matriz caller/mode do `catalogador` e fechada: `loki-init` usa
`init-bootstrap-cataloger`, `init-publication-batch` e
`init-final-reconciliation`; `loki-continuous-improvement` e `loki-run-plan`
usam `task_scoped_writer`; `loki-catalogar-docs` usa `task_scoped_writer` ou
`proposal-only`. Combinacoes ausentes ou cruzadas bloqueiam antes da escrita.

## Support Skills

Esta seção lista skills `lf-*` e de domínio/tecnologia. Elas fornecem
conhecimento reutilizável; não são mini-orquestradores nem duplicam os command
bundles.

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `lf-command-workflows` | `mvp` | Skill agregadora para carregar comandos Loki compartilhados disponiveis no perfil instalado. |
| `lf-internal-command-workflows` | `mvp` | Skill internal-only para rotear apenas extracao de conhecimento e self-healing; melhoria continua permanece `both` no router publico. |
| `lf-agentic-orchestration` | `mvp` | Skill auxiliar para preflight de agentes, fan-out selecionado, estado XML, gates, cross-review, reports, liveness, invalidacao, digest, backlog e retrospectivas por agente. |
| `lf-run-plan-execution` | `mvp` | Procedimento de execucao com Execution Brief, dependencias, preflight pessoal de dominio, owners escopados, escrita serializada, validators e estado retomavel. |
| `lf-domain-context-preflight` | `mvp` | Preflight pessoal reutilizavel para docs minimas, fontes atuais, freshness, conflitos e lacunas, sem autocorrecao de docs. |
| `lf-external-knowledge-extraction` | `mvp` | Extrair observacoes, padroes, exemplos, riscos e aprendizados candidatos de artefatos externos sem decidir mudancas no Loki. |
| `lf-framework-impact-audit` | `mvp` | Auditar o impacto de aprendizados externos em artefatos e workflows do Loki usando `docs/operational-inventory.md`. |
| `lf-git-workflow` | `mvp` | Procedimento compartilhado para branch, commit e PR com preflight Git, staging seguro, gates humanos e GitHub MCP/`gh` fallback. |
| `lf-web-deep-research` | `mvp` | Procedimento reutilizavel de pesquisa profunda na internet com ondas de busca, avaliacao de fontes, contradicoes, assumptions, lacunas e output estruturado. |
| `lf-agent-execution-evidence` | `mvp` | Definir, coletar e revisar evidencia provider-neutral de execucao, com identidade tipada, snapshot sanitizado, lacunas explicitas e proveniencia de uso sem registrar raciocinio privado. |
| `lf-template-library` | `mvp` | Expor templates do pacote como referencias instalaveis por skill. |
| `excalidraw-diagram-generator` | `mvp` | Gerar diagramas Excalidraw para enriquecer documentacao rica de workflows, processos, arquitetura e relacoes. |
| `lf-index-navigator` | `mvp` | Navegar `docs/index.xml` do projeto consumidor com fallback controlado para `index.md` legado. |
| `lf-tech-analysis-authoring` | `mvp` | Criar e revisar analises tecnicas Loki baseadas em evidencias, com mapa de fontes, pesquisa condicionada, matriz de decisao, validators e handoff para plano. |
| `lf-action-plan-authoring` | `mvp` | Criar e revisar planos Loki executaveis por outro agente, com fases, tasks, dependencias, referencias, validators e validacao observavel. |
| `lf-command-creator` | `mvp` | Fonte compartilhada do contrato 24/24 para criar ou revisar command bundles com Input, Execution, Response, owners, gates, validators e retomada. |
| `lf-agent-creator` | `mvp` | Fonte compartilhada do contrato de agents por capacidades e modos, com envelope de escrita, validação e handoff claro. |
| `lf-skill-creator` | `mvp` | Fonte compartilhada do contrato 24/24 para criar ou revisar skills com capacidade única, metadata válida, progressive disclosure e forward testing. |
| `task-onboarding` | `reference-only` | Inspiracao historica internalizada em `lf-run-plan-execution`. |
| `brainstorm-character` | `backlog` | Apoio futuro para design de personagens e bosses. |

## Agents

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `standards-curator` | `mvp` | Avaliar promocao de aprendizados validados para pacote Loki, documentacao duradoura do consumidor ou backlog. |
| `retrospective-digester` | `mvp` | Digerir retrospectivas tecnicas em modo read-only, com fan-out por arquivo, retornando aprendizados, atritos, candidatos e evidencias para `loki-continuous-improvement`. |
| `runtime-qa` | `mvp` | Avaliar feedback, checklist de validacao humana e evidencias perceptiveis; pode escrever reports/evidencias quando uma task atribuir target_files. |
| `framework-artifact-writer` | `draft-scoped-writer` | Writer interno do pacote: recebe envelope de task com targets exatos, aplica promocao package-only e entrega checks ao auditor; nao atua em consumidor ou runtime. |
| `framework-artifact-quality-auditor` | `draft-write-test` | Auditor interno read-only: executa checks e rubrica independente sobre patch de pacote, bloqueia findings/incertezas e nunca corrige producao. |
| `execution-context-reader` | `mvp` | Extrair contexto read-only de `DIR_ANALISE`, tasks, docs e fontes locais para alimentar `loki-run-plan` sem escrever. |
| `source-researcher` | `mvp` | Mapear fatos, lacunas e conflitos em pesquisa multi-fonte antes de analise, plano, feedback, enriquecimento ou promocao. |
| `session-evidence-auditor` | `mvp` | Auditar em modo read-only manifests de evidencia de sessao ja validados, sem inventar identidade, transcritos, uso de tokens ou raciocinio privado. |
| `technical-implementer` | `mvp` | Pode aplicar mudancas tecnicas como `scoped-writer` quando a task atribuir target_files; caso contrario, retorna proposta. |
| `bibliotecario` | `mvp` | Navegar a documentacao duradoura do consumidor via `docs/index.xml`, recomendando a menor leitura suficiente. |
| `catalogador` | `mvp` | Unico writer de docs duradouros do consumidor; exige caller/mode, fontes e targets explicitos para manter `docs/**/*.md`, `docs/index.xml` e sincronizacao minima aprovada. |
| `game-product-owner` | `mvp` | Refinar objetivos, valor, prioridade e criterios de aceite para stories de jogo. |
| `game-business-analyst` | `mvp` | Converter brief de jogo em requisitos, regras e lacunas verificaveis para refinamento. |
| `game-designer` | `mvp` | Pode escrever specs, regras, tuning e criterios de jogabilidade quando a task atribuir target_files. |
| `narrative-designer` | `mvp` | Pode escrever estrutura narrativa, personagens, cenas, dialogos, escolhas e integracao com gameplay quando a task atribuir target_files. |
| `ux-ui-designer` | `mvp` | Avaliar fluxos, HUD, menus, legibilidade e interacao em historias de jogo. |
| `gameplay-engineer` | `mvp` | Pode escrever mecanicas, codigo/config de gameplay e dados aprovados quando a task atribuir target_files, skills e gates. |
| `narrative-qa` | `mvp` | Revisar coerencia narrativa, flags, rotas, regressao de dialogo e riscos de conteudo. |
| `level-designer` | `mvp` | Propor mapas, ritmo espacial, encounters e navegacao quando a story tocar superficie de level. |
| `balance-economy-designer` | `mvp` | Avaliar progressao, recompensas, custos, economia e curva de dificuldade. |
| `scene-presentation-designer` | `mvp` | Propor apresentacao de cenas, beats, transicoes, timing e leitura visual. |
| `audio-designer` | `mvp` | Propor intencao de audio, musica, SFX e cues sem validar audio perceptivel automaticamente. |
| `quest-content-designer` | `mvp` | Estruturar quests, objetivos, prerequisitos, recompensas e estados de conteudo. |
| `technical-artist` | `mvp` | Avaliar viabilidade de assets, apresentacao tecnica, constraints visuais e pipeline. |
| `prompt-engineer` | `reference-only` | Apoiar consolidacao de instrucoes reutilizaveis em comandos depois que contratos existirem. |
| `context-engineer-optimization` | `reference-only` | Inspirar melhoria continua e promocao de contexto sem copiar estruturas externas literalmente. |

## Codex Agents

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `codex/agents/*.toml` | `mvp` | Fonte versionada derivada de `agents/*.md` para custom agents Codex em `.codex/agents/`. |

## Scripts

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `scripts/install-loki-symlinks.py` | `mvp` | Instalar command bundles/skills, agents, templates e TOMLs Codex por symlink, filtrando por `--profile`, com dry-run, apply explícito, cleanup legado seguro e manifest de instalacao. |
| `scripts/validate-install-scopes.py` | `mvp` | Validar `install-scopes.json`, neutralidade de artefatos `both`, dependencias de comandos, TOMLs Codex e tags de tipo de projeto dos agentes no `manifest.yaml`. |
| `scripts/validate-install-loki-upgrade.py` | `mvp` | Validar baselines limpos dos perfis do instalador e fixtures temporarias de schema v2 e limpeza legada, sem tocar destinos consumidores. |
| `scripts/validate-agentic-run-state.py` | `mvp` | Validar estado XML do fluxo v2, incluindo parse, IDs, `selection_reason`, gates `must_ask_now`, contratos de escrita, conflitos de `target_files` e completion reports. |

## Install Scope Source

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `install-scopes.json` | `mvp` | Fonte machine-readable dos escopos `internal-only`, `both` e `consumer-only` para bundles/skills, agentes Markdown, docs compartilhados e projecoes Codex instalaveis. |

## Templates

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `tasks-template.md` | `mvp` | Registrar fases, objetivos, validacao observavel, dependencias, human loops, validators e estado de retomada. |
| `task-template.md` | `mvp` | Detalhar objetivo, contexto, requisitos, referencias, passos, Scoped Write Plan, validators, human loop, Definition of Done e resume notes de cada task. |
| `technical-analysis-template.md` | `mvp` | Padronizar analise tecnica com fontes, fatos, inferencias, hipoteses, research gate, matriz de decisao, validators e handoff. |
| `interaction/faseN/*.md` | `mvp` | Registrar perguntas, recomendacoes, decisoes e pendencias humanas. |
| `retrospetivas/faseN/*.md` | `mvp` | Registrar aprendizados tecnicos pos-fase. |
| `builds/faseN/*` | `mvp` | Guardar evidencias e scripts auditaveis quando houver escrita automatizada. |
| `command-contract-template.md` | `mvp` | Padronizar frontmatter, entradas, saidas, skills, gates e handoffs de comandos. |
| `component-contract-template.md` | `mvp` | Padronizar descricao operacional de agents, commands e skills. |
| `project-doc-index-template.xml` | `mvp` | Base para criar `docs/index.xml` no projeto consumidor e catalogar documentacao duradoura. |
| `agentic-run-manifest-template.xml` | `mvp` | Modelo de estado principal da rodada v2, com demanda, agentes selecionados, handoffs, gates, invalidacao, validators e proxima acao. |
| `agentic-analysis-manifest-template.xml` | `mvp` | Modelo de estado da analise agentica, agentes selecionados ou pulados, POVs, reviews, sintese e gates. |
| `agentic-agent-pov-template.xml` | `mvp` | Modelo de POV por agente selecionado, com evidencias, riscos, gates e handoff para sintese. |
| `agentic-agent-review-template.xml` | `mvp` | Modelo de cross-review agentico para acordos, conflitos materiais, resolucao recomendada e notas de validator. |
| `agentic-synthesis-template.xml` | `mvp` | Modelo de sintese do orquestrador com fatos, gates resolvidos, blockers e handoff para plano. |
| `agent-run-report-template.xml` | `mvp` | Modelo de completion report por handoff, com `agent_run_id`, `handoff_id`, owner, target files, validators, gates, evidencia e status. |
| `agent-session-evidence-template.xml` | `mvp` | Modelo de evidencia de sessao com identidade tipada, completude, snapshots sanitizados, locators de runtime e proveniencia de uso. |
| `agentic-run-digest-template.xml` | `mvp` | Modelo de digest final da rodada v2 para consolidar resultados, validators, gates pendentes, backlog e proxima acao. |
| `agentic-backlog-template.md` | `mvp` | Modelo Markdown para pendencias, blockers e follow-ups nao bloqueantes do fluxo agentic. |
| `templates-xml-zord` | `reference-only` | Referencia estrutural, sem formato obrigatorio no MVP Loki. |

## Docs

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `docs/source-boundaries.md` | `mvp` | Declarar fonte canonica, limites e politica de conflito do pacote. |
| `docs/operational-inventory.md` | `mvp` | Listar componentes operacionais a gerar. |
| `docs/usage-guide.md` | `mvp` | Explicar uso do framework em ate 2000 tokens. |
| `docs/loki-installation-workflow.md` | `mvp` | Explicar o workflow canonico de instalacao do Loki em projetos consumidores, do dry-run ao rollback por manifest. |
| `docs/loki-git-workflow.md` | `mvp` | Registrar comandos Git flow do Loki e dependencias minimas de Git, GitHub MCP e `gh`. |
| `docs/loki-installation-workflow.excalidraw.md` | `mvp` | Ilustrar o workflow canonico de instalacao do Loki em projetos consumidores. |
| `docs/loki-plan-execution-workflow.md` | `mvp` | Explicar o workflow canonico de execucao de plano, da descricao curta ate codigo, validacao e handoff para aprendizado. |
| `docs/loki-plan-execution-workflow.excalidraw.md` | `mvp` | Ilustrar a participacao de commands, skills e agents no workflow de execucao. |
| `docs/loki-learning-workflow.md` | `mvp` | Explicar o workflow canonico de aprendizado, retrospectiva e promocao de contexto duradouro. |
| `docs/loki-learning-workflow.excalidraw.md` | `mvp` | Ilustrar a participacao de commands, skills e agents no workflow de aprendizado. |
| `docs/model-effort-guidance.md` | `mvp` | Definir classes provider-neutral de modelo, effort, sinais de escalamento e projecao por adaptador para artefatos Loki. |
| `docs/package-authoring-guardrails.md` | `mvp` | Registrar preflight, regras estruturais, classificacao de referencias e validacoes para evoluir o pacote. |
| `docs/project-context-catalog.md` | `mvp` | Definir como o Loki usa `/docs` e `docs/index.xml` do projeto consumidor sem contaminar o pacote. |
| `docs/loki-init-inventory-contracts.md` | `mvp` | Definir packet schema v1, lotes, cobertura, continuacao, materializacao serial por `catalogador` e retomada do init. |
| `docs/self-containment-audit.md` | `mvp` | Registrar a auditoria e checklist de autocontencao do pacote. |
| `README.md` | `mvp` | Explicar instalacao local em Claude Code e Codex. |
| `manifest.yaml` | `mvp` | Declarar pacote, versao, componentes, destinos locais e tags de tipo de projeto consumidas por `loki-init` para selecao de agentes. |
| Fontes historicas externalizadas | `reference-only` | Usadas como origem antes da publicacao do pacote; nao sao dependencias operacionais. |

## Extensoes Opcionais: RPG Maker MZ

Os itens abaixo sao exemplos de especializacao por tecnologia. Eles nao fazem
parte do fluxo obrigatorio do core Loki e devem ser carregados somente quando o
projeto consumidor declarar RPG Maker MZ.

### Commands

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `loki-implementar-enemy` | `optional-extension` | Implementar inimigos em database RPG Maker MZ depois de validar gates da tecnologia. |
| `loki-action-sequence-generator` | `optional-extension` | Gerar Action Sequences VisuStella por contrato especializado. |
| `loki-visustella-add-postmortem` | `optional-extension` | Promover aprendizados VisuStella com gate de aprovacao. |

### Skills

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `rpg-maker-mz-data-json` | `optional-extension` | Skill especializada para superficies de dados, Database, Common Events ou mapas RPG Maker MZ. |
| `rpg-maker-mz-plugin-workflow` | `optional-extension` | Skill especializada para criar, editar, validar ou ativar plugins RPG Maker MZ. |
| `rpg-maker-mz-project-inventory` | `optional-extension` | Skill especializada para agentes game-dev inventariarem projeto RPG Maker MZ antes de handoff, analise tecnica ou planejamento de runtime/dados/plugins. |
| `rpg-maker-mz-visustella-plugin-index` | `optional-extension` | Skill roteadora para escolher referencias e skills VisuStella por plugin, tier, dependencia, familia, load order e superficie sem autorizar escrita em dados/plugins/runtime. |
| `rpg-maker-mz-visustella-plugin-parameters` | `optional-extension` | Skill para semantica de parametros VisuStella no Plugin Manager e valores em `js/plugins.js`, preservando o gate `rpg-maker-mz-plugin-workflow`. |
| `rpg-maker-mz-visustella-notetags` | `optional-extension` | Skill para sintaxe, alvo correto e validacao de notetags/comment tags VisuStella, preservando o gate `rpg-maker-mz-data-json`. |
| `rpg-maker-mz-visustella-plugin-commands` | `optional-extension` | Skill para comandos VisuStella em map events, troop events, Common Events e payloads PluginManager, preservando gates de dados e plugins. |
| `rpg-maker-mz-visustella-action-sequences` | `optional-extension` | Skill para Battle Core Action Sequences, `<Custom Action Sequence>`, Common Events, `MECH: Action Effect`, padroes e indice XML com Playtest gate. |
| `rpg-maker-mz-visustella-battle-mechanics` | `optional-extension` | Skill de dominio para Battle Core, ATB, TP, Battle AI, Aggro, passives, estados, dano, targeting, gauges e UI de combate, roteando para MVP surfaces e Playtest gate. |
| `rpg-maker-mz-visustella-progression-economy` | `optional-extension` | Skill de dominio para progressao, AP/SP, Skill Shop, More Currencies, Database Inherit, Items and Equips, equip passives, custos, requisitos, shops e inheritance com gate `rpg-maker-mz-data-json`. |
| `rpg-maker-mz-visustella-events-presentation` | `optional-extension` | Skill de dominio para Message Core, Picture Busts, eventos, movimento, DragonBones, options, save/debug, text codes, localization e apresentacao com `human-validation` para runtime visual/input/save. |
| `rpg-maker-mz-visustella-compat-diagnostics` | `optional-extension` | Skill de diagnostico para order, tiers, dependencias, compatibilidade, performance, conflitos, sintomas runtime, notetags sem efeito, Action Sequence cleanup, visuals e save/options/debug issues. |

## Pendencias Futuras Registradas

| Pendencia | Status | Motivo |
| --- | --- | --- |
| Politica fina de concorrencia multi-agent em runtime | `backlog` | O scoped-writer atual exige ownership exclusivo por `target_file`; concorrencia mais granular por AST, evento ou recurso exigira politica futura. |
| Politica de alocacao em superficies runtime especializadas | `backlog` | Nao necessaria para pacote documental; exigira decisao antes de alterar runtime. |
| Skill ou referencia `rpg-maker-mz-quest-state-modeling` | `backlog` | Definir guideline especializada para modelar progresso linear de quests RPG Maker MZ com variavel numerica de etapa e switches apenas para flags ortogonais, antes de promover essa preferencia como regra universal. |
| Renomeacao de namespaces antigos | `backlog` | Nao renomear comandos historicos automaticamente. |

## Conclusao

O inventario operacional separa command bundles/skills, agents, templates e docs. O pacote deve permanecer autocontido para instalacao em outros projetos.
