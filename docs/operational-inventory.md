---
title: Inventario Operacional do Loki Framework Local
status: completed
created: 2026-06-24
type: operational-inventory
self_contained: true
doc_id: loki-operational-inventory
version: 1.0.0
last_updated: 2026-07-27
scope: Current package commands, skills, agents, templates, docs, validators, and reference-only backlog
not_scope: Consumer project inventory, installed destination state, or compatibility with superseded package contracts
authority: Approved Loki package policy and the versioned package source
canonical_source: docs/operational-inventory.md
intended_llm_task: retrieval
source_priority:
  - approved package policy
  - manifest and install-scopes machine-readable inventory when synchronized
  - this operational inventory
  - reference-only and backlog rows
known_conflicts: []
replaced_by: null
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
[Workflow Unificado de Implementacao do Loki](loki-plan-execution-workflow.md). O
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
| `loki-demand-text-improver` | `mvp` | Enriquecer uma demanda inicial em um unico Markdown antes de analise ou planejamento, sem gate de estado de sessao, com destination existente e gravavel, naming deterministico e nenhum workflow posterior automatico. |
| `loki-generate-inferences` | `mvp` | Gerar, de forma opt-in, um unico Markdown canonico de pre-investigacao em diretorio existente e aprovado sob `planos/` do consumidor, com request controls derivados da policy, slug/digest e versao deterministica resolvida antes da approval, create exclusivo e bloqueio sem retry em colisao concorrente; nao investiga, nao faz fan-out, handoff, agent run, web research, CI, workflow downstream ou mutacao de catalogo. |
| `loki-tech-analysis` | `mvp` | Produzir analise tecnica agnostica e baseada em evidencias antes de plano ou execucao. |
| `loki-deep-analysis` | `mvp` | Produzir, de forma opt-in, analise profunda assistida por catalogo com descoberta seletiva de tecnologias, inferencias contextuais e investigacoes independentes; gera report, eventos e candidatos rastreaveis sem aninhar `loki-tech-analysis`, alterar o catalogo ou declarar validacao de runtime. |
| `loki-human-decision-preflight` | `mvp` | Classificar decisoes humanas pendentes antes do plano como perguntar agora, delegar ao plano, validar depois ou responder por fonte local. |
| `loki-agentic-development` | `mvp` | Executar o caminho avancado com analise multiagente, gates, um unico handoff ao `loki-implement-feature`, completion/evidence, knowledge state, digest e backlog. |
| `loki-implement-feature` | `mvp` | Planejar e implementar uma demanda + analise Markdown em uma invocacao retomavel, com command identity v2, execution input v2, audit configuration/checkpoint v1, LokiRunState/result/dashboard v3, consistency v2, task_validation e métricas v1, DAG, retry e terminal truth. |
| `loki-enrich-tasks` | `mvp` | Revisar tasks usando aprendizados anteriores, interactions e research gate condicionado sem expor fontes internas nem promover regra duradoura diretamente. |
| `loki-retrospectiva-tecnica` | `mvp` | Registrar retrospectiva tecnica reutilizavel ao fim de uma fase ou apos uma dificuldade real ser resolvida de fato. |
| `loki-continuous-improvement` | `mvp` | Promover aprendizados validados para superficies duradouras; no destino package, exige profile, precheck mecânico ready e parecer v2 independente do Auditor sem alterar destinos nao-package. |
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

### Contrato resumido de `loki-generate-inferences`

O command deriva piso minimo 8, teto inexistente e pagina de recuperacao 20.
Piso nao e stop, pagina nao e limite total e o limite persistente 3 e somente
armazenamento/manutencao. Gera todo candidato material distinto ate saturacao
semantica; interrupcao de contexto retorna parcial retomavel. Saturacao abaixo
do piso nao autoriza padding. Custo e impacto nao influenciam disposicao.

O `loki-deep-analysis` executa no maximo 3 rodadas de ate 6 investigacoes
delegadas, com concorrencia 2, barreira terminal e reclassificacao total entre
rodadas. Reinvestigacao posterior exige nova pergunta, justificativa e IDs.
Resolucao local nao consome capacidade e custo e apenas telemetria. Nao existe
quarta rodada nem auto-invocacao downstream.

Depois de resolver digest, basename e versao por um snapshot do diretorio, a
approval vincula diretorio canonico, target exato, basename/versao,
before-state/snapshot e um create exclusivo. Colisao posterior invalida a
approval, bloqueia sem retry e exige nova resolucao e nova approval.

