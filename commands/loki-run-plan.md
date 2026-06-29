---
name: loki:run-plan
type: command
status: draft
domain: execution
required_skills:
  - loki-run-plan-execution
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - long execution with complex resume state
    - broad cross-artifact writes
    - high-risk implementation or sensitive write
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:run-plan

## Purpose

Executar uma fase planejada com leitura paralela, escrita serializada, validators, gates humanos e estado retomavel.

## Inputs

- `FASE_ATUAL`: numero ou identificador da fase alvo.
- `TASKS_MD`: caminho relativo ou absoluto para `tasks.md`.
- `TASK_TARGET` opcional: task especifica dentro da fase alvo.
- `DIR_ANALISE` opcional: diretorio ou arquivo de analise tecnica/pre-analise aprovada.
- Arquivos `task-N.M.md` correspondentes.
- Decisoes registradas em `interaction/`.

## Outputs

- Artefatos da fase.
- Status atualizado em task files e `tasks.md`.
- Evidencias em `builds/faseN/`.
- `Execution Brief` ou resumo equivalente com contexto, dependencias, riscos, validators e gates antes da primeira escrita.
- Disclaimer final destacado somente quando a execucao terminar com input humano
  material ainda necessario, como `pending-technical-review`,
  `pending-human-validation`, `pending-approval`, `interview` pendente ou outro
  bloqueio nao resolvido pelo plano aprovado.
- Retrospectiva quando a fase terminar.

## Allowed Writes

- Arquivos do plano ativo autorizados pela task.
- Build reports e interaction records da fase.

## Forbidden Writes

- Qualquer superficie fora do escopo da task.
- `.claude/**`, `.agents/**` e `.codex/**` sem approval especifico posterior.
- Runtime, engine, framework ou superficies sensiveis do consumidor sem plano, skill tecnica selecionada quando exigida, validadores e gate humano.

## Required Skills

- `loki-run-plan-execution` para preflight da fase, leitura de tasks, selecao de contexto, ordem de execucao, validators e estado retomavel.
- Nenhuma skill tecnica e default do core.
- Carregar `<technology_required_skills>` apenas por pedido do usuario, contexto detectado ou retrospectiva que tenha criado ou indicado skill especializada aprovada.
- A skill tecnica selecionada declara `<consumer_runtime_surfaces>`, validadores e `<human_validation_gate>` aplicaveis.

## Gates

- `approval` para politica, instalacao, promocao ou escrita sensivel.
- `human-validation` para comportamento perceptivel, superficies runtime, estado em execucao, integracoes ativas, dados persistidos ou artefatos gerados.
- `technical-review` para mudanca em command, skill, agent, template ou validator.

## Human Gate Resolution Policy

- A coluna `Human Loop` e os gates descritos em uma task aprovada documentam a
  natureza da revisao, mas nao obrigam parada automatica quando a execucao segue
  exatamente o que o plano ja autorizou.
- Considere como aprovado pelo plano qualquer decisao explicitamente descrita
  em `tasks.md`, `task-N.M.md`, artefatos aprovados de fases anteriores ou
  confirmacao humana ja registrada.
- Pare e marque `pending-technical-review`, `pending-approval`,
  `pending-human-validation` ou `interview` apenas quando:
  - a task exige uma decisao que nao esta no plano nem em decisao humana
    registrada;
  - a execucao precisou inferir, alterar ou escolher algo fora do que estava
    previsto;
  - algo previsto no plano nao pode ser executado como descrito;
  - um validator falhou ou ficou inconclusivo;
  - a mudanca toca superficie sensivel, runtime perceptivel ou instalacao que
    exige confirmacao humana especifica.
- Quando parar, explique concretamente por que a parada foi necessaria e quais
  pontos dependem do usuario. Nao use technical-review como checkpoint
  cerimonial.

## Workflow

1. Confirmar `FASE_ATUAL`, `TASKS_MD`, `TASK_TARGET` opcional, `DIR_ANALISE` opcional, escopo permitido e forbidden writes.
2. Resolver paths relativos ou absolutos e parar se algum path obrigatorio estiver ausente, ambiguo ou fora do plano ativo.
3. Carregar `loki-run-plan-execution`.
4. Ler `TASKS_MD`, identificar tasks da fase alvo, localizar os arquivos `task-N.M.md` correspondentes e conferir ordem topologica, dependencias, status, validators e human loops. Se os artefatos do plano estiverem ignorados, untracked ou ausentes do `git status`, conferir estado por leitura direta em disco (`find`, `rg`, `sed`/equivalente) e nao usar status do VCS como unico validador.
5. Montar um `Execution Brief` antes de escrever: objetivo da fase, tasks em ordem, referencias, arquivos provaveis, superficies afetadas, skills sugeridas, approvals existentes, riscos, blockers e proximo passo.
6. Se `DIR_ANALISE` foi informado, acionar uma ou mais instancias de
   `execution-context-reader` em modo read-only para extrair apenas informacoes
   relevantes para a fase alvo. Paralelizar por fonte ou lote pequeno quando
   houver multiplos arquivos independentes.
