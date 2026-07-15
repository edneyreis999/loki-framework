---
name: loki:criar-branch
type: command
status: draft
domain: git
required_skills:
  - lf-git-workflow
required_commands: []
execution_profile:
  model_class: coding
  default_effort: medium
  max_effort: high
  escalation_signals:
    - detached HEAD
    - uncommitted changes while changing base branch
    - existing local or remote branch name
    - ambiguous default branch or remote
  handoff_effort:
    coding: medium
    validator: low
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:criar-branch

## Purpose

Criar uma branch Git segura e revisavel para novo trabalho, com nome derivado
do objetivo ou do diff local, sem trocar base ou publicar estado sem gate
humano.

## Inputs

- Descricao opcional do trabalho.
- Tipo opcional: `feat`, `fix`, `ref`, `docs`, `test`, `chore`, `ci`, `build`,
  `perf`, `style`, `meta` ou `license`.
- Base branch opcional.
- Prefixo de autor opcional quando nao houver usuario GitHub detectavel.

## Outputs

- Branch criada localmente.
- Registro textual com base usada, branch anterior, branch nova e qualquer
  decisao humana tomada.

## Allowed Writes

- Referencias Git locais necessarias para criar e trocar para a branch nova.
- Stash temporario somente com approval explicito quando houver mudancas locais
  bloqueando troca de base.

## Forbidden Writes

- Arquivos do working tree, exceto restauracao de stash aprovada.
- `.claude/**`, `.agents/**` e `.codex/**`.
- Push remoto, commit, PR, merge, rebase destrutivo, reset ou checkout
  destrutivo.

## Required Skills

- `lf-git-workflow` para preflight, nomeacao, gates, validadores e fallback de
  GitHub MCP/`gh`.

## Workflow

1. Carregar `lf-git-workflow`.
2. Ler estado minimo: branch atual, `git status --short`, remotes e default
   branch quando detectavel.
3. Se houver descricao, usar como fonte principal. Se nao houver, inferir pelo
   diff local; se nao houver diff suficiente, perguntar objetivo do trabalho.
4. Gerar nome no formato `<autor>/<tipo>/<descricao-curta>` quando houver autor
   detectavel; caso contrario usar `<tipo>/<descricao-curta>` ou perguntar
   prefixo preferido.
5. Validar caracteres, tamanho, colisao local/remota e base.
6. Se a branch atual nao for a base pretendida, explicar o delta e pedir
   approval antes de trocar de base. Se houver mudancas locais, oferecer stash
   temporario ou criar a branch a partir da branch atual.
7. Pedir approval final mostrando branch, base e comando planejado.
8. Criar a branch localmente com comando Git apropriado e restaurar stash
   aprovado, se houver.
9. Reportar resultado e proximos comandos possiveis, sem executar commit, push
   ou PR.

## Validators

- `git branch --show-current` retorna a branch nova.
- `git show-ref --verify refs/heads/<branch>` confirma a referencia local.
- Mudancas locais preexistentes permanecem visiveis em `git status --short`.
- Nenhum push, commit ou PR foi executado.

## Human Gates

- `approval` antes de criar a branch.
- `approval` antes de trocar de base quando a branch atual nao for a base.
- `approval` antes de stashear ou restaurar mudancas locais.

## Stop Conditions

- Repositorio Git ausente.
- Base branch ambigua e usuario nao confirmou uma base.
- Branch local ou remota ja existe e o usuario nao escolheu outro nome.
- Detached HEAD sem confirmacao de base.
- Mudancas locais impedem troca de base e usuario nao aprovou stash nem branch
  a partir da branch atual.

## Resume Contract

Registrar objetivo, branch atual, base escolhida, nome proposto, decisoes
humanas, comandos executados, estado final de branch e validadores.