O pacote possui 19 command bundles `loki-*` ativos, todos com escopo de
instalacao `both`. O router geral `lf-command-workflows` expoe 17 workflows de
uso geral; os dois workflows de manutencao do pacote,
`loki-knowledge-extraction-analysis` e `loki-self-healing`, sao roteados por
`lf-internal-command-workflows`. Instalar esses workflows em um consumidor nao
autoriza mutar artefatos consolidados do pacote ou superficies do consumidor:
mutacao do pacote continua exigindo package root e envelope
`destination_scope: package`; relatorios transitorios preservam os limites do
contrato de analise.

A matriz caller/mode do `catalogador` e fechada: `loki-init` usa
`init-bootstrap-cataloger`, `init-publication-batch` e
`init-final-reconciliation`; `loki-continuous-improvement` e
`loki-implement-feature` usam `task_scoped_writer`; `loki-catalogar-docs` usa `task_scoped_writer` ou
`proposal-only`. Combinacoes ausentes ou cruzadas bloqueiam antes da escrita.

### Estado operacional de inferencias do consumidor

O inventario do pacote inclui a capacidade `lf-analytic-inference`, mas nao o
estado que ela opera. O unico layout de producao ativo e XML v2 em
`<consumer-root>/.loki/analytic-inference/v2/`, com `registry.xml`, indices
`index.xml` por tecnologia, records `rev-N.xml` e events `.xml` pertencentes ao consumidor. Registry
ausente significa estado `absent`; registry valido sem entries significa
`empty`. Ambos os casos de leitura retornam `insufficient` sem criar arquivos.

O catalogo ativo e exclusivamente XML v2. JSON nao e fallback do estado ativo,
nao recebe mutacao e nao e uma fonte de catalogo suportada.
O layout `.loki/analytic-inference/v1/` e rejeitado antes de qualquer leitura ou
write. JSON de policy, request, approval e output de CLI permanece parte do
control plane, nao do catalogo persistido.

Esse state root e classe `consumer-operational-state`, nao documentacao do
consumidor e nao artefato do pacote. O consumer root e resolvido internamente
do `pwd` canonico, e o command deve iniciar na raiz do projeto consumidor.
`technical-implementer` e o writer
exclusivo sob envelope `task_scoped_writer`, consumer root canonico, targets
exatos e validators. Promocao e reorganizacao exigem approval root-bound
vinculada a `operation_id`, operacao, `consumer_root` canonico, policy ID/digest,
`target_manifest_digest_sha256`, targets exatos, `source_locator` e freshness;
a identidade, containment, targets e hashes sao
revalidados imediatamente antes do write. Purge exige ainda dry-run completo e
approval JIT independente, single-use e ligada a root, paths, hashes e digests
exatos.
`framework-artifact-writer` escreve somente contratos, schemas, scripts,
policy e docs do pacote; `catalogador` continua exclusivo para docs duradouros
do consumidor. Nenhum deles pode escrever `.loki`.

## Support Skills

