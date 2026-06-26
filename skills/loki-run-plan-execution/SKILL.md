---
name: loki-run-plan-execution
description: Execute approved Loki action-plan phases from `tasks.md` and `task-N.M.md` files. Use for `loki:run-plan` preflight, phase/task onboarding, execution briefs, dependency checks, read-only context extraction routing, serialized writes, validators, human gates, build evidence, and resumable task state.
when_to_use:
  - "Use for loki:run-plan preflight and phase execution from approved tasks.md and task-N.M.md files."
  - "Use when checking dependencies, execution briefs, read-only context routing, serialized writes, validators, gates, build evidence, and resumable state."
argument-hint: "[phase, tasks.md, task target, analysis directory]"
arguments:
  required: []
  optional:
    - phase
    - tasks_md
    - task_target
    - analysis_directory
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
  - dependency or resume-state ambiguity
  - broad cross-artifact writes
  - sensitive write, runtime behavior, or human gate complexity
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-run-plan-execution/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:run-plan
---

# loki-run-plan-execution

## Purpose

Preparar e executar uma fase aprovada do plano Loki sem depender de memoria da
conversa. A skill transforma `tasks.md`, `task-N.M.md`, analises existentes,
decisoes humanas e validators em uma execucao rastreavel.

## Procedure

1. Confirmar entradas: `FASE_ATUAL`, `TASKS_MD`, `TASK_TARGET` opcional,
   `DIR_ANALISE` opcional, escopo permitido e forbidden writes.
2. Resolver paths relativos ou absolutos antes de ler. Parar se um path
   obrigatorio estiver ausente, ambiguo ou fora do plano ativo.
3. Ler `TASKS_MD` e localizar todos os arquivos `task-N.M.md` da fase alvo.
4. Conferir dependencias, status, referencias, validators, observable
   validation, human loop, Definition of Done e resume notes de cada task.
5. Montar um `Execution Brief` antes da primeira escrita:
   - objetivo da fase;
   - tasks em ordem topologica;
   - dependencias pendentes;
   - referencias e fontes lidas;
   - arquivos e superficies provaveis;
   - skills tecnicas sugeridas e origem da sugestao;
   - validators e human gates;
   - riscos, blockers e proximo passo.
6. Quando `DIR_ANALISE` existir, pedir ao orquestrador para acionar uma ou mais
   instancias de `execution-context-reader` em modo read-only e extrair somente
   fatos relevantes para `FASE_ATUAL`, paralelizando por fonte ou lote pequeno
   quando houver multiplos arquivos independentes.
7. Quando `DIR_ANALISE` nao existir e as referencias da task forem
   insuficientes, pedir pre-analise local minima via `execution-context-reader`
   antes de implementar, paralelizando apenas quando houver fontes
   independentes.
8. Resolver lacunas criticas antes de escrever. Nao iniciar implementacao se
   faltar decisao humana, referencia executavel, approval, validator ou skill
   tecnica exigida.
9. Carregar `<technology_required_skills>` apenas quando o usuario, a task, o
   contexto detectado ou retrospectiva aprovada indicar uma tecnologia.
10. Executar tasks uma por vez na ordem topologica. Leitura pode ser paralela;
    escrita e serializada por um unico orquestrador.
11. Antes de cada escrita, verificar que o arquivo, superficie, `<domain_ids>`,
    integration point e gate estao cobertos pela task ativa.
12. Rodar validators declarados. Registrar comando/checklist, resultado,
    evidencia e justificativa quando um validator nao se aplicar.
13. Nao declarar comportamento perceptivel, runtime, integracao, estado
    persistido ou artefato gerado como validado sem `<human_validation_gate>`.
14. Atualizar `task-N.M.md`, `tasks.md`, `builds/faseN/` e `interaction/faseN/`
    apenas conforme permitido pelo plano ativo.
15. Ao concluir a fase, recomendar `loki:retrospectiva-tecnica` com resumo de
    arquivos afetados, validators, gates humanos e riscos residuais.

## Inputs

- `FASE_ATUAL`.
- `TASKS_MD`.
- `TASK_TARGET` opcional.
- `DIR_ANALISE` opcional.
- `task-N.M.md` da fase alvo.
- Decisoes humanas em `interaction/`.
- Escopo permitido, out of scope e forbidden writes.

## Outputs

- `Execution Brief`.
- Lista de tasks executadas, bloqueadas ou puladas com motivo.
- Evidencias de validators e build reports.
- Atualizacao de status em `tasks.md` e `task-N.M.md`.
- `LokiRunState` retomavel.
- Recomendacao de retrospectiva ao fim da fase.

## Limits

- Nao execute plano inteiro quando o usuario especificar apenas fase ou task.
- Nao escreva fora do escopo da task ativa.
- Nao pule dependencias pendentes.
- Nao use analise externa ou memoria da conversa como substituto de referencias
  em disco.
- Nao carregue skill tecnica por default.
- Nao marque human validation como aprovada sem resposta humana explicita.
- Nao permita que handoffs escrevam no projeto consumidor; handoffs `read-only`
  ou `proposal-only` podem rodar em paralelo quando as entradas forem
  independentes e retornam contexto, checklist ou proposta para consolidacao
  pelo orquestrador.

## Required Gates

- `interview` quando fase, task alvo, path ou requisito estiver ambiguo.
- `approval` para politica, instalacao, promocao, escrita sensivel ou mudanca
  fora do escopo aprovado.
- `human-validation` para comportamento perceptivel, runtime, integracoes,
  estado persistido ou artefatos gerados.
- `technical-review` para mudanca em command, skill, agent, template ou
  validator.

## Validators

- `TASKS_MD` existe e referencia a fase alvo.
- Todos os `task-N.M.md` da fase alvo foram localizados ou a lacuna foi
  registrada como blocker.
- Dependencias e ordem topologica foram conferidas antes da execucao.
- Cada task executada tem referencia, validator, human loop e out of scope.
- `Execution Brief` foi produzido antes da primeira escrita.
- Toda escrita ficou dentro do escopo da task ativa.
- Validators foram executados ou justificados.
- Human gates pendentes nao foram marcados como aprovados.
- `LokiRunState` permite retomada sem memoria da conversa.
