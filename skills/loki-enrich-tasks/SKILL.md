---
name: loki-enrich-tasks
description: Run the Loki `loki-enrich-tasks` command bundle in Codex. Enrich only the active phase tasks from retrospectives, builds, human decisions, and scoped-write evidence before execution; preserve phase scope, source confidentiality, research gates, validators, owners, and human loops without promoting durable policy.
when_to_use:
  - "Use before loki-run-plan when the active phase tasks need targeted enrichment from prior retrospectives, builds, decisions, scoped-write ownership, target files, validators, success criteria, or human loops."
  - "Use when improving active plan tasks without exposing transient sources or promoting durable context directly."
argument-hint: "[FASE_ATUAL, TASKS_MD, DIR_RETROSPECTIVAS, DIR_BUILDS, optional INTERACTIONS_RELEVANTES and enrichment_scope]"
arguments:
  required:
    - FASE_ATUAL
    - TASKS_MD
    - DIR_RETROSPECTIVAS
    - DIR_BUILDS
  optional:
    - INTERACTIONS_RELEVANTES
    - enrichment_scope
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
  - conflicting retrospective or build evidence
  - enrichment changes execution order, scope, or gates
  - durable package policy may be affected
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-enrich-tasks/"
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
  - loki-enrich-tasks
---

# loki-enrich-tasks

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: FASE_ATUAL
    input_type: string_or_integer
    requirement: required
    description: Numero ou identificador que resolve uma unica fase ativa do plano.
  - key: TASKS_MD
    input_type: path[file]
    requirement: required
    description: Caminho existente e legivel para o tasks.md do plano ativo.
  - key: DIR_RETROSPECTIVAS
    input_type: path[file_or_directory]
    requirement: required
    description: Arquivo ou diretorio existente e legivel com retrospectivas relevantes.
  - key: DIR_BUILDS
    input_type: path[file_or_directory]
    requirement: required
    description: Arquivo ou diretorio existente e legivel com builds, validacoes ou evidencias relevantes.
  - key: INTERACTIONS_RELEVANTES
    input_type: list[path_or_string]
    requirement: optional
    default: []
    description: Decisoes humanas, approvals, defaults ou rejeicoes aplicaveis a fase.
  - key: enrichment_scope
    input_type: string_or_mapping
    requirement: optional
    default: current_phase
    description: Recorte solicitado dentro da fase atual; nunca autoriza outra fase.
```

Valide presença, tipo e formato de todos os parâmetros. Resolva paths no
filesystem sem escrever: `TASKS_MD` deve ser arquivo regular legível;
`DIR_RETROSPECTIVAS` e `DIR_BUILDS` devem ser arquivo ou diretório legível; e
cada path em `INTERACTIONS_RELEVANTES` deve existir. Confirme que `FASE_ATUAL`
resolve exatamente uma fase declarada em `TASKS_MD` e que `enrichment_scope`
não amplia essa fase. Rejeite entrada inválida com explicação acionável e não
normalize silenciosamente algo que altere a intenção.

Identifique cada parâmetro obrigatório ausente e solicite-o ao usuário. Não
invente path, escopo, approval, decisão ou default. Não avance enquanto uma
ausência ou ambiguidade impedir execução segura.

Normalize a entrada em um registro com objetivo, parâmetros validados, fase e
tasks alvo, escopo, restrições, destinos de saída, `allowed_writes`,
`forbidden_writes`, approvals, gates e lacunas. A fase Execution deve consumir
esse registro, não o pedido bruto. Durante Input não analise fontes para
enriquecimento, não pesquise, não altere arquivos, não execute a tarefa
principal e não declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referências adicionais que esse arquivo ordenar.

## Evidence Policy

Subagentes devolvem completion record; o orquestrador captura evidence sanitizada
ou declara `partial`, `unavailable` ou `unsupported`. Nunca solicite CoT privado
nem use retrospectiva como fallback automático.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
