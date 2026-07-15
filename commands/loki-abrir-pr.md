---
name: loki:abrir-pr
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
    - branch has uncommitted changes
    - branch is not pushed or upstream is ambiguous
    - provider is not GitHub
    - PR body depends on issue tracker or release policy
    - repository has a required PR template
  handoff_effort:
    coding: medium
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:abrir-pr

## Purpose

Abrir um Pull Request revisavel a partir da branch atual, usando GitHub MCP
quando disponivel ou `gh` autenticado como fallback, com titulo e corpo gerados
do diff entre base e head.

## Inputs

- Base branch opcional.
- Titulo opcional.
- Corpo opcional.
- Flag opcional para PR draft.
- Referencias opcionais de issue, ticket, plano ou validadores.

## Outputs

- Pull Request criado ou proposta de PR pronta para aprovacao.
- URL do PR quando criado.
- Base, head, titulo, corpo, commits incluidos e validadores.

## Allowed Writes

- Push da branch atual para o remote aprovado.
- Criacao de PR no provedor remoto aprovado.

## Forbidden Writes

- Alteracoes no working tree.
- Commits automaticos para resolver pendencias; use `loki:commit`.
- Merge, auto-merge, labels, reviewers, milestones ou assignees sem pedido
  explicito.
- `.claude/**`, `.agents/**` e `.codex/**`.

## Required Skills

- `lf-git-workflow` para preflight de PR, composicao de titulo/corpo, uso de
  GitHub MCP/`gh`, gates e validadores.

## Tooling

- Preferir GitHub MCP quando o adaptador expuser ferramenta de Pull Request
  compativel, como `create_pull_request`, e houver repo/head/base resolvidos.
- Usar `gh pr create` como fallback quando `gh` estiver instalado e autenticado.
- Se o remote nao for GitHub, parar e reportar que o comando ainda nao cobre o
  provedor; nao assumir GitHub para conceitos genericos de review.

## Workflow

1. Carregar `lf-git-workflow`.
2. Ler branch atual, default/base branch, remote, upstream, `git status
   --short`, commits `BASE..HEAD` e diff `BASE...HEAD`.
3. Se houver mudancas nao commitadas, parar e recomendar `loki:commit` ou
   exclusao consciente das mudancas.
4. Confirmar que a branch atual nao e a base/default.
5. Confirmar ou detectar base branch. Se ambigua, perguntar.
6. Se a branch nao estiver publicada, mostrar remote e pedir approval antes de
   `git push -u`.
7. Gerar titulo convencional a partir dos commits ou argumento fornecido.
8. Gerar corpo com: resumo, motivacao, mudancas principais, validadores
   executados/nao executados e referencias.
9. Mostrar titulo e corpo completos para approval.
10. Criar PR via GitHub MCP preferencialmente; se indisponivel, usar `gh pr
    create` com os mesmos dados aprovados.
11. Reportar URL, base/head e status draft/ready.

## Validators

- `git status --short` esta limpo ou contem apenas mudancas explicitamente
  deixadas fora do PR.
- `git log BASE..HEAD --oneline` tem ao menos um commit.
- `git diff BASE...HEAD --stat` foi revisado.
- Branch remota existe antes da criacao do PR.
- PR criado aponta para a base e head aprovadas.

## Human Gates

- `approval` antes de push.
- `approval` antes de criar PR.
- `approval` antes de ignorar template de PR existente ou adaptar seu conteudo.

## Stop Conditions

- Repositorio Git ausente.
- Branch atual e default/base.
- Nenhum commit entre base e head.
- Mudancas nao commitadas relevantes.
- Remote/provedor ambiguo ou nao suportado.
- GitHub MCP indisponivel e `gh` ausente ou nao autenticado.
- Usuario nao aprova titulo, corpo, push ou criacao.

## Resume Contract

Registrar base, head, remote, upstream, commits incluidos, diff stat, titulo,
corpo, decisoes humanas, ferramenta usada, URL do PR, validadores e pendencias.
