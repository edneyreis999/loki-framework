---
name: loki-demand-text-improver
description: Run the public Loki `loki-demand-text-improver` command bundle. Use when an initial demand and optional local sources should become a traceable enriched demand before any technical analysis, decision preflight, planning, or implementation.
when_to_use:
  - "Use when a rough demand should be clarified and enriched without executing it."
  - "Use before technical analysis or planning when objective, scope, requirements, constraints, acceptance criteria, validators, assumptions, risks, or references need to become explicit."
argument-hint: "[analysis_input, optional source_paths, destination directory]"
arguments:
  required:
    - analysis_input
    - destination
  optional:
    - source_paths
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
  - material ambiguity that changes intent or scope
  - conflicting local sources
  - unsafe destination or target collision
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-demand-text-improver/"
  execution: "references/execution.md"
  response: "references/response.md"
  enrichment_contract: "references/enrichment-contract.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
status: draft
domain: spec-driven
required_skills: []
required_commands: []
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - material ambiguity that changes intent or scope
    - conflicting local sources
    - unsafe destination or target collision
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
used_by:
  - loki-demand-text-improver
---

# loki-demand-text-improver

## Input

Peça os parâmetros de entrada para o workflow. O estado de sessão do adapter
não é parâmetro nem gate deste command; a segurança da execução depende da
validação explícita de inputs, destino, target, ownership, entrevistas e
validators abaixo.

```yaml
parameters:
  - key: analysis_input
    input_type: inline_text | path
    requirement: required
    description: Demanda inicial não vazia, fornecida explicitamente como texto inline ou caminho de arquivo local legível.
  - key: source_paths
    input_type: list[path]
    requirement: optional
    default: []
    description: Arquivos locais legíveis que complementam contexto; nunca influenciam o nome da saída.
  - key: destination
    input_type: directory_path
    requirement: required
    description: Diretório explicitamente autorizado, existente, gravável e contido no envelope de escrita do adapter.
```

Solicite todo parâmetro obrigatório ausente. Normalize `analysis_input` de forma
inequívoca como `inline` ou `file`; um path explicitamente fornecido que não
exista não pode ser reinterpretado como texto inline. Valide conteúdo não vazio,
tipo, legibilidade de cada arquivo, lista de fontes, existência do destination,
tipo diretório, autorização e gravabilidade verificável.

Calcule um único target sem escrever:

- `file`: remova somente a última extensão do basename, preserve caixa e stem e
  use `<destination>/<stem>-improved.md`;
- `inline`: use `<destination>/improved-demand.md`.

Canonicalize destination e target. O parent canônico do target deve ser o
destination canônico e o target deve estar dentro do envelope gravável. Qualquer
entrada já ocupando o target, inclusive symlink, bloqueia. Não crie destination,
sobrescreva, apague, autonumere nem escolha nome alternativo. `source_paths`
nunca participa do nome.

Normalize objetivo, modo de entrada, fontes, target, allowed/forbidden writes,
gates e lacunas para Execution. Durante Input não enriqueça a demanda, não
escreva, não invoque writer e não declare sucesso.

## Execution

Leia [references/execution.md](references/execution.md) e
[references/enrichment-contract.md](references/enrichment-contract.md)
integralmente antes de agir. Cumpra o plano, os handoffs terminais, ownership,
validators, gates, stops e resume contract desses arquivos.

## Response

Leia [references/response.md](references/response.md) integralmente antes de
responder. Preencha [assets/response-template.md](assets/response-template.md)
com o estado real. O próximo workflow pode ser mencionado, mas nunca invocado
automaticamente.
