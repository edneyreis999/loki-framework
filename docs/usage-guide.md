---
title: Guia de Uso do Loki Framework Local
type: usage-guide
status: draft
created: 2026-06-24
scope: local-project-package
doc_id: loki-usage-guide
version: 1.0.0
last_updated: 2026-07-24
not_scope: Consumer project policy, installation approval, runtime validation, or compatibility with superseded commands
authority: Approved Loki package policy and current package command contracts
canonical_source: docs/usage-guide.md
intended_llm_task: routing
source_priority:
  - approved human decisions and package policy
  - current command and helper contracts
  - this usage guide and linked package docs
  - examples and consumer-provided content
known_conflicts: []
replaced_by: null
---

# Guia de Uso do Loki Framework Local

O Loki Framework local organiza trabalho em projetos de software e jogos usando
command bundles, skills e agents. Ele e um pacote documental e operacional
autocontido: descreve como conduzir analise, plano, execucao, validacao e
melhoria continua sem depender de blueprint, planos historicos ou arquivos de
outro projeto.

## Estrutura

- `skills/loki-*/`: commands invocaveis serializados como bundles com Input,
  Execution, Response e template.
- `skills/lf-*` e skills de dominio: conhecimento tecnico ou processual
  reutilizavel carregado quando o dominio aparecer.
- `agents/`: papeis especialistas que retornam analise, checklist, proposta ou
  escrita escopada quando um workflow aprovado atribuir `target_files`.
- `codex/agents/`: TOMLs versionados derivados de `agents/*.md` para custom
  agents Codex.
- `scripts/install-loki-symlinks.py`: instalador Codex por symlink para
  projetos consumidores ou para o package source, filtrado por perfil.
- `install-scopes.json`: fonte machine-readable dos escopos `internal-only`,
  `both` e `consumer-only`.
- `templates/`: contratos minimos para criar novos command bundles e componentes.
- `docs/`: limites, inventario e guia de uso.
- `docs/project-context-catalog.md`: contrato entre o pacote Loki e a
  documentacao duradoura do projeto consumidor.
- `manifest.yaml`: lista componentes, origem, destino sugerido e guardrails.

## Fluxos Canonicos

Use estes documentos como fonte principal do ciclo operacional:

- [Workflow de Instalacao do Loki em Projetos Consumidores](loki-installation-workflow.md):
  descreve dry-run, approval, aplicacao por symlink, perfis, validacao e
  rollback antes de usar Loki em um projeto alvo.
- [Workflow Unificado de Implementacao do Loki](loki-plan-execution-workflow.md):
  descreve o caminho publico de demanda + analise Markdown para plano, DAG,
  escrita serializada, AC/validators, dashboard, teste manual e evidencia, alem
  do caminho agentic avancado com um unico handoff ao executor unificado.
- [Workflow de Aprendizado do Loki](loki-learning-workflow.md): descreve como
  resultados, bugs, feedbacks e retrospectivas viram ajuste local, candidato,
  regra duradoura ou backlog.
- [Model and Effort Guidance for Loki Artifacts](model-effort-guidance.md):
  define como classificar `model_class`, `effort`, escalamento e projecao por
  adaptador para comandos, skills, agentes, templates e docs gerados.

Quando a melhoria atingir o proprio pacote, aplique
`docs/package-authoring-guardrails.md` depois de identificar o destino pelo
workflow de aprendizado.

## Antes da Analise: Enriquecer a Demanda

Use `loki-demand-text-improver` para transformar uma demanda inicial em um
Markdown standalone que explicita objetivo, contexto, escopo, requisitos,
restricoes, criterios de aceite, validators, premissas, riscos e referencias.
Esse passo preserva a intencao original e acontece antes de analise tecnica ou
planejamento.

O command nao exige Plan Mode nem outro estado de sessao. Ele continua
fail-closed para inputs ausentes ou invalidos, destination inseguro ou nao
gravavel, target ocupado, conflito material, gate humano pendente ou validator
falho. O `destination` precisa ser um diretorio existente, gravavel e autorizado.

Exemplo com entrada em arquivo:

```text
loki-demand-text-improver
analysis_input: docs/Demanda.md
source_paths: [docs/contexto-produto.md]
destination: planos/027-demanda/
```

A saida sera `planos/027-demanda/Demanda-improved.md`. Com `analysis_input`
inline, o target sera `planos/027-demanda/improved-demand.md`. Se o target ja
existir, o command bloqueia sem sobrescrever, autonumerar ou escolher outro
nome.

O resultado terminal e somente a demanda enriquecida. O command nao produz
analise tecnica como `loki-tech-analysis` e nao percorre o caminho integrado de
analise, gates, plano e execucao de `loki-agentic-development`. Tambem nao
invoca decision preflight, action planning ou implementacao. Depois da saida, o
usuario faz uma nova escolha explicita sobre o proximo workflow.

## Analise Padrao e Analise Profunda

Use `loki-tech-analysis` como rota padrao de analise pre-plano baseada em
evidencias. Ela organiza fontes, fatos, inferencias, hipoteses, alternativas,
risco, validators e gates consumidos pelo planejamento interno do
`loki-implement-feature`.

Use `loki-deep-analysis` de forma opt-in quando a demanda se beneficiar de
descoberta de tecnologias, consulta seletiva a inferencias catalogadas,
geracao contextual de candidatos ou investigacoes independentes. Essa e uma
rota especializada para a mesma etapa: ela nao chama nem aninha
`loki-tech-analysis`. Seu report, seus eventos imutaveis e seus candidatos
`unreviewed` sao evidencia rastreavel; nao alteram o catalogo e nao comprovam
validacao de runtime.

`loki-generate-inferences` e um fork opcional anterior a investigacao. Ele
recebe `analysis_input`, `source_paths` locais permitidos e um `destination`
aprovado; o destino deve ser um diretorio existente abaixo de
`<consumer-root>/planos/`, sem symlink ou traversal. O command deriva piso
minimo 8, nenhum teto e pagina de recuperacao 20. O piso nao encerra geracao e
a pagina nao limita recuperacao total. Preserva todo candidato material
distinto ate saturacao semantica; interrupcao de contexto retorna parcial com
cursor e superficies nao exploradas, enquanto saturacao abaixo do piso termina
sem padding. O limite persistente 3 e somente armazenamento/manutencao. Custo
e impacto nao influenciam disposicao. Depois resolve o digest da demanda e
escolhe antes da approval um target versionado: slug NFKD/ASCII do
stem para arquivo ou `inferences-<digest12>` para inline, seguido pelo menor
`-vN` ausente quando o basename ja existir. A approval fica vinculada ao
diretorio canonico, target exato, basename/versao, before-state/snapshot e um
create exclusivo. Colisao posterior invalida a approval e bloqueia sem retry;
uma nova resolucao e nova approval sao obrigatorias. Seu unico output e
esse Markdown, com um core canonico de preparacao de inferencias, criado uma
unica vez e terminal em
`pre-investigation-complete`. O command nao investiga, nao cria fan-out,
handoff ou agent run, nao pesquisa a web, nao roda CI, nao invoca workflow
downstream e nao altera o catalogo. Depois da resposta, a pessoa escolhe
manualmente uma rota posterior permitida, como `loki-deep-analysis`; o command
nao a agenda nem a invoca.

`loki-deep-analysis` usa no maximo 3 rodadas de ate 6 investigacoes delegadas,
em subondas de concorrencia 2. Ao fim de cada rodada terminal, reclassifica
todas as inferencias e para cedo quando nao resta investigacao util. A mesma
inferencia pode ser reinvestigada apenas em rodada posterior, com nova pergunta,
justificativa material e IDs novos. Resolucao local nao consome os seis slots e
custo e telemetria, nunca gate. A terceira rodada encerra a fase e o handoff
downstream e retornado sem auto-invocacao.

As duas projecoes suportadas, Codex e Claude Code, compartilham
`lf-analytic-inference` com escopo de instalacao `both`. O pacote distribui
somente capacidade imutavel: contratos, schemas, scripts, fixtures e a policy
default. Ele nao contem catalogo de producao, seed nem overlay.