Esta seção lista skills `lf-*` e de domínio/tecnologia. Elas fornecem
conhecimento reutilizável; não são mini-orquestradores nem duplicam os command
bundles.

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `lf-command-workflows` | `mvp` | Skill agregadora para rotear os 17 commands Loki de uso geral disponiveis no perfil instalado. |
| `lf-internal-command-workflows` | `mvp` | Skill `both` especializada em rotear extracao de conhecimento e self-healing; a disponibilidade no consumidor nao amplia os limites package-only desses workflows. |
| `lf-agentic-orchestration` | `mvp` | Skill auxiliar para preflight de agentes, fan-out selecionado, estado XML, gates, cross-review, reports, liveness, invalidacao, digest, backlog e retrospectivas por agente. |
| `lf-implement-feature-execution` | `mvp` | Autoridade current-only para command identity v2, execution input v2, audit configuration/checkpoint v1, LokiRunState/result/dashboard v3, consistency v2, métricas v1, target decisions, DAG, preflights, AC/validators, liveness, retry, resume e terminal truth. |
| `lf-execution-knowledge-capture` | `mvp` | Separar evidence de knowledge, avaliar materialidade, despachar entry exclusiva sem bloquear e reconciliar estados degradados em checkpoint. |
| `lf-domain-context-preflight` | `mvp` | Preflight pessoal reutilizavel para docs minimas, fontes atuais, freshness, conflitos e lacunas, sem autocorrecao de docs. |
| `lf-external-knowledge-extraction` | `mvp` | Extrair observacoes, padroes, exemplos, riscos e aprendizados candidatos de artefatos externos sem decidir mudancas no Loki. |
| `lf-framework-impact-audit` | `mvp` | Auditar o impacto de aprendizados externos em artefatos e workflows do Loki usando `docs/operational-inventory.md`. |
| `lf-git-workflow` | `mvp` | Procedimento compartilhado para branch, commit e PR com preflight Git, staging seguro, gates humanos e GitHub MCP/`gh` fallback. |
| `lf-web-deep-research` | `mvp` | Procedimento reutilizavel de pesquisa profunda na internet com ondas de busca, avaliacao de fontes, contradicoes, assumptions, lacunas e output estruturado. |
| `lf-agent-execution-evidence` | `mvp` | Definir, coletar e revisar evidencia provider-neutral de execucao, com identidade tipada, snapshot sanitizado, lacunas explicitas e proveniencia de uso sem registrar raciocinio privado. |
| `lf-template-library` | `mvp` | Expor templates do pacote como referencias instalaveis por skill. |
| `excalidraw-diagram-generator` | `mvp` | Gerar diagramas Excalidraw para enriquecer documentacao rica de workflows, processos, arquitetura e relacoes. |
| `lf-index-navigator` | `mvp` | Navegar a documentacao do consumidor por `docs/index.xml`; se o catalogo estiver ausente, retornar `consumer_docs_index_missing` e encaminhar ao `catalogador`, sem ler `index.md`. |
| `lf-tech-analysis-authoring` | `mvp` | Criar e revisar analises tecnicas Loki baseadas em evidencias, com mapa de fontes, pesquisa condicionada, matriz de decisao, validators e handoff para plano. |
| `lf-analytic-inference` | `mvp` | Compartilhar entre Codex e Claude Code contratos, schemas, scripts, fixtures e policy para consulta seletiva e manutencao deterministica. O pacote nao contem catalogo, seed nem overlay; o estado vivo XML pertence ao consumer root canonico em `.loki/analytic-inference/v2/`. |
| `lf-analytic-inference-preparation` | `mvp` | Preparar deterministica e read-onlymente um core de inferencias antes de investigacao, compondo `lf-analytic-inference` sem dispatch, handoff, web research, CI, workflow downstream, mutacao de catalogo ou replay byte a byte. |
| `lf-action-plan-authoring` | `mvp` | Criar e revisar planos Loki executaveis por outro agente, com fases, tasks, dependencias, referencias, validators e validacao observavel. |
| `lf-command-creator` | `mvp` | Fonte compartilhada do contrato 24/24 para criar ou revisar command bundles com Input, Execution, Response, owners, gates, validators e retomada. |
| `lf-agent-creator` | `mvp` | Fonte compartilhada do contrato de agents por capacidades e modos, com envelope de escrita, validação e handoff claro. |
| `lf-skill-creator` | `mvp` | Fonte compartilhada do contrato 24/24 para criar ou revisar skills com capacidade única, metadata válida, progressive disclosure e forward testing. |
| `lf-documentation-writing` | `mvp` | Classificar modo documental e aplicabilidade LLM-facing de forma independente; rotear artefatos aplicaveis aos requisitos de autoria e ao contrato canonico de perfil, fixtures e auditoria independente. |
| `task-onboarding` | `reference-only` | Inspiracao historica ja internalizada no contrato current-only de execucao unificada. |
| `brainstorm-character` | `backlog` | Apoio futuro para design de personagens e bosses. |

