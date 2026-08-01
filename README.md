---
title: Loki Framework Local README
type: install-readme
status: draft
created: 2026-06-24
doc_id: loki-framework-local-readme
version: 1.0.0
last_updated: 2026-07-27
scope: local-project-package
not_scope: consumer project policy, package installation approval, or runtime validation
authority: Approved Loki package policy and this package source
canonical_source: README.md
intended_llm_task: routing
source_priority:
  - approved human decisions and package policy
  - this README and linked package documentation
  - manifest and install-scopes machine-readable state
  - examples and consumer-provided paths
known_conflicts: []
replaced_by: null
---

# Loki Framework Local

Pacote local do Loki Framework para projetos de software e jogos,
agnostico de engine/framework, dividido em `agents`, command bundles em `skills`,
`templates` e `docs`.

Este pacote e a fonte auditavel. Instalar significa copiar ou sincronizar estes
arquivos para pastas locais do projeto, depois de approval humano. Para Codex,
o caminho principal e o instalador por symlink em
`scripts/install-loki-symlinks.py`, mantendo este repositorio como fonte
versionada. Instalacao global esta fora de escopo.

Conhecimento especifico do projeto consumidor nao pertence ao pacote. O destino
duradouro desse tipo de contexto e `/docs` do consumidor, com `docs/index.xml`
como catalogo obrigatorio de navegacao. Sem esse arquivo, a navegacao deve
falhar explicitamente; `index.md` nao e fallback para documentacao do
consumidor.

Fluxos principais:

- `loki-demand-text-improver`: enriquece uma demanda inicial antes de analise
  ou planejamento e termina em um unico Markdown, sem executar etapas
  posteriores.
- `loki-implement-feature`: caminho publico direto de demanda + analise
  Markdown para plano persistido, implementacao autonoma, validacao por task,
  dashboard e teste manual.
- `loki-agentic-development`: caminho avancado de demanda para analise
  agentica, gates, um unico handoff ao `loki-implement-feature`, digest e
  backlog.
- `loki-deep-research`: pesquisa profunda na internet com fontes citadas,
  verificacao cruzada, contradicoes e handoff para analise ou plano.
- `loki-generate-inferences`: prepara, de forma opt-in, um unico artefato
  deterministico de pre-investigacao sob `planos/` do consumidor; nao inicia
  investigacao, dispatch, CI ou outro workflow.
- `loki-continuous-improvement`: recebe fontes aprovadas ou um plano completo,
  produz candidate v2 current-only, promove por roots independentes e prova
  recuperação e independência do conhecimento sem decidir lifecycle/exclusão.

Use `loki-demand-text-improver` quando a demanda ainda precisar explicitar
objetivo, contexto, escopo, requisitos, restricoes, aceite, validators,
premissas, riscos ou referencias. O command valida diretamente os inputs, o
destino e o target; ele não exige Plan Mode nem outro estado de sessão. O
`destination` deve ser um diretorio existente e gravavel. Exemplo com entrada
em arquivo:

```text
loki-demand-text-improver
analysis_input: docs/Demanda.md
source_paths: [docs/contexto-produto.md]
destination: planos/027-demanda/
```

Nesse caso, o target e `planos/027-demanda/Demanda-improved.md`. Para texto
inline, o nome e `improved-demand.md`. Uma colisao bloqueia sem sobrescrever ou
autonumerar. O command termina nesse Markdown enriquecido: nao inicia
`loki-tech-analysis`, decisao humana, plano, `loki-agentic-development` ou
execucao. O usuario escolhe o proximo workflow em um novo pedido.