O estado vivo pertence exclusivamente ao projeto consumidor, sob o root
canonico `<consumer-root>/.loki/analytic-inference/v2/`. O layout ativo usa
`registry.xml`, indices `index.xml`, records `rev-N.xml` e events `.xml`. Operacoes
catalog-backed resolvem internamente o consumer root a partir do `pwd` canônico
no inicio do command, que deve ser executado na raiz do projeto consumidor.
Nao existe parametro publico de root nem fallback por adapter, Git, ambiente,
source paths, docs ou descoberta de `.loki`. Registry ausente ou valido sem entries
retorna `insufficient`, `mutation_applied: false` e zero writes. A primeira
mutacao aprovada pode fazer bootstrap nesse layout; instalacao e lookup
read-only nunca fazem bootstrap.

O catalogo ativo e exclusivamente XML v2. JSON nao e fallback para lookup,
nao recebe mutacao e nao e uma fonte de catalogo suportada; instalacao e
dry-run nao criam nem alteram estado de catalogo.
Uma arvore `.loki/analytic-inference/v1/` e rejeitada antes de leitura ou
escrita; nao existe conversao automatica desse layout. JSON continua suportado
no control plane (por exemplo, policy, requests, approvals e saida de CLI), que
nao e estado de catalogo.

Estado nesse layout usa `destination_scope: consumer-operational-state` e tem
`technical-implementer` como writer exclusivo sob `task_scoped_writer`, com
root canonico, targets exatos e writes serializados. Promocao e reorganizacao
exigem approval root-bound vinculada a `operation_id`, operacao,
`consumer_root` canonico, policy ID/digest,
`target_manifest_digest_sha256`, targets exatos, `source_locator` e freshness;
root, containment, targets e hashes sao revalidados imediatamente antes da
mutacao.
Purge exige dry-run completo e uma approval JIT separada, posterior, single-use
e ligada a root, IDs, paths, hashes e digests exatos.
`framework-artifact-writer` escreve somente contratos, schemas, scripts, policy
e docs do pacote; `catalogador` escreve somente docs duradouros do consumidor.
Nenhum dos dois escreve `.loki`.

## Implementacao Unificada e Caminho Agentic

Use `loki-implement-feature` quando ja houver uma demanda nao vazia e uma
analise Markdown decision-complete. O comando recebe esses dois inputs,
materializa ou retoma o plano, registra targets e owners antes da escrita,
executa o DAG e termina com dashboard e passos de teste manual. Nao existe uma
segunda chamada publica para executar o plano.

Um terceiro argumento publico opcional, `audit_frequency`, controla a
granularidade da auditoria independente. Se omitido, normaliza para
`phase/default`. Se fornecido, aceita somente `task`, `phase` ou `plan` exatos e
usa origem `explicit`, inclusive quando o valor e `phase`. Null, vazio, aliases,
traducao e variacao de caixa sao invalidos. Input somente persiste essa escolha
em command identity v2/execution input v2: nao verifica disponibilidade do
Auditor e nao despacha auditoria.

Execution consulta o scheduler canonico nos pontos persistidos do DAG. Auditor
independente e resolvido apenas para uma fronteira due com escrita material.
Uma fronteira ainda nao due nao despacha; uma fronteira due sem bytes materiais
registra `not-applicable`, despacha ninguem e nao concede approval. Finding
retorna o escopo afetado ao Writer; qualquer correcao invalida checkpoint
sobreposto, repete checks/validators aplicaveis e exige replay completo da
mesma fronteira, nunca revisao incremental. A escolha significa:

- `task`: fronteira quando a task e seus checks exigidos ficam completos;
- `phase`: fronteira quando todos os membros da fase e seus checks ficam
  completos;
- `plan`: uma fronteira depois do DAG/checks terminais e antes da reconciliacao
  terminal.

Cada task possui ao menos um AC observavel e exatamente uma rota primaria:
validator deterministico ou Write Test Agent independente. A conversa de
correcao fica em findings, respostas do Writer e retestes imutaveis. Findings
minor nao consomem budget; medium/major consomem o `retry_limit`. Ao esgotar, a
task fica unresolved, seus dependentes transitivos sao pulados e branches
independentes continuam.

