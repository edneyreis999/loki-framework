---
name: loki-retrospectiva-tecnica
description: Run the Loki `loki-retrospectiva-tecnica` command workflow in Codex after a phase is completed or clearly paused, or a real difficulty is resolved, to capture auditable artifacts, validation, decisions, execution friction, inferences, scripts, environment mismatches, reusable learnings, and residual risks without directly promoting durable rules.
when_to_use:
  - "Use after a Loki phase is completed or clearly paused."
  - "Use after a real task difficulty is resolved and reusable evidence should be captured."
  - "Use when execution consumed avoidable tokens, tools, searches, scripts, validations, or user corrections."
argument-hint: "[completed or paused scope, tasks, builds, interactions, operational trace, target retrospective]"
arguments:
  required:
    - completed_or_paused_scope
  optional:
    - tasks
    - builds
    - interaction_records
    - operational_trace
    - residual_risks
    - target_retrospective
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - reusable learning may become durable policy
  - evidence is incomplete or conflicting
  - retrospective recommends package artifact changes
  - repeated failed searches, bad inferences, unexpected output, or environment mismatch
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-retrospectiva-tecnica/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: continuous-improvement
required_skills: []
required_commands: []
status: draft
used_by:
  - loki-retrospectiva-tecnica
  - loki-continuous-improvement
---

# loki-retrospectiva-tecnica

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: completed_or_paused_scope
    input_type: path_or_string_or_mapping
    requirement: required
    description: Fase concluida ou claramente pausada, ou dificuldade real ja resolvida, com criterio e resultado observavel.
  - key: tasks
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Tasks e estados que definem objetivo, escopo e conclusao.
  - key: builds
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Evidencias de build, implementacao ou artefatos produzidos.
  - key: interaction_records
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Decisoes humanas, gates, correcoes e interacoes materiais.
  - key: operational_trace
    input_type: list[path_or_string_or_mapping]
    requirement: optional
    default: []
    description: Ferramentas, comandos, scripts, buscas, tentativas, resultados e correcoes de rota observaveis.
  - key: residual_risks
    input_type: list[string_or_mapping]
    requirement: optional
    default: []
    description: Riscos, lacunas e pendencias ainda existentes.
  - key: target_retrospective
    input_type: path
    requirement: optional
    default: null
    description: Destino exato autorizado pelo workflow chamador.
```

Valide presenca, tipo e evidencia de conclusao/pausa/resolucao em
`completed_or_paused_scope`; valide listas, existencia de paths e, quando
fornecido, o path exato de `target_retrospective` dentro do plano autorizado.
Pare se a dificuldade ainda estiver em teste, a fase nao tiver resultado claro
ou evidencias essenciais forem contraditorias. Rejeite entrada invalida com
correcao acionavel.

Solicite uma informacao obrigatoria ausente por turno. Nao invente erros,
causas, metricas, validacoes, outputs, atritos, approvals ou destino. Normalize
objetivo, resultado, parametros, escopo, restricoes, destino, evidencias,
decisoes, approvals, gates e lacunas para Execution.

Durante Input nao redija a retrospectiva, promova aprendizados, altere arquivos,
execute validadores ou declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
