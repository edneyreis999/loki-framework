---
name: lf-run-plan-execution
description: Execute approved Loki action-plan phases with preflight, execution briefs, serialized writes, validators, resumable state and non-blocking execution-knowledge capture from persisted completion/evidence.
when_to_use:
  - "Use for loki-run-plan preflight and phase execution from approved tasks.md and task-N.M.md files."
  - "Use when checking dependencies, execution briefs, read-only context routing, serialized writes, validators, gates, build evidence, execution-knowledge capture and resumable state."
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
hooks: {}
paths:
  package_skill: "skills/lf-run-plan-execution/SKILL.md"
shell: bash
type: skill
status: draft
used_by:
  - loki-run-plan
required_skills:
  - lf-domain-context-preflight
---

# lf-run-plan-execution

## Purpose

Preparar e executar uma task, fase ou plano aprovado do plano Loki sem depender de memoria da
conversa. A skill transforma `tasks.md`, `task-N.M.md`, analises existentes,
decisoes humanas e validators em uma execucao rastreavel.

## Procedure

1. Confirmar entradas: `TASKS_MD`, `EXECUTION_SCOPE` (`task`, `fase` ou
   `plano`), `FASE_ATUAL`/`TASK_TARGET` condicionais, `DIR_ANALISE`
   opcional, escopo permitido e forbidden writes.
2. Resolver paths relativos ou absolutos antes de ler. Parar se um path
   obrigatorio estiver ausente, ambiguo ou fora do plano ativo.
3. Ler `TASKS_MD` e localizar todos os arquivos `task-N.M.md` da fase alvo.
   Quando artefatos do plano estiverem ignorados, untracked ou ausentes do
   `git status`, validar estado por leitura direta em disco (`find`, `rg`,
   `sed`/equivalente) e nao usar status do VCS como unico sinal.
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
   faltar decisao humana nao coberta pelo plano aprovado, referencia
   executavel, approval, validator ou skill tecnica exigida.
9. Carregar `<technology_required_skills>` apenas quando o usuario, a task, o
   contexto detectado ou retrospectiva aprovada indicar uma tecnologia.
10. Antes de cada task write aplicavel, selecionar pela formula canonica
    `installed_in_consumer AND category == Write Agent AND task_write_mode
    includes task_scoped_writer AND durable_context_root declared AND domain
    agent`. O proprio agent executa `lf-domain-context-preflight`; Execution
    Brief, docs ou brief entregues pelo orquestrador nao substituem essa leitura
    seletiva pessoal.
11. Registrar durable root/README/docs read, freshness, current sources,
    conflitos, gaps/materialidade/substitutes, precedence, cross-domain/gap
    handoffs, result `ready|ready-with-gaps|blocked` e minimum next input.
    Fonte atual prevalece sobre doc stale. Root absent so segue
    `ready-with-gaps` sem gap material; bloqueie stale/unavailable/conflict/gap
    material sem substitute ou route. Use `bibliotecario` read-only para lookup
    cross-domain estreito; o Write Agent nunca autoedita consumer docs.
12. Se target resolver em consumer docs, owner exclusivo e `catalogador` com
    `calling_workflow: loki-run-plan` e `write_mode: task_scoped_writer`.
    Indisponibilidade bloqueia pre-write com estado retomavel, sem escrita do
    orquestrador, domain agent ou writer alternativo.
13. Executar tasks uma por vez na ordem topologica dentro do escopo terminal.
    Leitura pode ser paralela;
    escrita e serializada por owner e arquivo. O owner pode ser o orquestrador
    ou um agente `scoped-writer` quando a task aprovada declarar
    `target_files`, `allowed_writes`, validators e gates.
14. Antes de cada escrita, verificar que o arquivo, superficie, `<domain_ids>`,
    integration point, owner, `scoped_write_domains` e gate estao cobertos pela
    task ativa.
15. Rodar validators declarados. Registrar comando/checklist, resultado,
    evidencia e justificativa quando um validator nao se aplicar.
16. Nao declarar comportamento perceptivel, runtime, integracao, estado
    persistido ou artefato gerado como validado sem `<human_validation_gate>`.
17. Ao terminar cada task, executar checkpoint obrigatorio antes de liberar
    dependentes: validators/evidencias, status em `task-N.M.md` e `tasks.md`,
    `LokiRunState` completo (incluindo blockers e `next_action`) e proxima task
    pronta na DAG. Atualizar `builds/faseN/` e `interaction/faseN/` apenas conforme permitido.
18. Depois de checkpoint valido, seguir automaticamente para a proxima task
    pronta; nao encerrar entre tasks. Quando a plataforma oferecer compactacao
    de contexto, ela pode ocorrer depois do checkpoint, mas sua ausencia/falha
    nunca bloqueia a continuacao pelo estado persistido.
19. Quando uma task tiver `pending-technical-review` ou qualquer input humano
    material pendente, persista esse estado no checkpoint. Só emita o disclaimer
    destacado na resposta terminal causada por esse bloqueio real, usando o
    status exato como titulo e bullets concretos do que falta esclarecer,
    aprovar ou validar:

    ```markdown
    --------------
    pending-technical-review
    ------------

    - Aprovar ou ajustar ...
    - Confirmar ...
    - Responder ...
    ```
20. Em cada checkpoint, persista primeiro completion/evidence mínimo. Aplique
    `lf-execution-knowledge-capture`: despache cataloger somente para target
    exclusivo, continue sem esperar e reconcilie o estado serialmente depois.
    Interrompa/cancele no final e registre `partial` se ainda não terminal;
    falha de capture/validator nunca bloqueia implementação validada.