Use `loki-agentic-development` quando tambem forem necessarios POVs, selecao de
agentes, cross-review, sintese, gates, completion reports, digest e backlog.
Esse caminho permanece semanticamente distinto, mas produz ou valida uma
analise Markdown e realiza um unico handoff ao `loki-implement-feature`.

O contrato e current-only: comandos, schemas e estados substituidos nao mantem
alias, wrapper, conversor, fallback ou uma segunda autoridade operacional.

Nos dois caminhos, completion/evidence minimo e persistido primeiro. Quando ha
atrito ou aprendizado material, `execution-knowledge-cataloger` pode criar em
paralelo uma entry exclusiva no run. O fluxo principal nao espera por esse
enriquecimento: atraso ou falha vira `partial`, `failed` ou `unsupported`;
lookup trivial pode ser `skipped-nonmaterial`. Somente
`loki-continuous-improvement` promove conhecimento depois.

O dashboard unificado deriva do estado persistido e inclui AC/evidence,
validators, ciclos, retries, failed tasks, skipped dependents, targets
inferidos, riscos, resume e teste manual. Human validation herdada da analise
aparece somente no final e apenas quando for a unica condicao restante.
Ele tambem mostra a configuracao v1 completa, fronteiras due, checkpoints
ativos, materialidade, independencia, findings/corrections e full replays. Um
status de sucesso exige toda fronteira due `approved` ou `not-applicable`.

O mesmo run publica `builds/metrics/execution-metrics.json` schema v1, ligado
por ref/digest ao LokiRunState v3, resultado v3 e dashboard v3. Ele registra spans,
clocks, elapsed/active/critical-path, contagens e tokens separados em
`exact`, `estimated` ou `unavailable`; estimativas têm range, baixa confiança e
escopo parcial. Telemetria degradada não bloqueia execução funcional. Uma
parada por silêncio exige liveness probe do adaptador, e `running`/`progress`
proíbe a parada. O dashboard exibe custo/recursos apenas com provenance: não há
budgets de token/custo nem parada automática por custo.
O mesmo hash canônico, calculado sem os dois campos de identidade, alimenta
`metrics_id` e `metrics_digest`. Um documento mínimo `unavailable` publicado
mantém ref/digest; somente falha total de publicação usa null/null com status
`unavailable` e motivo explícito `publication failure`.

## Evidencia de Sessao

Use `lf-agent-execution-evidence` quando o orquestrador ou collector precisar
registrar evidencia de uma execucao de agente. O collector recebe entrada
estruturada do adaptador e um destino aprovado; ele preserva um snapshot
sanitizado quando possivel ou registra uma lacuna tipada quando a fonte nao e
observavel. `session-evidence-auditor` revisa manifests ja validados em modo
read-only. Metricas de tokens exigem fonte, escopo e tempo: valores cumulativos
ou de janela de conta nunca representam uso por agente. Nenhum workflow coleta
raciocinio privado.

## Gates Humanos

O framework usa gates para impedir validacao falsa:

- `interview`: quando falta requisito, preferencia ou contexto.
- `approval`: antes de politica duradoura, instalacao, promocao ou escrita sensivel.
- `human-validation`: obrigatorio para comportamento perceptivel, estado
  runtime, integracoes ativas ou superficies declaradas por skill tecnica.

Mudancas do pacote Loki nao usam um gate generico: somente
`loki-continuous-improvement` na ramificacao `destination_scope: package`
coordena envelope, approval aplicavel, `framework-artifact-writer`, checks e
precheck mecânico. Somente `ready-for-auditor` com `dispatch_allowed: true`
segue para `framework-artifact-quality-auditor` independente; o precheck não
aprova nem substitui a auditoria completa.

Parsers estruturais, validadores de linguagem e diff restrito reduzem risco
estrutural, mas nao substituem validacao humana quando a mudanca afeta
comportamento perceptivel ou o runtime do consumidor.

## Modelos e Effort

Use `docs/model-effort-guidance.md` como referencia central para orientar
modelo e effort. Artefatos canonicos devem declarar classes provider-neutral,
como `frontier_reasoning`, `coding`, `generalist`, `long_context` e
`fast_low_cost`, antes de citar IDs concretos de fornecedor.