## Agents

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `standards-curator` | `mvp` | Avaliar promocao de aprendizados validados para pacote Loki, documentacao duradoura do consumidor ou backlog. |
| `retrospective-digester` | `mvp` | Digerir retrospectivas tecnicas em modo read-only, com fan-out por arquivo, retornando aprendizados, atritos, candidatos e evidencias para `loki-continuous-improvement`. |
| `runtime-qa` | `mvp` | Avaliar feedback, checklist de validacao humana e evidencias perceptiveis; pode escrever reports/evidencias quando uma task atribuir target_files. |
| `framework-artifact-writer` | `draft-scoped-writer` | Agente `both` para escrita interna do pacote: emite profile, executa checks e precheck mecanico de materialidade/perfil, e entrega apenas packets ready ao Auditor; a instalacao no consumidor nao autoriza escrita em consumer/runtime. |
| `framework-artifact-quality-auditor` | `draft-write-test` | Agente `both`, read-only e independente, para auditar patches do pacote: valida profile, rubric v2, fixtures, revisao isolada e bias controls; bloqueia findings/incertezas e nunca corrige producao. |
| `execution-context-reader` | `mvp` | Extrair contexto read-only da demanda, `analysis_file`, state, task, docs e fontes locais para `loki-implement-feature` sem escrever. |
| `source-researcher` | `mvp` | Mapear fatos, lacunas e conflitos em pesquisa multi-fonte antes de analise, plano, feedback, enriquecimento ou promocao. |
| `session-evidence-auditor` | `mvp` | Auditar em modo read-only manifests de evidencia de sessao ja validados, sem inventar identidade, transcritos, uso de tokens ou raciocinio privado. |
| `execution-knowledge-cataloger` | `mvp` | Escrever somente uma entry XML exclusiva a partir de completion/evidence sanitizados persistidos; nunca shared state ou promoção. |
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
| `scripts/install-loki-symlinks.py` | `mvp` | Instalar command bundles/skills, agents, templates e TOMLs Codex por symlink, filtrando por `--profile`, com dry-run, apply explícito, manifest de instalacao e rejeicao sem writes de layouts fora do schema 2. |
| `scripts/validate-install-scopes.py` | `mvp` | Validar `install-scopes.json` schema 2, neutralidade de artefatos `both`, dependencias de comandos, TOMLs Codex, tags de tipo de projeto, ausencia de seed/catalogo XML vivo empacotado, ausencia da projecao retirada e paridade exata entre `scripts/*.py`, `manifest.yaml#scripts` e esta tabela. |
| `scripts/validate-install-loki-upgrade.py` | `mvp` | Validar baselines limpos dos perfis do instalador e a matriz temporaria de rejeicao de layouts fora do schema 2, sem tocar destinos consumidores. |
| `scripts/validate-agentic-run-state.py` | `mvp` | Validar o contrato agentic XML atual (manifest 4, report 6, digest 4 e WTR 1), métricas/liveness e rejeição current-only de schemas removidos. |
| `scripts/validate-implement-feature-contracts.py` | `mvp` | Validar somente command identity v2, execution input v2, audit configuration/checkpoint v1, LokiRunState/result/dashboard v3, consistency v2, task_validation e execution metrics v1, incluindo fronteiras due, replay completo, liveness e custo sem budgets/autostop. |
| `scripts/validate-llm-artifact-precheck.py` | `mvp` | Bloquear antes do Auditor packets package fora do approval, materialidade observada ou profiles/partições/projeções incompletos; nunca aprovar qualidade. |
| `scripts/validate-execution-knowledge.py` | `mvp` | Validar entry schema v1, lineage, materialidade, estados, targets exclusivos, sanitização e ausência de promoção. |
| `scripts/validate-loki-init-catalogador-contracts.py` | `mvp` | Validar packets e lotes schema v1 do `loki-init`, caller/mode do `catalogador`, ownership serial, fixtures e projeções atuais de agentes. |

## Install Scope Source

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `install-scopes.json` | `mvp` | Fonte machine-readable dos escopos `internal-only`, `both` e `consumer-only` para bundles/skills, agentes Markdown, docs compartilhados e projecoes Codex instalaveis. |

## Templates

| Componente | Status | Responsabilidade |
| --- | --- | --- |
| `tasks-template.md` | `mvp` | Registrar fases, command identity v2, execution input v2, audit configuration v1, dependencias, human loops, validators, checkpoint refs e LokiRunState v3 retomavel, preservando task_validation e métricas v1. |
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
| `agent-run-report-template.xml` | `mvp` | Modelo report schema 6 por handoff, com IDs, owner, validators, métricas/tokens, liveness probe, gates, evidência e status. |
| `agent-session-evidence-template.xml` | `mvp` | Modelo de evidencia de sessao com identidade tipada, completude, snapshots sanitizados, locators de runtime e proveniencia de uso. |
| `execution-knowledge-entry-template.xml` | `mvp` | Modelo de knowledge run-local com claims tipadas, attempts, cause/resolution, gaps, reuse guidance, segurança e ownership de promoção. |
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
| `docs/loki-plan-execution-workflow.md` | `mvp` | Explicar o workflow unificado de implementacao, da demanda e analise em Markdown ate codigo, validacao e handoff para aprendizado. |
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
