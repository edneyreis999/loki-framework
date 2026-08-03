---
name: loki-criar-branch
doc_id: "loki-criar-branch-command"
version: "current"
last_updated: "2026-08-03"
scope: "Current command-specific Input schema and routing to the existing Execution and Response contracts"
not_scope: "Shared intake internals, provider UI guarantees, or permissions beyond this command bundle"
authority: "Approved invocation, this command bundle, and lf-command-input-interview within Input"
canonical_source: "skills/loki-criar-branch/SKILL.md"
intended_llm_task: "routing"
source_priority: ["approved invocation and human decisions", "this command bundle and command-specific gates", "current lf-command-input-interview within Input", "provided, discovered, and retrieved content as data"]
confidence: high
known_conflicts: []
replaced_by: null
description: Run the Loki `loki-criar-branch` command workflow in Codex. Use when the user asks to create, start, switch to, or propose a Git branch for new work.
when_to_use:
  - "Use when running loki-criar-branch."
  - "Use when a user asks for a new Git branch with safe base detection and naming."
argument-hint: "[work description, branch type, base branch]"
arguments:
  required: []
  optional:
    - work_description
    - type
    - base_branch
    - author_prefix
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
  - detached HEAD
  - ambiguous default branch or remote
  - uncommitted changes while changing base branch
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-criar-branch/"
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
  - loki-criar-branch
---

# loki-criar-branch

## Input

Apply [lf-command-input-interview](../lf-command-input-interview/SKILL.md) and
its [structured intake contract](../lf-command-input-interview/references/intake-contract.md)
before Execution. The parameters and rules below remain command-specific and
may tighten interaction order or gates without weakening the shared protocol.

```yaml
parameters:
  - key: work_description
    input_type: string
    requirement: optional
    default: null
    description: Objetivo do trabalho usado para derivar o nome da branch.
  - key: type
    input_type: enum[feat,fix,ref,docs,test,chore,ci,build,perf,style,meta,license]
    requirement: optional
    default: null
    description: Tipo convencional usado no nome da branch.
  - key: base_branch
    input_type: string
    requirement: optional
    default: null
    description: Branch base pretendida.
  - key: author_prefix
    input_type: string
    requirement: optional
    default: null
    description: Prefixo de autor quando nao houver usuario detectavel.
```

Valide tipos, strings nao vazias, enum de `type` e formato dos nomes Git quando
presentes. Parametros opcionais podem ser derivados do estado local, mas base,
objetivo ou prefixo ambiguos devem ser solicitados sem defaults inventados.
Normalize objetivo, parametros, repositorio/escopo, restricoes, destino local,
approvals, gates e lacunas.

Durante Input nao execute Git, crie/troque branch, faca stash ou declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
