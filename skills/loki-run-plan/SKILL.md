---
name: loki-run-plan
description: Run the Loki `loki-run-plan` command bundle in Codex. Use when executing an approved plan phase or task from tasks.md and task-N.M.md with an Execution Brief, dependency DAG, scoped writers, validators, non-ceremonial human gates, evidence, task-state updates, and resumable LokiRunState.
when_to_use:
  - "Use when executing an approved Loki plan phase or task from tasks.md and task-N.M.md."
  - "Use when phase execution requires an Execution Brief, dependency checks, scoped writers, validators, human gates, evidence, task-state updates, and resumable state."
argument-hint: "[TASKS_MD, EXECUTION_SCOPE=task|fase|plano, optional FASE_ATUAL, TASK_TARGET, DIR_ANALISE, task_files, interaction_records]"
arguments:
  required:
    - TASKS_MD
    - EXECUTION_SCOPE
  optional:
    - TASK_TARGET
    - DIR_ANALISE
    - task_files
    - interaction_records
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
  - long execution with complex resume state
  - broad cross-artifact writes
  - high-risk implementation or sensitive write
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-run-plan/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: execution
required_skills:
  - lf-run-plan-execution
required_commands: []
status: draft
used_by:
  - loki-run-plan
---

# loki-run-plan

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: EXECUTION_SCOPE
    input_type: enum
    requirement: required
    description: "Escopo terminal: task, fase ou plano."
    allowed_values: [task, fase, plano]
  - key: FASE_ATUAL
    input_type: string_or_integer
    requirement: conditional
    description: Fase alvo para task/fase; no plano, fase inicial ou primeira fase retomavel.
  - key: TASKS_MD
    input_type: path[file]
    requirement: required
    description: Caminho existente e legivel para o tasks.md aprovado do plano ativo.
  - key: TASK_TARGET
    input_type: string
    requirement: optional
    default: null
    description: Obrigatoria quando EXECUTION_SCOPE=task; quando ausente, execute o escopo selecionado conforme a DAG.
  - key: DIR_ANALISE
    input_type: path[file_or_directory]
    requirement: optional
    default: null
    description: Analise ou pre-analise aprovada a usar na extracao read-only de contexto.
  - key: task_files
    input_type: list[path[file]]
    requirement: optional
    default: []
    description: Arquivos task-N.M.md informados explicitamente; quando vazios, descubra-os por TASKS_MD e leitura direta do disco.
  - key: interaction_records
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Decisoes humanas, approvals e gates ja registrados para a fase ou task alvo.
```

Valide presença, tipo e formato dos parâmetros. `TASKS_MD` deve ser arquivo
regular legível. `EXECUTION_SCOPE=task` exige `FASE_ATUAL` e `TASK_TARGET`;
`fase` exige `FASE_ATUAL`; `plano` resolve todas as fases pela DAG e
usa `LokiRunState` persistido ou a primeira fase retomável.
Cada path em `task_files`, `DIR_ANALISE` e `interaction_records` deve existir e
ser legível quando informado. Confirme que cada task file pertence ao plano e ao
escopo selecionado, que `TASK_TARGET` resolve uma única task quando aplicável e que decisões ou
approvals registrados são aplicáveis ao mesmo escopo. Confira arquivos ignorados
ou untracked por leitura direta em disco; nunca use `git status` como única prova
de existência.

Rejeite entrada inválida com explicação acionável. Identifique e solicite toda
informação obrigatória ausente; não invente path, fase, task, escopo, decisão,
approval, validator ou gate. Não avance enquanto uma lacuna impedir execução
segura.

Normalize a entrada em registro com objetivo, parâmetros validados, escopo
terminal, fase inicial e tasks alvo, DAG conhecida, restrições, destinos, `allowed_writes`,
`forbidden_writes`, approvals, gates e lacunas. Durante Input não implemente,
altere arquivos, execute a tarefa principal, invoque escritores nem declare
sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referências adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
