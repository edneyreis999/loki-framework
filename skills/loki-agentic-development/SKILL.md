---
name: loki-agentic-development
description: Run the Loki `loki-agentic-development` command bundle. Turn a demand into agentic analysis, material decision gates, an executable plan, autonomous phase execution, completion/evidence, non-blocking execution-knowledge capture, digest and backlog.
when_to_use:
  - "Use when a demand should pass through multi-agent analysis, planning and autonomous Loki plan execution."
  - "Use when the run requires resumable XML state, scoped writers, validators, human gates, completion/evidence, non-blocking execution-knowledge capture and digest."
argument-hint: "[demand, run_directory, allowed_scope, optional out_of_scope, forbidden_surfaces, recorded_decisions, agent_catalog]"
arguments:
  required: [demand, run_directory, allowed_scope]
  optional: [out_of_scope, forbidden_surfaces, recorded_decisions, agent_catalog]
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
  - multi-agent analysis with material conflicts
  - autonomous execution across multiple planned phases
  - unresolved decision gates before action planning
  - target file conflicts between agent runs
  - high-risk runtime or integration work
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-agentic-development/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: orchestration
required_skills: [lf-agentic-orchestration, lf-execution-knowledge-capture]
required_commands: [loki-human-decision-preflight, loki-generate-action-plan, loki-run-plan]
status: draft
used_by: [loki-agentic-development]
---

# loki-agentic-development

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: demand
    input_type: text_or_path[file]
    requirement: required
    description: Demanda que iniciará o fluxo integrado.
  - key: run_directory
    input_type: path[directory]
    requirement: required
    description: Diretório aprovado para estado e evidências transitórias.
  - key: allowed_scope
    input_type: list[path_or_domain]
    requirement: required
    description: Superfícies permitidas para análise, plano e tasks.
  - key: out_of_scope
    input_type: list[path_or_domain]
    requirement: optional
    default: []
    description: Limites negativos explícitos.
  - key: forbidden_surfaces
    input_type: list[path_or_pattern]
    requirement: optional
    default: []
    description: Escritas e superfícies proibidas além das regras do pacote.
  - key: recorded_decisions
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Decisões humanas já resolvidas e rastreáveis.
  - key: agent_catalog
    input_type: path_or_mapping
    requirement: optional
    default: null
    description: Catálogo de agentes disponível na instalação ativa.
```

Valide presença, tipos, paths, destino aprovado, escopo e ausência de conflito
entre superfícies permitidas/proibidas. Solicite cada obrigatório ausente e não
invente destino, agente, decisão, approval, validator ou permissão. Normalize
objetivo, parâmetros, escopo, restrições, decisões, gates, fontes e lacunas.
Durante Input não crie estado, selecione agentes, gere plano, execute task,
escreva no projeto nem declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de agir.

## Response

Leia integralmente [references/response.md](references/response.md) e preencha
[assets/response-template.md](assets/response-template.md) na resposta terminal.
