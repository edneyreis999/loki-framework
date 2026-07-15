---
name: loki-catalogar-docs
description: Run the Loki `loki-catalogar-docs` command workflow in Codex. Use when cataloging durable consumer documentation under `/docs`, validating directory paths, applying recursion limits, coordinating safe bottom-up fan-out, invoking `catalogador` with explicit scoped-write envelopes, and producing a summarized catalog update.
when_to_use:
  - "Use when running loki-catalogar-docs to catalog durable consumer documentation under /docs."
  - "Use when a user asks to catalog docs, refresh docs/index.xml, validate documentation directory scope, or run bottom-up cataloging with catalogador."
  - "Use when safe fan-out, recursion limits, target_files ownership, approval gates, validators, and resumable catalog state are required."
argument-hint: "[DOCS_DIR, RECURSIVE, approval context]"
arguments:
  required:
    - DOCS_DIR
  optional:
    - RECURSIVE
    - LARGE_TREE_CONFIRMATION
    - OUT_OF_DOCS_APPROVAL
    - recorded_decisions
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
  - ambiguous documentation target or ownership
  - recursive tree near command limits
  - conflicting target_files or shared index writes
  - durable consumer documentation changes without recorded approval
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-catalogar-docs/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: documentation
required_skills: []
required_commands: []
status: draft
used_by:
  - loki-catalogar-docs
---

# loki-catalogar-docs

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: DOCS_DIR
    input_type: path
    requirement: required
    description: Diretorio de documentacao duradoura do consumidor a catalogar, preferencialmente relativo ao workspace.
  - key: RECURSIVE
    input_type: boolean
    requirement: optional
    default: true
    description: Quando true, descobre a arvore ate os limites do command; quando false, processa apenas DOCS_DIR.
  - key: LARGE_TREE_CONFIRMATION
    input_type: approval_record
    requirement: optional
    default: null
    description: Confirmacao humana exigida se a descoberta encontrar mais de 20 e no maximo 100 diretorios.
  - key: OUT_OF_DOCS_APPROVAL
    input_type: approval_record
    requirement: optional
    default: null
    description: Approval explicito exigido para um alvo documental fora de /docs.
  - key: recorded_decisions
    input_type: list[mapping]
    requirement: optional
    default: []
    description: Decisoes humanas ja registradas por um plano ou workflow retomavel, com fonte e escopo.
```

Valide que `DOCS_DIR` foi informado, possui formato de path, existe, e um
diretorio, resolve dentro do workspace real e nao atravessa symlink ou traversal
para fora dele. Valide `RECURSIVE` como boolean, os approvals como registros
com decisao, fonte e escopo, e `recorded_decisions` como lista. Nao trate um
approval generico como autorizacao para alvo fora de `/docs` ou para escrita.

Identifique cada informacao obrigatoria ausente ou invalida, explique como
corrigi-la e solicite-a ao usuario antes de avancar. Nao invente paths,
decisoes, approvals, escopo ou defaults alem dos declarados acima.

Normalize a entrada em um registro com objetivo, parametros validados,
workspace e `DOCS_DIR` resolvidos, escopo, restricoes, exclusoes previstas,
destinos de saida, approvals, gates e lacunas. Durante Input nao descubra a
arvore, catalogue documentos, invoque agentes, altere arquivos, execute a
tarefa principal nem declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