Documentacao duravel, politicas, contratos, templates e mudancas normativas do
pacote usam effort alto por padrao. Documentacao transiente de execucao pode
usar effort baixo ou medio, exceto pesquisas de `loki-deep-research`, analises
de `loki-tech-analysis` e planos materializados por `loki-implement-feature`,
que continuam high effort. Implementacao de codigo
usa modelo de codificacao e effort medio por padrao, escalando quando houver
risco tecnico, integracao, arquitetura ou validacao dificil.

## Instalacao Codex por Symlink

Para Codex, o caminho principal e manter este pacote como fonte versionada e
criar symlinks no projeto consumidor:

```bash
PACKAGE_ROOT="$(pwd)"
DEST="/tmp/loki-symlink-test"
python3 "$PACKAGE_ROOT/scripts/install-loki-symlinks.py" --dest "$DEST" --dry-run --profile consumer
python3 "$PACKAGE_ROOT/scripts/install-loki-symlinks.py" --dest "$DEST" --yes --profile consumer
```

Perfis aceitos:

- `consumer`: instala artefatos `both` e `consumer-only`.
- `package-source`: instala artefatos `both` e `internal-only`.
- `all`: instala todos os escopos para validacao/desenvolvimento.

O perfil default e `consumer`. `package-source` existe para manter workflows de
manutencao do pacote fora de projetos consumidores. Distribuicao por
plugin/marketplace continua etapa posterior, fora do v2.

O script instala:

- `.agents/skills/<skill-name>` apontando para `skills/<skill-name>`;
- `.agents/agents/<agent>.md` apontando para `agents/<agent>.md`;
- `.agents/templates` apontando para `templates`;
- `.codex/agents/<agent>.toml` apontando para `codex/agents/<agent>.toml`.

Esses links instalam capacidade, nao estado operacional. Dry-run e apply nao
criam, registram nem removem `.loki`.
Se o destino ja tiver `.loki`, trate toda a arvore como estado do consumidor e
preserve-a byte a byte durante o workflow de instalacao.

Instalacao em destino consumidor real exige approval especifico para o caminho
e para o modo de execucao. `--replace` e excepcional e exige approval separado.
O manifest gerado em `.agents/loki-installation-manifest.json` registra origem,
destino, tipo, `install_profile`, `install_scope` e status de cada link.

O instalador bloqueia mistura de perfis. Se o destino ja tiver um manifest Loki
de outro perfil, ou artefatos Loki conhecidos que nao pertencem ao perfil
solicitado, pare e faca rollback manual dos links registrados no manifest
anterior antes de rodar novo dry-run. Nao trate `consumer`, `package-source` e
`all` como camadas incrementais.

O instalador aceita somente o layout schema 2. `.agents/agents` como symlink de
diretorio, `.agents/commands` e manifests que registrem links de command ou
historico de remocao causam rejeicao sem writes. Ajuste o destino manualmente e
repita o dry-run antes de aplicar.

Depois da instalacao, valide a estrutura instalada:

```bash
python3 "$PACKAGE_ROOT/scripts/validate-install-scopes.py"
find -L "$DEST/.agents/skills" -maxdepth 2 -name SKILL.md | sort
find "$DEST/.agents/agents" -maxdepth 1 -type l -name '*.md' | sort
find "$DEST/.codex/agents" -maxdepth 1 -type l -name '*.toml' | sort
python3 - "$DEST" <<'PY'
import json
import pathlib
import sys

manifest = pathlib.Path(sys.argv[1]) / ".agents/loki-installation-manifest.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
print(f"profile={data.get('install_profile')} links={len(data.get('links', []))}")
assert all("install_scope" in link for link in data.get("links", []))
assert all(link.get("type") != "command" for link in data.get("links", []))
PY
git -C "$DEST" status --short .agents .codex
```

Esses checks confirmam entrypoints de skills, agentes Markdown, TOMLs Codex,
manifest parseavel e impacto visivel no git do consumidor. Eles nao substituem
validacao funcional de um workflow Loki dentro do projeto consumidor quando
esse comportamento for necessario.