`loki-generate-inferences` e outra preparacao opt-in, para quando uma entrada
de analise e fontes locais permitidas precisarem virar um unico core canonico
de inferencias antes da investigacao. Ele requer `analysis_input` e um
`destination` que seja diretorio existente sob `<consumer-root>/planos/`, sem
symlink ou traversal. Depois do digest da demanda, resolve um target versionado
deterministico: slug NFKD/ASCII do stem para input em arquivo, ou
`inferences-<digest12>` para inline; se `<base>.md` existir, escolhe antes da
approval o menor `<base>-vN.md` ausente. Internamente, deriva piso minimo 8,
nenhum teto de candidatos e pagina de recuperacao 20. O piso nao encerra a
geracao e a pagina nao limita a recuperacao total. Preserva todo candidato
material distinto e termina somente por saturacao semantica; se o contexto
interromper antes disso, retorna parcial com cursor e superficies nao
exploradas. Saturacao abaixo do piso e valida sem padding. O limite persistente
3 existe somente para armazenamento/manutencao do catalogo. Custo e impacto
nao influenciam essa disposicao pre-investigacao. A approval vincula diretorio canonico,
target exato,
basename/versao, before-state/snapshot e um create exclusivo. Colisao posterior
invalida a approval e bloqueia sem retry; exige nova resolucao e nova approval.
O command cria somente esse arquivo uma vez e termina em
`pre-investigation-complete`: nao faz fan-out, handoff, agente, pesquisa web,
CI, mutacao de catalogo ou chamada downstream. Uma pessoa pode escolher, em
novo pedido, uma rota posterior permitida — por exemplo
`loki-deep-analysis` — usando o artefato validado.

Na investigacao, `loki-deep-analysis` executa no maximo 3 rodadas de ate 6
investigacoes delegadas, em subondas de concorrencia 2. Cada rodada espera seus
handoffs terminais, reclassifica todas as inferencias e so abre a seguinte se
ainda houver investigacao material util. Uma inferencia pode voltar em rodada
posterior com nova pergunta, justificativa material e IDs novos. Custo e apenas
telemetria. A terceira rodada encerra a analise; o command retorna a rota
downstream sem invoca-la automaticamente.

## Implementar uma feature

Use `loki-implement-feature` quando houver uma demanda nao vazia e uma analise
Markdown legivel e decision-complete. A invocacao recebe `demand`,
`analysis_file`, `plan_directory` opcional e `retry_limit` opcional, com default
3 para correcoes medium/major. Ela materializa ou retoma o plano em disco,
registra cada target e owner antes da escrita e executa o DAG sem uma segunda
fronteira publica entre planejar e executar.

Cada task precisa de criterio de aceite observavel e exatamente uma rota
primaria: validator deterministico ou Write Test Agent independente. Findings,
respostas do Writer, retestes e retry debits ficam persistidos. Falha esgotada
interrompe apenas dependentes transitivos; branches independentes continuam.
Findings minor nao consomem o budget e cedem o scheduler entre ciclos.

A resposta final e um dashboard derivado do estado persistido: status, units,
targets alterados e inferidos, ACs e evidencias, validators, retries, riscos,
resume e passos de teste manual completos. `pending-human-validation` aparece
somente na reconciliacao final quando for a unica condicao restante.

`loki-agentic-development` permanece uma rota distinta para quem precisa de
POVs, sintese agentica, cross-review, digest e backlog. Depois de produzir ou
validar a analise Markdown, ele faz um unico handoff ao mesmo
`loki-implement-feature`; nao existe um executor publico alternativo.

Este e um contrato current-only: nao ha alias, wrapper, conversor, fallback ou
segunda autoridade publica para formatos e comandos substituidos.

Identidade operacional:

- `skills/loki-<stem>/` representa um command operacional completo, com Input
  no `SKILL.md`, Execution/Response em `references/` e template em `assets/`;
- `type: command` e `serialization: skill-bundle` preservam a taxonomia mesmo
  que o command seja distribuido por uma superficie baseada em skills;
- `lf-*` e namespaces de dominio ou tecnologia representam skills
  operacionais reutilizaveis;
- o caminho `skills/**` ou o formato `SKILL.md` nao reclassifica uma projecao
  `loki-*` como skill.

Os exemplos abaixo usam `PACKAGE_ROOT` para manter o pacote portavel entre projetos:

```bash
PACKAGE_ROOT="$(pwd)"
```

## Conteudo

```text
002-loki-framework-local/
├── manifest.yaml
├── agents/
├── codex/
├── skills/
├── scripts/
├── templates/
└── docs/
```

## Claude Code

Destino local sugerido:

```text
.claude/agents/
.claude/skills/
```

