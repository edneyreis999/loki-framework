---
title: Loki Framework Local README
type: install-readme
status: draft
created: 2026-06-24
scope: local-project-package
---

# Loki Framework Local

Pacote local do Loki Framework para projetos de software e jogos,
agnostico de engine/framework, dividido em `agents`, `commands`, `skills`,
`templates` e `docs`.

Este pacote e a fonte auditavel. Instalar significa copiar ou sincronizar estes
arquivos para pastas locais do projeto, depois de approval humano. Para Codex,
o caminho principal e o instalador por symlink em
`scripts/install-loki-symlinks.py`, mantendo este repositorio como fonte
versionada. Instalacao global esta fora de escopo.

Conhecimento especifico do projeto consumidor nao pertence ao pacote. O destino
duradouro desse tipo de contexto e `/docs` do consumidor, com `docs/index.xml`
como catalogo navegavel.

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
├── commands/
├── skills/
├── scripts/
├── templates/
└── docs/
```

## Claude Code

Destino local sugerido:

```text
.claude/commands/loki/
.claude/agents/
.claude/skills/
```

Mapeamento:

```text
commands/*.md -> .claude/commands/loki/
agents/*.md   -> .claude/agents/
skills/*/     -> .claude/skills/
templates/*.md -> .claude/templates/loki/
```

Dry-run manual recomendado antes de aplicar:

```bash
find "$PACKAGE_ROOT" -maxdepth 4 -type f | sort
find .claude/commands .claude/agents .claude/skills -maxdepth 2 -type f 2>/dev/null | sort
```

Aplicar somente apos approval explicito:

```bash
mkdir -p .claude/commands/loki .claude/agents .claude/skills .claude/templates/loki
cp "$PACKAGE_ROOT"/commands/*.md .claude/commands/loki/
cp "$PACKAGE_ROOT"/agents/*.md .claude/agents/
cp -R "$PACKAGE_ROOT"/skills/* .claude/skills/
cp "$PACKAGE_ROOT"/templates/*.md .claude/templates/loki/
```

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
.agents/commands/loki/<command>.md -> $PACKAGE_ROOT/commands/<command>.md
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

Instalacoes antigas podem ter `.agents/agents` como symlink para o diretorio
inteiro `agents/`. O instalador atual usa um link por agente para respeitar
`install-scopes.json`; se esse symlink legado existir, o dry-run bloqueia a
instalacao ate ele ser removido no destino aprovado.

Validacao pos-instalacao:

```bash
python3 "$PACKAGE_ROOT/scripts/validate-install-scopes.py"
find -L "$DEST/.agents/skills" -maxdepth 2 -name SKILL.md | sort
find -L "$DEST/.agents/commands/loki" -maxdepth 1 -name 'loki-*.md' | sort
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
rm -f .claude/commands/loki/loki-*.md
rm -f .claude/agents/standards-curator.md .claude/agents/retrospective-digester.md .claude/agents/runtime-qa.md .claude/agents/execution-context-reader.md .claude/agents/source-researcher.md .claude/agents/technical-implementer.md .claude/agents/bibliotecario.md .claude/agents/catalogador.md
rm -rf .claude/skills/loki-feedback .claude/skills/loki-enrich-tasks .claude/skills/lf-run-plan-execution .claude/skills/loki-retrospectiva-tecnica .claude/skills/lf-command-creator .claude/skills/lf-agent-creator .claude/skills/lf-skill-creator .claude/skills/lf-index-navigator .claude/skills/lf-tech-analysis-authoring .claude/skills/lf-action-plan-authoring .claude/skills/rpg-maker-mz-data-json .claude/skills/rpg-maker-mz-plugin-workflow
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