## Git Flow

O Loki inclui tres comandos de Git flow:

- `loki-criar-branch` para criar branch local com base e nome aprovados.
- `loki-commit` para stage explicito e commit local.
- `loki-abrir-pr` para publicar a branch e abrir PR.

`loki-abrir-pr` prefere GitHub MCP quando disponivel e usa `gh` autenticado
como fallback. Sem GitHub MCP nem `gh`, o comando deve parar apos montar a
proposta de PR. Consulte `docs/loki-git-workflow.md`.

## Command Bundles, Skills Core e Extensoes

Os command bundles instaláveis (`loki-init`, `loki-feedback`,
`loki-tech-analysis`, `loki-deep-analysis`,
`loki-human-decision-preflight`, `loki-implement-feature`,
`loki-agentic-development`,
`loki-enrich-tasks` e `loki-retrospectiva-tecnica`) expõem commands Loki por
meio de `SKILL.md`, references e assets, e continuam sendo commands operacionais.

As skills core (`lf-agentic-orchestration`, `lf-implement-feature-execution`,
`lf-execution-knowledge-capture`,
`lf-command-creator`, `lf-agent-creator`, `lf-skill-creator`,
`lf-index-navigator`, `lf-tech-analysis-authoring`, `lf-analytic-inference`,
`lf-action-plan-authoring` e `lf-template-library`) fornecem conhecimento e
procedimentos reutilizáveis chamados pelos commands.

Juntas, essas superficies governam entrevista, autoria de analises,
planejamento e execucao unificados, AC/validators por task, orquestracao
agentica, templates, enriquecimento de tasks, retrospectiva, navegacao de
documentacao e evolucao controlada de commands, agents e skills.

Skills tecnicas por tecnologia entram somente quando o projeto consumidor, o
pedido do usuario ou o plano aprovado declarar aquela superficie.

Planos executaveis devem declarar write owner, `target_files`,
`allowed_writes`, validators, gates, AC e primary route quando uma task puder
ser executada por agente `scoped-writer`. `loki-enrich-tasks` deve preservar ou
refinar esse escopo antes do dispatch por `loki-implement-feature`.

## Inicializacao Pos-Instalacao

Depois de instalar o Loki em um projeto consumidor aprovado, use somente
`loki-init` para criar ou auditar a documentacao inicial do projeto.

A execucao explicita de `loki-init` autoriza escrita somente em `docs/**` e
`planos/000-init-loki/**` do consumidor. O comando cria ou audita
`docs/loki-init/**`, `docs/index.xml` e a trilha operacional
`planos/000-init-loki/` com `interaction/fase1` e `builds/fase1` quando
necessario para registrar interacoes ou evidencias operacionais.

O init nao escreve em runtime, engine, assets, dados gerados, `.agents/**`,
`.codex/**`, `.claude/**`, `AGENTS.md` ou `CLAUDE.md`. Ele tambem nao valida
gameplay, UI, audio, build, save/load, integracoes ou estado persistido sem
human-validation posterior.

Agentes de dominio atuam como `init_inventory_domain_investigator` read-only
ou proposal-only e devolvem packets schema v1 com fontes, fatos, inferencias,
lacunas, conflitos e cobertura. O orquestrador valida os packets e chama
`catalogador` serialmente em `init-bootstrap-cataloger`,
`init-publication-batch` e `init-final-reconciliation`, preservando cobertura,
continuacao, materializacao e retomada. Nao ha escrita direta nem fallback por
investigador ou orquestrador; indisponibilidade do `catalogador` bloqueia.

### Extensao Opcional: RPG Maker MZ

Use `rpg-maker-mz-data-json` somente quando o projeto consumidor exigir
edicao ou revisao de superficies de dados RPG Maker MZ, como Database, Common
Events ou mapas.

Use `rpg-maker-mz-plugin-workflow` somente quando o projeto consumidor
exigir criar, editar, validar ou ativar plugins RPG Maker MZ.

Use `rpg-maker-mz-project-inventory` quando um agente game-dev atuar sobre
um projeto RPG Maker MZ e precisar de inventario compartilhado antes de handoff,
analise tecnica ou planejamento que dependa de Common Events, mapas, plugins,
assets ou save/load.

