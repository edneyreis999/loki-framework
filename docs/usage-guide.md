---
title: Guia de Uso do Loki Framework Local
type: usage-guide
status: draft
created: 2026-06-24
scope: local-project-package
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
- [Workflow de Execucao de Plano do Loki](loki-plan-execution-workflow.md):
  descreve o caminho manual e o caminho integrado v2 para transformar uma
  descricao curta em analise, preflight de decisoes humanas, plano, tasks,
  escrita serializada, validacao e evidencia.
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
risco, validators e gates para o decision preflight e o action plan.

Use `loki-deep-analysis` de forma opt-in quando a demanda se beneficiar de
descoberta de tecnologias, consulta seletiva a inferencias catalogadas,
geracao contextual de candidatos ou investigacoes independentes. Essa e uma
rota especializada para a mesma etapa: ela nao chama nem aninha
`loki-tech-analysis`. Seu report, seus eventos imutaveis e seus candidatos
`unreviewed` sao evidencia rastreavel; nao alteram o catalogo e nao comprovam
validacao de runtime.

`loki-generate-inferences` e um fork opcional anterior a investigacao. Ele
recebe `analysis_input`, `source_paths` locais permitidos e um `destination`
aprovado; o destino deve ser exatamente um novo arquivo `.md` abaixo de
`<consumer-root>/planos/`, com parent existente, sem symlink, traversal ou
colisao. Seu unico output e esse Markdown, com um core canonico de preparacao
de inferencias, criado uma unica vez e terminal em
`pre-investigation-complete`. O command nao investiga, nao cria fan-out,
handoff ou agent run, nao pesquisa a web, nao roda CI, nao invoca workflow
downstream e nao altera o catalogo. Depois da resposta, a pessoa escolhe
manualmente uma rota posterior permitida, como `loki-deep-analysis`; o command
nao a agenda nem a invoca.

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
exigem technical review e approval root-bound antes da mutacao; purge exige
dry-run completo e uma approval JIT separada, posterior, single-use e ligada a
root, IDs, paths, hashes e digests exatos. `framework-artifact-writer` escreve
somente contratos, schemas, scripts, policy e docs do pacote; `catalogador`
escreve somente docs duradouros do consumidor. Nenhum dos dois escreve `.loki`.

## Caminho Integrado v2

Use `loki-agentic-development` quando a demanda deve seguir o caminho completo:
demanda simples, analise agentica, gates humanos materiais antes do plano,
action plan, execucao autonoma, completion reports, digest e backlog.

Use o caminho manual quando precisar controlar cada etapa separadamente:
`loki-deep-research` quando depender de pesquisa web citada,
uma rota de analise (`loki-tech-analysis` por padrao ou `loki-deep-analysis`
opt-in; opcionalmente precedida por `loki-generate-inferences` quando houver
preparacao deterministica de candidatos), `loki-human-decision-preflight`,
`loki-generate-action-plan`, `loki-enrich-tasks` quando aplicavel e
`loki-run-plan` por fase ou task.

O fluxo integrado nao substitui `loki-run-plan`; ele o preserva como executor
manual e pode usa-lo como executor delegado depois que o plano existir. O fluxo
integrado tambem nao promove aprendizado duradouro automaticamente. Digest,
backlog, reports e retrospectivas viram entrada para
`loki-continuous-improvement` somente por decisao posterior.

Nos dois executores, completion/evidence mínimo é persistido primeiro. Quando
há atrito ou aprendizado material, `execution-knowledge-cataloger` pode criar
em paralelo uma entry exclusiva no run. O fluxo principal não espera por esse
enriquecimento: atraso ou falha vira `partial`, `failed` ou `unsupported`; lookup
trivial pode ser `skipped-nonmaterial`. Somente
`loki-continuous-improvement` promove conhecimento depois.

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
- `technical-review`: para mudanca em command, skill, agent, template, validator ou doc consolidado.

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
de `loki-tech-analysis` e planos de `loki-generate-action-plan`, que continuam
high effort. Implementacao de codigo
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
`loki-human-decision-preflight`, `loki-agentic-development`,
`loki-enrich-tasks` e `loki-retrospectiva-tecnica`) expõem commands Loki por
meio de `SKILL.md`, references e assets, e continuam sendo commands operacionais.

As skills core (`lf-agentic-orchestration`, `lf-run-plan-execution`,
`lf-execution-knowledge-capture`,
`lf-command-creator`, `lf-agent-creator`, `lf-skill-creator`,
`lf-index-navigator`, `lf-tech-analysis-authoring`, `lf-analytic-inference`,
`lf-action-plan-authoring` e `lf-template-library`) fornecem conhecimento e
procedimentos reutilizáveis chamados pelos commands.

Juntas, essas superfícies governam entrevista, autoria de analises, preflight
de decisoes humanas, planos, orquestracao agentica, templates, enriquecimento
de tasks, execucao de fase, retrospectiva, navegacao de documentacao e
evolucao controlada de commands, agents e skills.

Skills tecnicas por tecnologia entram somente quando o projeto consumidor, o
pedido do usuario ou o plano aprovado declarar aquela superficie.

Planos executaveis devem declarar write owner, `target_files`,
`allowed_writes`, validators e gates quando uma task puder ser executada por
agente `scoped-writer`. `loki-enrich-tasks` deve preservar ou refinar esse
escopo antes de `loki-run-plan`.

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
obrigatorias para feedback, analise tecnica, plano de acao, execucao de plano,
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
- `execution-context-reader`: extrai contexto em modo read-only para
  `loki-run-plan`, usando `DIR_ANALISE`, tasks e fontes locais permitidas sem
  escrever.
- `source-researcher`: mapeia fatos, lacunas e conflitos em pesquisa
  multi-fonte antes de analise, plano, feedback, enriquecimento ou promocao,
  sem decidir solucao nem escrever.
- `technical-implementer`: pode aplicar mudancas tecnicas como
  `scoped-writer` quando a task atribuir `target_files`; caso contrario,
  retorna proposta, validadores e gates.
- Agentes game-dev como `gameplay-engineer` e `narrative-designer` podem
  escrever mecanicas, conteudo narrativo, dialogos,
  quests, tuning ou artefatos equivalentes quando `loki-run-plan` entregar
  envelope `task_scoped_writer` com arquivos, validators e gates.

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
`init-final-reconciliation`; `loki-continuous-improvement` e `loki-run-plan`
usam `task_scoped_writer`; `loki-catalogar-docs` usa `task_scoped_writer` ou
`proposal-only`. Caller ou mode ausente ou cruzado bloqueia antes da escrita.

## Regra de Uso Seguro

Mantenha o diretorio do pacote como fonte auditavel. Instale em `.claude/`,
`.agents/` ou `.codex/` somente depois de approval especifico. Nao copie
`.agents/` ou `.codex/` como fonte normativa. Nao declare runtime validado sem
gate humano apropriado.

Quando a mudanca for no proprio pacote, nao pare em retrospectiva ou intuicao: atualize o artefato normativo correto, registre impacto no `manifest.yaml` se necessario e termine com validacao objetiva de estrutura e autocontencao.
