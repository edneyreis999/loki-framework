---
name: loki-commit
description: Run the Loki `loki-commit` command workflow in Codex. Use when the user asks to commit local changes with explicit staging, conventional message, branch safety, and validation.
when_to_use:
  - "Use when running loki-commit."
  - "Use when a user asks to commit, save changes in Git, or prepare a commit message for local changes."
argument-hint: "[files or scope, message, type, issue references]"
arguments:
  required: []
  optional:
    - paths
    - message
    - type
    - references
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: coding
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - mixed unrelated changes
  - suspected secrets or binaries
  - default branch commit request
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-commit/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: git
required_skills:
  - lf-git-workflow
required_commands: []
status: draft
used_by:
  - loki-commit
---

# loki-commit

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: paths
    input_type: list[path]
    requirement: optional
    default: []
    description: Paths candidatos ao staging explicito; vazio permite propor grupos a partir do diff.
  - key: message
    input_type: string
    requirement: optional
    default: null
    description: Mensagem de commit fornecida pelo usuario.
  - key: type
    input_type: enum[feat,fix,ref,docs,test,chore,ci,build,perf,style,meta,license]
    requirement: optional
    default: null
    description: Tipo convencional do commit.
  - key: references
    input_type: list[string]
    requirement: optional
    default: []
    description: Issues, tickets ou planos relacionados.
```

Valide tipos, existencia dos paths, enum de `type` e mensagem nao vazia quando
presente. Nao normalize silenciosamente paths, tipo ou mensagem de modo que
altere a intencao. Parametros opcionais ausentes podem ser derivados do diff e
propostos para approval; solicite qualquer informacao que impeça selecao segura.
Normalize objetivo, parametros, escopo de arquivos, restricoes, destino local,
approvals, gates e lacunas.

Durante Input nao execute Git, stage ou commit, nao altere indice/working tree e
nao declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
