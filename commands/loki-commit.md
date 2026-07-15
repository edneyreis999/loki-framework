---
name: loki:commit
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
    - mixed unrelated changes
    - secrets or generated binaries in diff
    - current branch is main, master or default branch
    - staged changes differ materially from unstaged changes
  handoff_effort:
    coding: medium
    validator: low
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:commit

## Purpose

Criar um commit Git pequeno, revisavel e intencional a partir do diff local,
com staging explicito, mensagem convencional e bloqueio contra commits
acidentais na branch default.

## Inputs

- Escopo opcional de arquivos ou paths.
- Mensagem opcional de commit.
- Tipo opcional: `feat`, `fix`, `ref`, `docs`, `test`, `chore`, `ci`, `build`,
  `perf`, `style`, `meta` ou `license`.
- Referencias opcionais de issue, ticket ou plano.

## Outputs

- Commit local criado.
- Mensagem final de commit.
- Lista de arquivos incluidos e arquivos deixados fora.
- Validadores executados ou motivo para nao executar.

## Allowed Writes

- Indice Git (`git add`) somente para pathspecs aprovados.
- Um commit local na branch atual aprovada.

## Forbidden Writes

- Commit direto em `main`, `master` ou default branch sem pedido explicito do
  usuario.
- Staging de arquivos nao revisados ou fora do escopo aprovado.
- `.claude/**`, `.agents/**` e `.codex/**` salvo pedido explicito e escopo
  aprovado.
- Push remoto, PR, merge, rebase destrutivo, reset ou checkout destrutivo.

## Required Skills

- `lf-git-workflow` para agrupamento de mudancas, staging seguro, mensagem,
  gates e validadores.

## Workflow

1. Carregar `lf-git-workflow`.
2. Ler branch atual, default branch, `git status --short`, diff staged e diff
   unstaged.
3. Se a branch atual for default (`main`, `master` ou default detectada), parar
   e recomendar `loki:criar-branch`, exceto quando o usuario pediu commit na
   default explicitamente.
4. Agrupar mudancas relacionadas e identificar arquivos suspeitos: secrets,
   binarios grandes, artefatos gerados ou paths fora do escopo.
5. Se houver grupos nao relacionados, propor commits separados e pedir escolha.
6. Montar pathspecs explicitos para os arquivos escolhidos; nao usar `git add .`
   como padrao.
7. Gerar mensagem convencional:
   `<type>(<scope>): <subject>`, com corpo explicando o que e por que quando
   necessario.
8. Mostrar arquivos, diff resumido e mensagem completa para approval.
9. Executar staging aprovado e criar commit local.
10. Reportar SHA curto, arquivos incluidos e estado remanescente.

## Validators

- `git status --short` antes e depois do commit.
- `git diff --cached --check` antes do commit quando houver diff textual.
- `git log -1 --oneline` confirma o commit criado.
- Arquivos deixados fora continuam fora do commit.

## Human Gates

- `approval` antes de stagear.
- `approval` antes de criar o commit.
- `approval` explicito para commit na default branch.

## Stop Conditions

- Repositorio Git ausente.
- Nenhuma mudanca selecionavel.
- Mudancas parecem incluir segredo, credencial ou binario grande nao aprovado.
- Branch default sem pedido explicito para commit direto.
- O usuario nao aprova arquivos ou mensagem.

## Resume Contract

Registrar branch, default branch detectada, grupos de mudanca, arquivos
incluidos/excluidos, mensagem aprovada, comandos executados, SHA criado,
validadores e estado final.
