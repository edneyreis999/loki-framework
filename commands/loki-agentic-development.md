---
name: loki:agentic-development
type: command
status: draft
domain: orchestration
required_skills:
  - lf-agentic-orchestration
  - loki-human-decision-preflight
  - loki-generate-action-plan
  - loki-run-plan
  - loki-retrospectiva-tecnica
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - multi-agent analysis with material conflicts
    - autonomous execution across multiple planned phases
    - unresolved decision gates before action planning
    - target file conflicts between agent runs
    - high-risk runtime or integration work delegated by a generated plan
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: medium
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:agentic-development

## Purpose

Executar o fluxo integrado v2 de demanda simples para analise agentica, gates
materiais, plano, execucao autonoma, evidencias, retrospectivas e digest, sem
substituir `loki:run-plan` como executor manual.

## Inputs

- Demanda em texto ou arquivo.
- Diretorio de execucao ou destino de run aprovado para artefatos transientes.
- Escopo permitido, fora de escopo e superficies proibidas.
- Decisoes humanas ja registradas, quando existirem.
- Catalogo de agentes disponivel na instalacao ativa, quando houver.
- Documentacao duradoura do consumidor quando for relevante para a demanda.

## Outputs

- `agentic-run-manifest.xml` com estado retomavel do fluxo integrado.
- Pasta `analise/` com manifest, POVs de agentes, reviews opcionais, sintese e
  decision gates ausentes, resolvidos ou bloqueantes.
- Registro de `loki:human-decision-preflight` quando houver decision gates
  materiais antes do plano.
- Plano gerado por `loki:generate-action-plan` quando a analise estiver pronta.
- Execucao das fases do plano por `loki:run-plan`, em ordem topologica.
- `agent-runs/faseN/*.xml` com handoffs, owners, target files, validators,
  evidencias, status e blockers.
- Retrospectivas por agente quando houver escrita, analise substancial,
  validacao material, blocker ou dificuldade resolvida.
- Digest integrado e backlog de pendencias nao bloqueantes.

## Allowed Writes

- Arquivos de estado e evidencia dentro do diretorio de execucao aprovado:
  `agentic-run-manifest.xml`, `analise/**`, `agent-runs/**`, `builds/**`,
  `interaction/**`, `retrospetivas/**`, `digest.xml` e `backlog.md`.
- Arquivos do plano gerado no diretorio aprovado para `loki:generate-action-plan`.
- Arquivos alvo autorizados por tasks do plano gerado, somente quando
  executados por `loki:run-plan` com owner, `target_files`, validators e gates
  definidos.

## Forbidden Writes

- `loki:run-plan`, seus contratos e seu comportamento manual.
- `.claude/**`
- `.agents/**`
- `.codex/**`
- Superficies fora do diretorio de execucao aprovado ou fora dos `target_files`
  autorizados pelo plano gerado.
- `<consumer_runtime_surfaces>` sem plano, owner, validator e
  `<human_validation_gate>`.
- `<sensitive_write_patterns>` sem approval especifico.
- Promocao automatica de retrospectivas para conhecimento duradouro.

## Required Skills

- `lf-agentic-orchestration` para preflight de agentes, delegacao obrigatoria de
  trabalho material, fan-out condicionado, estado XML, decision gates,
  cross-review, liveness, invalidacao,
  completion reports, digest e retrospectivas.
- `loki-human-decision-preflight` quando a analise gerar decision gates
  materiais antes do plano.
- `loki-generate-action-plan` para gerar o plano executavel depois da analise.
- `loki-run-plan` para executar autonomamente cada fase do plano gerado.
- `loki-retrospectiva-tecnica` para retrospectivas de fase ou agente quando
  exigidas pelo trabalho realizado.
- `<technology_required_skills>` somente quando a demanda, analise ou plano
  aprovado exigir uma tecnologia especifica.

## Execution Profile

- `model_class`: `frontier_reasoning`
- `default_effort`: `high`
- `max_effort`: `xhigh`
- `escalation_signals`: conflitos multiagente, gates materiais, execucao
  autonoma longa, conflito de targets, runtime de alto risco ou validator
  inconclusivo.
- `handoff_effort`: leitura e pesquisa em `medium`, implementacao em `medium`,
  documentacao duravel em `high`, validators em `medium`.
- `adapter_projection`: metadado consultivo em Codex e projetavel em Claude
  Code quando suportado.

## Handoffs

- Agentes selecionados em modo read-only para POV de analise.
- Agentes selecionados em modo proposal-only para review cruzado ou proposta
  tecnica sem escrita.
- Agentes `scoped-writer` somente quando uma task aprovada declarar owner,
  `target_files`, `allowed_writes`, `scoped_write_domains`, validators e gates.
- Agentes especialistas obrigatorios para leitura multi-fonte nao trivial,
  trabalho de tecnologia especifica, escrita sensivel/runtime, validacao
  material ou qualquer etapa que ameace consumir contexto substancial da main
  thread. Tarefas triviais, single-source e de baixo risco podem ficar no
  orquestrador somente com excecao registrada.
- `runtime-qa` quando a execucao depender de comportamento perceptivel,
  integracoes, estado persistido ou artefatos gerados.

## Workflow

1. Confirmar demanda, diretorio de execucao aprovado, escopo permitido, fora de
   escopo, forbidden writes e estado retomavel inicial.
2. Criar ou atualizar `agentic-run-manifest.xml` antes de iniciar fan-out.
3. Executar preflight de agentes: listar agentes disponiveis, registrar
   `selection_reason`, modo, owner permitido, riscos, paralelismo e motivos de
   skip.
