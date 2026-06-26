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
arquivos para pastas locais do projeto, depois de approval humano. Instalacao
global esta fora de escopo.

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
├── commands/
├── skills/
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

Uso local recomendado:

1. Mantenha o diretorio do pacote como fonte auditavel.
2. Leia `manifest.yaml` para entender componentes e destinos.
3. Use `docs/usage-guide.md` como guia operacional.
4. Quando houver approval, copie skills e artefatos para uma area local do projeto.

Destino local sugerido para staging Codex:

```text
.agents/commands/
.agents/agents/
.agents/skills/
```

Mapeamento:

```text
commands/*.md -> .agents/commands/
agents/*.md   -> .agents/agents/
skills/*/     -> .agents/skills/
```

Dry-run manual recomendado:

```bash
find "$PACKAGE_ROOT"/{commands,agents,skills} -type f | sort
find .agents/commands .agents/agents .agents/skills -maxdepth 2 -type f 2>/dev/null | sort
```

Aplicar somente apos approval explicito:

```bash
mkdir -p .agents/commands .agents/agents .agents/skills
cp "$PACKAGE_ROOT"/commands/*.md .agents/commands/
cp "$PACKAGE_ROOT"/agents/*.md .agents/agents/
cp -R "$PACKAGE_ROOT"/skills/* .agents/skills/
```

Gate: `.agents/` e deny-by-default e local/efemero. Nao copie artefatos de `.agents/` para o pacote. Escrever em `.agents/**` exige approval humano posterior.

## Sync, Risco e Rollback

Use copia simples (`cp`) para o MVP. Evite `rsync --delete`, overwrite destrutivo e comandos que apaguem arquivos.

Antes de aplicar, registre:

- origem;
- destino;
- lista de arquivos;
- approval humano;
- plano de rollback.

Rollback simples:

```bash
rm -f .claude/commands/loki/loki-*.md
rm -f .claude/agents/standards-curator.md .claude/agents/runtime-qa.md .claude/agents/execution-context-reader.md .claude/agents/source-researcher.md .claude/agents/technical-implementer.md .claude/agents/bibliotecario.md .claude/agents/catalogador.md
rm -rf .claude/skills/loki-feedback .claude/skills/loki-enrich-tasks .claude/skills/loki-run-plan-execution .claude/skills/loki-retrospectiva-tecnica .claude/skills/loki-command-creator .claude/skills/loki-agent-creator .claude/skills/loki-skill-creator .claude/skills/loki-index-navigator .claude/skills/loki-tech-analysis-authoring .claude/skills/loki-action-plan-authoring .claude/skills/loki-rpg-maker-mz-data-json .claude/skills/loki-rpg-maker-mz-plugin-workflow
rm -f .agents/commands/loki-*.md
rm -f .agents/agents/standards-curator.md .agents/agents/runtime-qa.md .agents/agents/execution-context-reader.md .agents/agents/source-researcher.md .agents/agents/technical-implementer.md .agents/agents/bibliotecario.md .agents/agents/catalogador.md
rm -rf .agents/skills/loki-feedback .agents/skills/loki-enrich-tasks .agents/skills/loki-run-plan-execution .agents/skills/loki-retrospectiva-tecnica .agents/skills/loki-command-creator .agents/skills/loki-agent-creator .agents/skills/loki-skill-creator .agents/skills/loki-index-navigator .agents/skills/loki-tech-analysis-authoring .agents/skills/loki-action-plan-authoring .agents/skills/loki-rpg-maker-mz-data-json .agents/skills/loki-rpg-maker-mz-plugin-workflow
```

Nao execute rollback sem confirmar que os arquivos removidos vieram desta instalacao.

## Guardrails

- Nao instalar globalmente.
- Nao alterar o runtime/engine/framework do consumidor durante instalacao documental.
- Nao declarar comportamento perceptivel, estado runtime, integracoes ativas
  ou superficies sensiveis declaradas como validadas sem gate humano apropriado.
- Nao promover aprendizado para standard, command, skill ou agent sem fonte, destino, verificacao e approval.
- Nao guardar regra de negocio do projeto consumidor no pacote Loki; esse
  conteudo pertence a `/docs` e `docs/index.xml` do consumidor.