21. Ao concluir a fase, recomendar `loki-retrospectiva-tecnica` com resumo de
    arquivos afetados, validators, gates humanos, riscos residuais, comandos e
    scripts executados, outputs inesperados, inferencias uteis e incorretas,
    mismatches de ambiente, correcoes do usuario e desperdicios que a proxima
    execucao deve evitar.

## Inputs

- `TASKS_MD`.
- `EXECUTION_SCOPE` (`task`, `fase` ou `plano`).
- `FASE_ATUAL` condicional.
- `TASK_TARGET` opcional.
- `DIR_ANALISE` opcional.
- `task-N.M.md` da fase alvo.
- Decisoes humanas em `interaction/`.
- Escopo permitido, out of scope e forbidden writes.

## Outputs

- `Execution Brief`.
- Lista de tasks executadas, bloqueadas ou puladas com motivo.
- Evidencias de validators e build reports.
- Diffs ou artefatos gerados por owners `scoped-writer`, sempre associados a
  `target_files` e validators da task.
- Atualizacao de status em `tasks.md` e `task-N.M.md`.
- `LokiRunState` retomavel.
- Registros de `domain_context_preflight` por task/agent com durable roots/docs,
  freshness, conflicts, gaps, source precedence, result e next input.
- Disclaimer final destacado quando o status depender de input humano material
  nao resolvido pelo plano aprovado, como `technical-review`,
  `human-validation`, `approval`, `interview` ou outro gate pendente.
- Recomendacao de retrospectiva ao fim da fase.
- Entry refs ou estados degradados de execution knowledge, sem promoção.

## Limits

- Nao execute fora do escopo explicitamente selecionado; execute plano
  quando esse for o escopo selecionado.
- Nao escreva fora do escopo da task ativa.
- Nao pule dependencias pendentes.
- Nao use analise externa ou memoria da conversa como substituto de referencias
  em disco.
- Nao carregue skill tecnica por default.
- Nao marque human validation como aprovada sem resposta humana explicita.
- Nao permita handoff solto escrever no projeto consumidor. Escrita por agente
  exige `mode: scoped-writer`, task aprovada, `target_files`, `allowed_writes`,
  ownership exclusivo, validators e gates aplicaveis.
- Nao permita domain agent ou orquestrador escrever consumer docs; use somente
  `catalogador` com caller/mode fixo e bloqueie sem fallback se indisponivel.
- Quando o plano aprovado exigir retrospectiva tecnica por agente, o agente
  escreve somente o proprio `target_retrospective` exato sob
  `retrospetivas/faseN/`. Essa excecao nao se aplica a docs duradouros,
  inventarios finais, runtime, codigo, assets, config, `AGENTS.md`,
  `CLAUDE.md`, `.agents/**`, `.codex/**` ou `.claude/**`.
- O execution-knowledge cataloger não escreve shared state e sua falha,
  indisponibilidade ou demora nunca bloqueia conclusão de implementação.
- Stop conditions de dependency, handoff e validator se aplicam à implementação,
  write safety e resumability mínima. O cataloger é excluído; interrupção final
  reconciliada como `partial` com reason/`minimum_next_path` é terminal.

## Required Gates

- `interview` quando fase, task alvo, path ou requisito estiver ambiguo.
- `approval` para politica, instalacao, promocao, escrita sensivel ou mudanca
  fora do escopo aprovado.
- `human-validation` para comportamento perceptivel, runtime, integracoes,
  estado persistido ou artefatos gerados.
- `technical-review` para mudanca em command, skill, agent, template ou
  validator.

## Human Gate Resolution Policy

- `Human Loop` em `tasks.md` e `task-N.M.md` identifica o tipo de revisao, mas
  nao e uma ordem para parar sempre.
- Informacao explicitamente aprovada no plano, em artefatos aprovados de fases
  anteriores ou em confirmacao humana registrada deve ser tratada como aprovada
  para execucao.
- Pare e marque status pendente somente quando a execucao depender de input
  humano novo: inferencia fora do plano, desvio necessario, impossibilidade de
  cumprir o que estava descrito, validator falho/inconclusivo, escrita sensivel
  nao autorizada ou validacao perceptivel/runtime ainda nao confirmada.
- Quando parar, registre por que o plano nao bastou e liste as decisoes
  concretas pendentes. Nao use `technical-review` como checkpoint cerimonial.

## Validators

- `TASKS_MD` existe e referencia a fase alvo.
- Todos os `task-N.M.md` da fase alvo foram localizados ou a lacuna foi
  registrada como blocker.
- Se `tasks.md`, `task-N.M.md`, `builds/`, `interaction/` ou `retrospetivas/`
  estiverem ignorados ou nao aparecerem no `git status`, o estado foi conferido
  por leitura direta dos arquivos do plano.
- Dependencias e ordem topologica foram conferidas antes da execucao.
- Cada task executada tem referencia, validator, human loop e out of scope.
- Cada task com agente `scoped-writer` tem owner, `target_files`,
  `allowed_writes`, `scoped_write_domains`, validators e gates rastreados.
- `Execution Brief` foi produzido antes da primeira escrita.
- Toda escrita ficou dentro do escopo da task ativa, com owner e `target_files`
  rastreados.
- Preflight pessoal aplicavel foi executado pelo proprio Write Agent e os campos
  de root/docs/freshness/conflicts/gaps/precedence/result/next input foram
  persistidos; caller context nao foi aceito como substituto.
- Consumer docs pertencem ao `catalogador` com caller/mode esperado e ausencia
  resulta em blocker retomavel sem fallback.
- Validators foram executados ou justificados.
- Human gates pendentes nao foram marcados como aprovados quando dependiam de
  input humano material fora do plano aprovado.
- `LokiRunState` permite retomada sem memoria da conversa.
- Cada checkpoint terminal de task registra proxima acao e libera
  automaticamente a proxima task pronta, salvo stop condition real.