4. Selecionar o menor conjunto util de agentes. Delegar trabalho material para
   agentes especialistas sempre que houver leitura multi-fonte nao trivial,
   escrita sensivel/runtime, tecnologia especifica, validacao material ou risco
   de budget de contexto. Abrir fan-out real quando os agentes puderem trabalhar
   com contexto de leitura independente ou `target_files` disjuntos. Se o
   orquestrador mantiver trabalho material, registrar excecao com motivo
   concreto, escopo, risco aceito e owner de validacao.
5. Coletar POVs de analise em arquivos separados sob `analise/agentes/`.
6. Executar no maximo uma rodada inicial de cross-review quando houver mais de
   um POV ou conflito material.
7. Consolidar `analise/sintese.xml`, registrando fatos, divergencias,
   decision gates, plano recomendado, validators e stop conditions.
8. Registrar checkpoint pos-MVP `experience_juice_needed` antes de gerar o
   plano. Se a sintese apontar lacunas materiais de experiencia, apresentacao,
   narrativa, audio, UX, balanceamento, onboarding, feedback, acessibilidade,
   performance, risco tecnico ou outra superficie relevante, abrir uma ou mais
   waves adicionais read-only/proposal-only com o menor conjunto util de
   agentes escolhido por lacuna, superficie e risco da demanda atual. Cada wave
   registra `selection_reason`, pergunta de analise, superficie afetada, risco,
   validator esperado e criterio de parada. Nao usar lista fixa de agentes.
9. Se houver decision gate material antes do plano, executar
   `loki:human-decision-preflight`. Prosseguir somente quando nao houver
   `must_ask_now` pendente.
10. Executar `loki:generate-action-plan` usando a sintese aprovada como fonte.
11. Executar as fases do plano por `loki:run-plan`, uma fase por vez, sem
    perguntar ao humano durante a execucao autonoma.
12. Durante a execucao, converter limites nao resolviveis automaticamente em
    blockers ou itens de backlog para a fase humana posterior.
13. Registrar validators, evidencias, completion reports, retrospectivas
    exigidas e digest integrado.
14. Encerrar com status retomavel: completed, blocked, pending-human-validation
    ou outro status concreto, sempre com proximo passo.

## Validators

- XML de estado e reports parseavel quando os templates v2 existirem.
- Todo agente selecionado possui `selection_reason`.
- Todo handoff possui `handoff_id`, owner, modo, inputs, expected output e
  status.
- Todo writer possui `target_files`, `allowed_writes`, validators e gates.
- Todo trabalho material possui agente owner ou excecao explicita do
  orquestrador com motivo, escopo, risco e owner de validacao.
- A sintese registra `experience_juice_needed`, decisao, criterio de parada e
  waves adicionais quando houver lacunas materiais pos-MVP.
- Nenhum `must_ask_now` segue pendente antes de gerar o plano.
- Nenhum grupo paralelo compartilha `target_files` sem serializacao.
- `loki:generate-action-plan` produziu tasks com dependencias, validators,
  human loops e resume state.
- Cada fase executada por `loki:run-plan` registrou validators e evidencias.
- Retrospectivas foram registradas para trabalho substancial e omitidas com
  justificativa para handoffs triviais ou agentes pulados.
- Nenhuma escrita ocorreu fora do diretorio de execucao aprovado ou dos
  `target_files` do plano.

## Human Gates

- `interview` via `loki:human-decision-preflight` somente para decision gates
  materiais antes da geracao do plano.
- `approval` para instalacao, politica, escrita sensivel ou destino nao
  aprovado.
- `human-validation` para comportamento perceptivel, runtime, integracoes,
  estado persistido ou artefatos gerados.
- `technical-review` para mudancas em command, skill, agent, template,
  validator, roteiro operacional ou docs consolidados.

## Packaging Checks

- O comando usa namespace `loki:`.
- Wrapper esperado: `skills/loki-agentic-development/SKILL.md`.
- Skill auxiliar esperada: `skills/lf-agentic-orchestration/SKILL.md`.
- O comando e o wrapper devem estar registrados em `manifest.yaml` e
  `install-scopes.json` quando adicionados ao conjunto instalavel.
- Validar com `python3 scripts/validate-install-scopes.py`.

## Stop Conditions

- Demanda, escopo permitido ou diretorio de execucao aprovado ausente.
- `lf-agentic-orchestration` indisponivel no perfil ativo.
- Decision gate `must_ask_now` pendente antes de gerar o plano.
- Sintese de analise nao consegue produzir plano executavel sem inventar
  referencia, approval, validator ou decisao humana.
- Checkpoint `experience_juice_needed` aponta lacunas materiais, mas o fluxo nao
  consegue selecionar wave adicional sem inventar agente, gate, validator ou
  superficie.
- `loki:generate-action-plan` falha ou gera plano sem dependencias,
  validators, human loops ou resume state suficientes.
- `loki:run-plan` reporta validator blocker ou escrita fora de escopo.
- Agentes paralelos compartilham `target_files` sem serializacao.
- Trabalho material permanece na main thread sem excecao registrada e sem owner
  de validacao.
- Execucao autonoma exigiria nova pergunta humana no meio do plano.
- `scripts/validate-agentic-run-state.py` ainda nao existe quando um fixture ou
  execucao declarar estado v2 como validado.

## Resume Contract

Registrar no estado integrado: demanda, diretorio de execucao, agentes
selecionados e pulados, `selection_reason`, handoffs, decision gates, caminho
da sintese, checkpoint `experience_juice_needed`, waves adicionais pos-MVP,
plano gerado, fase atual, task atual, agent runs, target files, validators,
evidencias, retrospectivas, blockers, backlog, status final e proximo passo.
