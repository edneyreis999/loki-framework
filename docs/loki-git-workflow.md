---
title: Loki Git Workflow And MCP Requirements
type: workflow
status: draft
created: 2026-07-10
self_contained: true
---

# Loki Git Workflow And MCP Requirements

O Loki expõe três comandos pequenos para Git flow:

- `loki-criar-branch`: cria branch local com base e nome aprovados.
- `loki-commit`: faz staging explicito e cria um commit local.
- `loki-abrir-pr`: publica a branch e abre Pull Request com approval.

## Dependencias

Operacao local exige apenas Git disponivel no shell do projeto consumidor.

Operacao GitHub completa usa, nesta ordem:

1. GitHub MCP quando o adaptador expuser ferramentas de repositorio, branch e
   Pull Request.
2. `gh` CLI autenticado como fallback.

O Loki nao instala nem configura MCP automaticamente. Se GitHub MCP e `gh` nao
estiverem disponiveis, `loki-abrir-pr` deve parar apos gerar a proposta de PR.

## Capacidades Minimas

Para branch local:

- `git branch --show-current`
- `git status --short`
- `git checkout -b` ou equivalente

Para commit:

- `git diff`, `git diff --cached`, `git status --short`
- `git add -- <pathspecs>`
- `git commit`

Para Pull Request no GitHub:

- GitHub MCP: lookup de repositorio, busca/criacao de branch e criacao de PR; ou
- `gh auth status`, `gh repo view`, `gh pr create`

## Regras

- Nenhum comando Git flow executa operacao destrutiva.
- Commit na branch default exige pedido explicito.
- Push e PR exigem approval.
- Provider nao GitHub deve parar ate existir skill ou comando especifico.
