---
name: loki-deep-research
description: Run the Loki `loki-deep-research` command workflow in Codex. Use when the user asks for deep research on the internet, web research with citations, multi-source investigation, source credibility analysis, contradiction mapping, or a sourced research report before analysis, planning, or decision-making.
when_to_use:
  - "Use when running loki-deep-research for internet/web deep research."
  - "Use when the output needs cited sources, query methodology, credibility checks, contradictions, assumptions, gaps, and next-step handoff."
argument-hint: "[research question, scope, depth, source constraints, destination]"
arguments:
  required:
    - research_question
  optional:
    - scope
    - out_of_scope
    - depth
    - deadline
    - source_policy
    - destination
    - constraints
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
  - broad or ambiguous research scope
  - conflicting or weak external sources
  - high-stakes legal, medical, financial, security or compliance claims
  - expensive multi-lane or long-running web research
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-deep-research/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: research
required_skills:
  - lf-web-deep-research
required_commands: []
status: draft
used_by:
  - loki-deep-research
---

# loki-deep-research

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: research_question
    input_type: string
    requirement: required
    description: Pergunta, tese, decisao ou tema verificavel da pesquisa.
  - key: scope
    input_type: string_or_mapping
    requirement: optional
    default: null
    description: Limites positivos da pesquisa.
  - key: out_of_scope
    input_type: list[string]
    requirement: optional
    default: []
    description: Temas ou superficies excluidos.
  - key: depth
    input_type: enum[quick,standard,deep,deeper]
    requirement: optional
    default: null
    description: Profundidade esperada, a confirmar quando o custo material variar.
  - key: deadline
    input_type: string
    requirement: optional
    default: null
    description: Prazo ou limite temporal relevante.
  - key: source_policy
    input_type: mapping
    requirement: optional
    default: {}
    description: Tipos de fonte preferidos/proibidos e criterios de credibilidade.
  - key: destination
    input_type: path
    requirement: optional
    default: null
    description: Arquivo Markdown aprovado para o relatorio, quando houver escrita.
  - key: constraints
    input_type: mapping
    requirement: optional
    default: {}
    description: Restricoes de idioma, periodo, geografia, dominio, seguranca ou compliance.
```

Valide `research_question` nao vazia, enum de profundidade, tipos, combinacoes e
path de destino permitido. Solicite toda informacao obrigatoria ausente e
esclareca pergunta, escopo, custo ou destino ambiguos sem inventar approval.
Normalize objetivo, parametros, escopo, restricoes, destino, approvals, gates e
lacunas.

Durante Input nao pesquise, navegue, escreva relatorio, invoque agentes ou
declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
