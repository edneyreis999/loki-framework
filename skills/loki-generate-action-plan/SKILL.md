---
name: loki-generate-action-plan
description: Run the Loki `loki-generate-action-plan` command workflow in Codex. Use when creating phased executable action plans with approved inputs, tasks.md, focused task files, phase folders, dependencies, scoped write owners, validators, human loops, stop conditions, and resumable state.
when_to_use:
  - "Use when approved analysis, feedback, brief, or objectives must become a phased executable Loki plan."
  - "Use when creating tasks.md, task-N.M.md, phase folders, a dependency DAG, scoped writers, validators, human loops, and resume state."
argument-hint: "[approved input, allowed scope, preflight record, candidate plan directory]"
arguments:
  required:
    - approved_input
    - allowed_scope
  optional:
    - preflight_record
    - out_of_scope
    - forbidden_surfaces
    - recorded_decisions
    - candidate_plan_directory
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
  - large multi-phase plan
  - complex dependency graph
  - sensitive writes or human gates are hard to model
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-generate-action-plan/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: planning
required_skills:
  - lf-action-plan-authoring
required_commands: []
status: draft
used_by:
  - loki-generate-action-plan
---

# loki-generate-action-plan

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: approved_input
    input_type: path_or_string_or_mapping
    requirement: required
    description: Analise, brief, feedback ou objetivo aprovado que fundamenta o plano.
  - key: allowed_scope
    input_type: string_or_mapping
    requirement: required
    description: Escopo positivo verificavel que o plano pode cobrir.
  - key: preflight_record
    input_type: path_or_mapping
    requirement: optional
    default: null
    description: Registro de loki-human-decision-preflight, quando existente.
  - key: out_of_scope
    input_type: list[string]
    requirement: optional
    default: []
    description: Objetivos e superficies excluidos do plano.
  - key: forbidden_surfaces
    input_type: list[path_or_pattern]
    requirement: optional
    default: []
    description: Superficies proibidas para a execucao futura.
  - key: recorded_decisions
    input_type: list[string_or_mapping]
    requirement: optional
    default: []
    description: Decisoes humanas ja aprovadas e suas evidencias.
  - key: candidate_plan_directory
    input_type: path
    requirement: optional
    default: null
    description: Diretorio candidato, ainda sujeito a approval separado antes da criacao.
```

Valide presenca, tipo e conteudo de `approved_input` e `allowed_scope`; valide a
existencia de paths de leitura, tipos das listas, conflitos de escopo e formato
do diretorio candidato. Se houver preflight, valide que nao restou
`must_ask_now` e que `ready_for_next_phase` e `true`. Rejeite entrada invalida
com correcao acionavel e nao interprete diretorio candidato como approval.

Solicite uma informacao obrigatoria ausente por turno e pare diante de lacuna
critica. Nao invente escopo, referencias, decisoes, approvals, validators ou
destino. Normalize objetivo, parametros, escopo, restricoes, destino candidato,
decisoes, approvals, gates e lacunas para Execution.

Durante Input nao planeje tasks, crie diretorios, escreva arquivos, invoque
agentes, execute o objetivo aprovado nem declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Evidence Policy

Subagentes devolvem completion record; o orquestrador captura evidence sanitizada
ou declara `partial`, `unavailable` ou `unsupported`. Nunca solicite CoT privado
nem use retrospectiva como fallback automático.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