Essas skills sao extensoes especializadas opcionais. Elas nao sao
obrigatorias para feedback, analise tecnica, implementacao unificada,
retrospectiva ou melhoria continua do core Loki.

Para evoluir o pacote, use os criadores certos por tipo de artefato e valide contra `docs/package-authoring-guardrails.md`. O objetivo e transformar aprendizado em regra operacional sem depender de memoria da conversa.

## Quando Registrar Aprendizados

Use [Workflow de Aprendizado do Loki](loki-learning-workflow.md) como unica
referencia canonica para decidir entre ajuste local, retrospectiva, promocao
duradoura e backlog.

## Agents

- `standards-curator`: classifica aprendizados como universal, provavel-universal, project-specific ou backlog.
- `execution-knowledge-cataloger`: lê somente completion/evidence sanitizados
  persistidos e escreve uma única entry run-local; não altera shared state nem
  promove policy, e sua falha não bloqueia implementação.
- `retrospective-digester`: digere retrospectivas tecnicas em modo read-only,
  com fan-out por arquivo quando `loki-continuous-improvement` recebe multiplas
  retros.
- `bibliotecario`: consulta `docs/index.xml` antes de abrir a documentacao
  duradoura do consumidor.
- `catalogador`: unico writer de docs duradouros do consumidor; exige caller,
  mode, fontes e targets explicitos para manter `/docs` e o catalogo XML.
- `lf-domain-context-preflight`: preflight pessoal antes de cada task; consulta
  docs minimas, compara fontes atuais, registra freshness, conflitos e lacunas
  e nunca autocorrige `/docs`.
- `runtime-qa`: produz checklist e evidencia exigida; nunca simula
  confirmacao humana.
- `execution-context-reader`: extrai contexto em modo read-only da demanda,
  `analysis_file`, state, task e fontes locais permitidas para
  `loki-implement-feature`, sem escrever.
- `source-researcher`: mapeia fatos, lacunas e conflitos em pesquisa
  multi-fonte antes de analise, plano, feedback, enriquecimento ou promocao,
  sem decidir solucao nem escrever.
- `technical-implementer`: pode aplicar mudancas tecnicas como
  `scoped-writer` quando a task atribuir `target_files`; caso contrario,
  retorna proposta, validadores e gates.
- Agentes game-dev como `gameplay-engineer` e `narrative-designer` podem
  escrever mecanicas, conteudo narrativo, dialogos,
  quests, tuning ou artefatos equivalentes quando `loki-implement-feature`
  entregar session/domain preflights validos e envelope `task_scoped_writer`
  com target decision, arquivos, validators e gates.

## Contexto Duradouro do Consumidor

- O pacote Loki guarda regras do framework, nao fatos do projeto consumidor.
- Regras de negocio, lore, fluxo funcional e terminologia do projeto consumidor
  devem morar em `docs/**/*.md`.
- `docs/index.xml` e o catalogo preferencial para `bibliotecario` e
  `lf-index-navigator`.
- `AGENTS.md` e `CLAUDE.md` do consumidor recebem apenas roteamento minimo para
  dizer quando a LLM deve consultar `/docs`.

A matriz caller/mode e fechada: `loki-init` usa
`init-bootstrap-cataloger`, `init-publication-batch` e
`init-final-reconciliation`; `loki-continuous-improvement` e
`loki-implement-feature` usam `task_scoped_writer`; `loki-catalogar-docs` usa `task_scoped_writer` ou
`proposal-only`. Caller ou mode ausente ou cruzado bloqueia antes da escrita.

## Regra de Uso Seguro

Mantenha o diretorio do pacote como fonte auditavel. Instale em `.claude/`,
`.agents/` ou `.codex/` somente depois de approval especifico. Nao copie
`.agents/` ou `.codex/` como fonte normativa. Nao declare runtime validado sem
gate humano apropriado.

Quando a mudanca for no proprio pacote, nao pare em retrospectiva ou intuicao: atualize o artefato normativo correto, registre impacto no `manifest.yaml` se necessario e termine com validacao objetiva de estrutura e autocontencao.
