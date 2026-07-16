---
name: loki-self-healing
description: Run the Loki `loki-self-healing` command bundle. Audit and automatically correct scoped internal Loki package artifacts in the working tree, validate the whole artifact or command bundle, and never stage or commit changes.
when_to_use:
  - "Use when a Loki package file, directory, workflow, or staged-file set must be audited and corrected."
  - "Use when command bundles require a complete 24/24 self-healing audit across SKILL, references and response asset."
argument-hint: "[scope_input, optional out_of_scope]"
arguments:
  required: [scope_input]
  optional: [out_of_scope]
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - broad package scope
  - staged-file input with working tree divergence
  - corrections affecting package artifacts or manifest
  - conflicting package rules or incomplete operational inventory
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-self-healing/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: package-maintenance
required_skills: [lf-framework-impact-audit, lf-command-creator, lf-skill-creator, lf-agent-creator]
required_commands: []
status: draft
used_by: [loki-self-healing]
---

# loki-self-healing

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: scope_input
    input_type: path[file_or_directory] | workflow_name | staged
    requirement: required
    description: Arquivo, diretório, workflow Loki ou conjunto staged a auditar.
  - key: out_of_scope
    input_type: list[path_or_domain]
    requirement: optional
    default: []
    description: Limites negativos adicionais definidos pelo usuário.
```

Valide que o escopo resolve dentro do package root; para `staged`, valide que o
índice contém candidatos mas nunca o altere. Valide tipos, paths e conflito com
`out_of_scope`. Solicite todo obrigatório ausente e não invente escopo, regra,
install scope, approval ou correção. Normalize objetivo, escopo, candidatos,
limites, gates, fontes e lacunas. Durante Input não analise artefatos, corrija,
execute validator, faça stage/commit nem declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) e as
referências de auditoria que ele selecionar antes de agir.

## Response

Leia integralmente [references/response.md](references/response.md) e preencha
[assets/response-template.md](assets/response-template.md) na resposta terminal.