7. Se `DIR_ANALISE` nao foi informado e as referencias das tasks forem
   insuficientes, usar `execution-context-reader` em modo read-only para uma
   pre-analise local minima do codebase e docs permitidos. Se a lacuna for
   ampla, ruidosa ou multi-fonte demais para a fase de execucao, pausar antes
   da escrita e acionar `source-researcher` para produzir evidencia que revise
   ou complemente o `Execution Brief`. Paralelizar apenas quando houver fontes
   independentes.
8. Resolver lacunas criticas antes da implementacao. Nao iniciar escrita quando
   faltarem referencia executavel, approval, validator ou decisao humana
   obrigatoria nao coberta pelo plano aprovado ou por decisao humana registrada.
9. Carregar skills tecnicas apenas quando a task, contexto detectado, pedido do usuario ou retrospectiva aprovada exigir `<technology_required_skills>`.
10. Executar tasks em ordem topologica, uma por vez. Leitura pode continuar em paralelo; escrita permanece serializada pelo orquestrador.
11. Antes de cada escrita, confirmar que o arquivo, superficie, `<domain_ids>` e gate estao cobertos pela task ativa e pelo plano.
12. Rodar validators da task e registrar evidencias em `builds/faseN/` ou justificativa objetiva quando um validator nao se aplicar.
13. Atualizar task files e `tasks.md` com status, arquivos afetados, validations, human_loop e next_action.
14. Acionar `runtime-qa` quando a mudanca depender de comportamento perceptivel, runtime, integracao ativa, estado persistido ou artefato gerado.
15. Quando uma task terminar com `pending-technical-review` ou qualquer input
    humano material ainda pendente, encerrar a resposta final com um bloco
    destacado no formato abaixo, listando em bullets o que ainda precisa ser
    esclarecido, aprovado ou validado:

    ```markdown
    --------------
    pending-technical-review
    ------------

    - Aprovar ou ajustar ...
    - Confirmar ...
    - Responder ...
    ```

    Substituir o titulo pelo gate real quando for `pending-human-validation`,
    `pending-approval`, `interview` ou outro status humano pendente.
16. Ao concluir a fase, recomendar ou iniciar `loki:retrospectiva-tecnica`
    conforme o contrato do plano, incluindo resumo de arquivos afetados,
    validators, gates humanos, riscos residuais, comandos e scripts executados,
    outputs inesperados, inferencias uteis e incorretas, mismatches de ambiente,
    correcoes do usuario e desperdicios que a proxima execucao deve evitar.

## Orchestration Rules

- Leitura e analise podem ser paralelas.
- Escrita deve ser feita por um unico orquestrador.
- Handoffs `read-only` ou `proposal-only` podem rodar em paralelo quando as
  entradas forem independentes; seus retornos devem ser consolidados antes de
  qualquer escrita.
- Conflitos por arquivo, superficie, gate ou destino bloqueiam escrita ate resolucao.

## Handoffs

- `execution-context-reader` em modo read-only para extrair contexto de
  `DIR_ANALISE` ou fazer pre-analise local minima quando referencias de task
  forem insuficientes. Enfatizar paralelismo por fonte, task ou lote pequeno.
- `source-researcher` em modo read-only quando nao houver analise aprovada e a
  lacuna de contexto for pre-decisional, multi-fonte ou ruidosa. Use antes da
  primeira escrita; para contexto estreito de fase, prefira
  `execution-context-reader`.
- `technical-implementer` em modo proposal-only quando a task exigir proposta
  para escrita sensivel, integration point, asset, artefato gerado ou
  `<consumer_runtime_surfaces>`. Pode rodar em paralelo com `runtime-qa` quando
  a superficie ja estiver conhecida ou hipotetizada.
- `runtime-qa` em modo read-only/proposal-only para checklist e evidencia humana
  quando validators automaticos nao cobrirem comportamento perceptivel. Pode
  rodar em paralelo com proposta tecnica, mas nunca substitui human validation.

## Stop Conditions

- `FASE_ATUAL`, `TASKS_MD` ou task files nao existem ou sao ambiguos; quando `DIR_ANALISE` for informado, ele tambem deve existir.
- Nao e possivel determinar quais tasks pertencem a fase alvo ou a ordem topologica segura.
- `Execution Brief` nao consegue listar objetivo, dependencias, referencias, validators e human loops suficientes para executar sem memoria da conversa.
- Input humano obrigatorio pendente que nao esteja resolvido pelo plano
  aprovado ou por decisao humana registrada.
- Validator blocker falhou.
- Validacao humana necessaria ainda nao foi confirmada.
- A task exige superficie fora do escopo aprovado.
- A task exige escrita sensivel sem approval, skill tecnica aplicavel, validator e gate humano.

## Final Response Contract

Se a execucao terminar com status humano pendente real, a ultima secao da
resposta ao usuario deve ser um disclaimer visualmente destacado. Use o status
exato como titulo e bullets concretos para o que falta decidir. Nao diluir esse
aviso em prosa comum. Nao emitir disclaimer quando a task foi executada conforme
o plano aprovado e nao restar decisao humana material.

Exemplo:

```markdown
--------------
pending-technical-review
------------

- Aprovar a matriz antes de executar a proxima task.
- Confirmar se algum papel deve mudar de agente para skill/checklist.
```

## Resume Contract

Manter `LokiRunState` ou resumo equivalente com fase, task, status, execution_brief, fontes lidas, arquivos afetados, validations, human_loop, blockers e next_action.
