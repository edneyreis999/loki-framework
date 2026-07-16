---
name: loki-tech-analysis
description: Run the Loki `loki-tech-analysis` command workflow in Codex. Use when producing evidence-based technical analyses from briefs, feedback, specs, source paths, runtime questions, source maps, decision matrices, validators, gates, and handoff to decision preflight or action planning.
when_to_use:
  - "Use when running loki-tech-analysis to produce evidence-based technical analysis."
  - "Use when the output needs source maps, fact/hypothesis separation, decision matrices, validators, gates, and handoff to decision preflight or action planning."
argument-hint: "[analysis input, source paths, scope, destination]"
arguments:
  required:
    - analysis_input
  optional:
    - source_paths
    - allowed_scope
    - out_of_scope
    - forbidden_surfaces
    - recorded_decisions
    - destination
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
  - architecture or security risk
  - conflicting multi-source evidence
  - irreversible or high-impact recommendation
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-tech-analysis/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
status: draft
domain: spec-driven
required_skills:
  - lf-tech-analysis-authoring
required_commands: []
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - architecture or security risk
    - conflicting multi-source evidence
    - irreversible or high-impact recommendation
  handoff_effort:
    research: high
    coding: medium
    documentation_transient: high
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
used_by:
  - loki-tech-analysis
---

# loki-tech-analysis

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: analysis_input
    input_type: string | path
    requirement: required
    description: Brief, PRD, NSD, feedback, especificação, pergunta de runtime ou pedido direto que define o objeto da análise.
  - key: source_paths
    input_type: list[path]
    requirement: optional
    default: []
    description: Fontes locais indicadas pelo usuário; quando vazias, registrar a necessidade e os limites da descoberta controlada.
  - key: allowed_scope
    input_type: list[path | surface | objective]
    requirement: optional
    default: []
    description: Superfícies e objetivos nos quais a análise pode atuar.
  - key: out_of_scope
    input_type: list[path | surface | objective]
    requirement: optional
    default: []
    description: Superfícies e objetivos explicitamente excluídos.
  - key: forbidden_surfaces
    input_type: list[path | pattern]
    requirement: optional
    default: []
    description: Superfícies que não podem ser escritas nem tratadas como autorizadas.
  - key: recorded_decisions
    input_type: list[decision | path]
    requirement: optional
    default: []
    description: Decisões humanas, assumptions, standards ou tasks já registradas e relevantes.
  - key: destination
    input_type: path
    requirement: optional
    default: null
    description: Arquivo Markdown de análise dentro do plano ativo; se ausente, confirmar antes de escrever.
```

Valide presença e conteúdo não vazio de `analysis_input`. Valide que listas usam
os tipos declarados, que caminhos fornecidos são legíveis quando forem fontes e
que `destination` é um arquivo Markdown dentro do plano ativo. Rejeite colisões
entre `allowed_scope`, `out_of_scope` e `forbidden_surfaces`, e não trate silêncio
como aprovação. Solicite toda informação obrigatória ausente ou ambígua que
impeça análise segura; não invente caminho, escopo, decisão, approval ou destino.

Normalize a entrada em um registro com objetivo, parâmetros validados, escopo,
restrições, fontes, destino, approvals, gates e lacunas abertas. Não execute a
análise, não altere arquivos e não declare sucesso durante `Input`.

## Execution

Leia [references/execution.md](references/execution.md) integralmente antes de
agir e cumpra todo o contrato de execução, inclusive delegação, evidência,
validators, gates, condições de parada e retomada.

## Evidence Policy

Subagentes devolvem completion record; o orquestrador captura evidence sanitizada
ou declara `partial`, `unavailable` ou `unsupported`. Nunca solicite CoT privado
nem use retrospectiva como fallback automático.

## Response

Leia [references/response.md](references/response.md) integralmente antes de
responder. Na resposta terminal, preencha
[assets/response-template.md](assets/response-template.md) conforme o consumidor
e o estado real do workflow.