Mapeamento:

```text
agents/*.md   -> .claude/agents/
skills/*/     -> .claude/skills/ (inclui os command bundles loki-*)
templates/*.md -> .claude/templates/loki/
```

Para Claude Code, aplique os mesmos profiles de `install-scopes.json`. Em um
consumer, copie somente skills e agents classificados como `both` ou
`consumer-only`; nunca use `cp -R skills/*` nesse profile, pois isso também
copiaria artefatos `internal-only`.

Dry-run manual recomendado antes de aplicar: gere e revise a lista exata a
partir de `install-scopes.json`, confirme que cada destino ainda não existe e
registre essa lista para rollback. Para `consumer`, a lista esperada contém 58
skills, 25 agents e 25 projecoes Codex; `templates/` e compartilhado por todos
os perfis.

```bash
find "$PACKAGE_ROOT" -maxdepth 4 -type f | sort
find .claude/agents .claude/skills -maxdepth 2 -type f 2>/dev/null | sort
```

Aplicar somente após approval explícito, copiando cada source selecionado para
seu destino exato. O exemplo amplo abaixo é permitido apenas para profile
`all`, nunca para um consumer:

```bash
mkdir -p .claude/agents .claude/skills .claude/templates/loki
# profile all somente:
cp "$PACKAGE_ROOT"/agents/*.md .claude/agents/
cp -R "$PACKAGE_ROOT"/skills/* .claude/skills/
cp "$PACKAGE_ROOT"/templates/*.md .claude/templates/loki/
```

Depois da cópia filtrada, confirme que `loki-self-healing`,
`loki-knowledge-extraction-analysis`, `lf-internal-command-workflows` e os dois
agentes de artefatos do framework foram registrados com escopo `both`. Essa
disponibilidade não concede permissão para alterar o projeto consumidor: os
agentes e qualquer mutação de artefato consolidado do pacote continuam
limitados a um package root e a um envelope `destination_scope: package`.
Relatórios transitórios permitidos pelo contrato de análise preservam seus
próprios targets e nunca autorizam essa mutação. Não sobrescreva destino
existente; conflito exige intervenção manual e novo dry-run.

Gate: escrever em `.claude/**` exige approval humano posterior. Este README nao autoriza a copia por si so.

## Codex

Uso local recomendado por symlink:

1. Mantenha o diretorio do pacote como fonte auditavel.
2. Leia `manifest.yaml` para entender componentes e destinos.
3. Escolha o perfil: `consumer`, `package-source` ou `all`.
4. Rode `--dry-run` no destino alvo e revise conflitos.
5. Aplique com `--yes` somente apos approval especifico para o destino.

Destino local criado pelo instalador:

```text
.agents/skills/<skill-name> -> $PACKAGE_ROOT/skills/<skill-name>
.agents/agents/<agent>.md   -> $PACKAGE_ROOT/agents/<agent>.md
.agents/templates          -> $PACKAGE_ROOT/templates
.codex/agents/<agent>.toml -> $PACKAGE_ROOT/codex/agents/<agent>.toml
```

Perfis:

- `consumer`: instala artefatos `both` e `consumer-only`.
- `package-source`: instala artefatos `both` e `internal-only`.
- `all`: instala todos os escopos para validacao/desenvolvimento.

`install-scopes.json` e a fonte machine-readable dos escopos. O perfil default
do script e `consumer`.

Os comandos `loki-implement-feature` e `loki-agentic-development` sao instalados
nos perfis que incluem artefatos `both`. Nenhum deles autoriza instalacao ou
sincronizacao por si so; dry-run, approval de destino e validacao continuam
obrigatorios.

Dry-run recomendado:

```bash
DEST="/tmp/loki-symlink-test"
python3 "$PACKAGE_ROOT/scripts/install-loki-symlinks.py" --dest "$DEST" --dry-run --profile consumer
```

Aplicar somente apos approval explicito:

```bash
python3 "$PACKAGE_ROOT/scripts/install-loki-symlinks.py" --dest "$DEST" --yes --profile consumer
```

O script grava o manifest de auditoria no destino:

```text
$DEST/.agents/loki-installation-manifest.json
```

