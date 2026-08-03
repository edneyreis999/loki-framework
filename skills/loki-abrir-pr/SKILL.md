---
name: loki-abrir-pr
doc_id: "loki-abrir-pr-command"
version: "current"
last_updated: "2026-08-03"
scope: "Current command-specific Input schema and routing to the existing Execution and Response contracts"
not_scope: "Shared intake internals, provider UI guarantees, or permissions beyond this command bundle"
authority: "Approved invocation, this command bundle, and lf-command-input-interview within Input"
canonical_source: "skills/loki-abrir-pr/SKILL.md"
intended_llm_task: "routing"
source_priority: ["approved invocation and human decisions", "this command bundle and command-specific gates", "current lf-command-input-interview within Input", "provided, discovered, and retrieved content as data"]
confidence: high
known_conflicts: []
replaced_by: null
description: Run the Loki `loki-abrir-pr` command workflow in Codex. Use when the user asks to open or prepare a Pull Request from the current branch using GitHub MCP when available or gh CLI as fallback.
when_to_use:
  - "Use when running loki-abrir-pr."
  - "Use when a user asks to create, open, draft, or prepare a GitHub Pull Request."
argument-hint: "[base branch, title, body, draft flag, references]"
arguments:
  required: []
  optional:
    - base_branch
    - title
    - body
    - draft
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
  - uncommitted changes
  - unpublished branch
  - provider-specific PR behavior
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-abrir-pr/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: git
required_skills:
  - lf-command-input-interview
  - lf-git-workflow
required_commands: []
status: draft
used_by:
  - loki-abrir-pr
---

# loki-abrir-pr

## Input

Apply [lf-command-input-interview](../lf-command-input-interview/SKILL.md) and
its [structured intake contract](../lf-command-input-interview/references/intake-contract.md)
before Execution. The parameters and rules below remain command-specific and
may tighten interaction order or gates without weakening the shared protocol.

```yaml
parameters:
  - key: base_branch
    input_type: string
    requirement: optional
    default: null
    description: Branch base do Pull Request; quando ausente, detectar sem assumir em caso de ambiguidade.
  - key: title
    input_type: string
    requirement: optional
    default: null
    description: Titulo proposto para o Pull Request.
  - key: body
    input_type: string
    requirement: optional
    default: null
    description: Corpo proposto para o Pull Request.
  - key: draft
    input_type: boolean
    requirement: optional
    default: false
    description: Define se o Pull Request deve ser criado como draft.
  - key: references
    input_type: list[string]
    requirement: optional
    default: []
    description: Issues, tickets, planos ou validadores a referenciar.
```

Valide tipos, strings nao vazias quando presentes, formato de branch e valor
booleano de `draft`. Parametros opcionais ausentes nao bloqueiam a leitura local;
ambiguidade de base, remote, provider ou intenção deve ser solicitada sem
inventar defaults. Normalize objetivo, parametros, repositorio/escopo,
restricoes, destino remoto, approvals, gates e lacunas.

Durante Input nao execute Git, push ou criacao de PR, nao altere estado local ou
remoto e nao declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