O perfil instalado e tratado como parte do estado do destino. Se o destino ja
tiver manifest Loki de outro perfil, ou se existirem artefatos Loki fora do
perfil solicitado, o instalador bloqueia a execucao. Trocar entre `consumer`,
`package-source` e `all` exige rollback manual dos links registrados no manifest
anterior e um novo dry-run limpo para o perfil desejado; a troca nao e
incremental.

O instalador aceita somente o layout schema 2. Se encontrar `.agents/agents`
como symlink de diretorio, `.agents/commands` ou um manifest com links de
command/historico de remocao, ele falha sem escrever no destino. Resolva o
layout existente manualmente fora do instalador e rode um novo dry-run.

Contratos removidos seguem politica de rejeicao, nunca de conversao automatica:
o estado agentic aceita somente manifest 4, report 5 e digest 4 (mantendo WTR
schema 1); o catalogo de inferencias usa somente XML v2; e a projecao retirada
nao possui superficie instalavel. Os formatos schema 1 que pertencem a evidencia, conhecimento
de execucao e subdocumentos analiticos continuam contratos atuais de suas
proprias familias.

Validacao pos-instalacao:

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
assert data.get("install_profile") == "consumer"
assert all("install_scope" in link for link in data.get("links", []))
assert all(link.get("type") != "command" for link in data.get("links", []))
PY
git -C "$DEST" status --short .agents .codex
```

Use `--replace` somente com approval separado para o caminho e modo de
execucao. Sem `--replace`, conflitos bloqueiam a instalacao em vez de
sobrescrever arquivos reais ou links divergentes.

Gate: `.agents/**` e `.codex/**` sao destinos deny-by-default e locais ao
projeto consumidor. Nao copie artefatos de `.agents/**` ou `.codex/**` para o
pacote. Escrever nesses destinos exige approval humano posterior.

## Sync, Risco e Rollback

Para Claude Code, use copia simples (`cp`) no MVP. Para Codex, use o script por
symlink. Evite `rsync --delete`, overwrite destrutivo e comandos que apaguem
arquivos.

Antes de aplicar, registre:

- origem;
- destino;
- lista de arquivos;
- approval humano;
- plano de rollback.

Para Codex, use o manifest gerado no destino para auditar origem, destino,
status e modo aplicado antes de qualquer remocao manual.

Rollback simples:

```bash
rm -f .claude/agents/standards-curator.md .claude/agents/retrospective-digester.md .claude/agents/runtime-qa.md .claude/agents/execution-context-reader.md .claude/agents/source-researcher.md .claude/agents/technical-implementer.md .claude/agents/bibliotecario.md .claude/agents/catalogador.md
rm -rf .claude/skills/loki-feedback .claude/skills/loki-enrich-tasks .claude/skills/loki-implement-feature .claude/skills/lf-implement-feature-execution .claude/skills/loki-retrospectiva-tecnica .claude/skills/lf-command-creator .claude/skills/lf-agent-creator .claude/skills/lf-skill-creator .claude/skills/lf-index-navigator .claude/skills/lf-tech-analysis-authoring .claude/skills/lf-action-plan-authoring .claude/skills/rpg-maker-mz-data-json .claude/skills/rpg-maker-mz-plugin-workflow
```

Para Codex, o rollback e orientado pelo manifest de instalacao. Remova somente
os destinos listados em `$DEST/.agents/loki-installation-manifest.json` depois
de confirmar que cada destino e um symlink para `PACKAGE_ROOT`.

Nao execute rollback sem confirmar que os arquivos removidos vieram desta
instalacao.

## Guardrails

- Nao instalar globalmente.
- Nao alterar o runtime/engine/framework do consumidor durante instalacao documental.
- Nao declarar comportamento perceptivel, estado runtime, integracoes ativas
  ou superficies sensiveis declaradas como validadas sem gate humano apropriado.
- Nao promover aprendizado para standard, command, skill ou agent sem fonte, destino, verificacao e approval.
- Nao guardar regra de negocio do projeto consumidor no pacote Loki; esse
  conteudo pertence a `/docs` e `docs/index.xml` do consumidor.
