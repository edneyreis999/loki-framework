# Execution — loki-agentic-development

## Execution

Use este contrato para a fase de execução.

## Purpose And Observable Contract

Este command orquestra demanda → análise agentic → decision preflight → plano →
execução autônoma por fases → completion/evidence → execution knowledge →
digest/backlog, sem
substituir `loki-run-plan` como executor manual. Inicia com Input normalizado e
diretório aprovado; termina com todos os handoffs e validators terminais e um
estado `completed`, `blocked` ou `pending-human-validation`. Produz manifest XML,
POVs/síntese, plano, completion records, evidências/gaps, knowledge
entries/degraded states, digest e backlog.

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha unidades, selecione agentes,
forneça contexto autocontido, acompanhe handoffs até sucesso, falha, bloqueio ou
parada, aplique validators/gates/approvals e consolide resultados, evidências,
riscos e próximos passos. Delegação não transfere responsabilidade global.

## Dependencies And Allowed Writes

Carregue `lf-agentic-orchestration` e `lf-execution-knowledge-capture`. Use,
nessa ordem condicional,
`loki-human-decision-preflight`, `loki-generate-action-plan` e `loki-run-plan`.
Carregue também cada
`<technology_required_skills>` quando a demanda, a análise ou o plano aprovado
exigir tecnologia específica. Allowed writes: estado/evidência dentro do run
aprovado, plano no destino aprovado e targets autorizados pelas tasks quando
executados por `loki-run-plan`. Forbidden: alterar `loki-run-plan`; `.claude/**`,
`.agents/**`, `.codex/**`; qualquer target fora do plano; runtime/sensível sem
owner, validator e gate; promoção automática de retrospectiva ou execution
knowledge.

## Plan, Preflight And Agent Handoffs

Crie/atualize `agentic-run-manifest.xml` antes do fan-out. Faça capability e
agent preflight, registrando selection reason, modo, owner, riscos, paralelismo
e skips. Selecione o menor conjunto útil e delegue leitura multifonte,
tecnologia específica, escrita sensível/runtime e validação material. Só retenha
trabalho material no orquestrador com exceção concreta, escopo, risco e owner de
validação registrados.

Use explicitamente `runtime-qa` quando a execução depender de comportamento
perceptível, integrações, estado persistido ou artefatos gerados.

Antes de cada subagente, forneça objetivo/motivo, unidade, fatos, decisões,
restrições, fontes, dependências, allowed/forbidden writes, targets, owner,
critérios, validators, gates, formato e destino. Registre handoff id, origem,
destino, entrada, expected output, status, evidência e próximo destino; acompanhe
até terminal. Abra fan-out apenas para leituras independentes ou targets
disjuntos; serialize overlaps.

## Integrated Workflow

1. Registre estado inicial retomável e preflight.
2. Colete POVs read-only separados e, quando material, uma rodada de cross-review.
3. Consolide `analise/sintese.xml` com fatos, divergências, gates, plano,
   validators e stop conditions.
4. Registre `experience_juice_needed`; abra waves adicionais mínimas quando
   lacunas pós-MVP materiais existirem, sem lista fixa de agentes.
5. Execute decision preflight e não avance com `must_ask_now` pendente.
6. Gere plano executável com dependências, writers, validators, loops e resume.
7. Execute uma fase topológica por vez via `loki-run-plan`, sem perguntar ao
   humano no meio da execução autônoma; converta limites em blocker/backlog.
8. Em cada checkpoint material, persista primeiro o completion/evidence mínimo
   sanitizado. Só depois, quando suportado, invoque
   `execution-knowledge-cataloger` em paralelo para um target exclusivo em
   `<run>/execution-knowledge/entries/<capture-id>.xml`; a implementação
   continua sem esperar pelo enriquecimento.
9. Reconcilie serialmente `captured`, `partial`, `failed`, `unsupported` ou
   `skipped-nonmaterial` no checkpoint/run state/digest. No checkpoint final,
   não espere por handoff não terminal: interrompa/cancele e registre `partial`
   com reason e `minimum_next_path`. Falha ou validator de knowledge nunca
   invalida implementação já validada.
10. Registre validators, digest e backlog; finalize o estado e o próximo passo.
   Retrospectiva é ação explícita, nunca fallback, e somente
   `loki-continuous-improvement` promove conhecimento.

## Write Ownership And Direct-Write Exception

Todo arquivo tem owner único; writers concorrentes com overlap são proibidos.
Delegue mudanças a `scoped-writer` com targets, allowed/forbidden writes,
validators, gates e evidência. Escrita direta só após registrar inexistência de
Write Agent apropriado; conveniência não serve. Declare envelope completo e
registre no completion record implementação, motivo, oportunidade/escopo do
futuro writer, evidências e riscos.

## Validators And Human Gates

Valide XML parseável; selection reason por agente; handoffs completos; writers
com targets/limits/controls; trabalho material delegado ou exceção; checkpoint
experience; zero must-ask pendente antes do plano; zero overlap paralelo; plano
executável; validators/evidência ou gap explícito por fase; zero
write fora de escopo. Aplique interview para decisões materiais pré-plano,
approval para instalação/política/sensível, human-validation para runtime e
technical-review para artefatos duradouros. Pare se qualquer controle falhar ou
estiver pendente; validator não substitui gate humano.

Para execution knowledge, valide target exclusivo, lineage para fontes
persistidas, materialidade, enum e sanitização. Falha desse validator degrada
somente o estado de capture. O cataloger jamais escreve manifest/digest/backlog,
run state, plano, runtime ou policy.

## Packaging Checks

O entrypoint esperado é `skills/loki-agentic-development/SKILL.md` e a helper
skill é `skills/lf-agentic-orchestration/SKILL.md`. Durante schema 1, command e
projection permanecem registrados em `manifest.yaml` e `install-scopes.json`;
no cutover, o bundle assume a autoridade conforme schema 2. Execute
`python3 scripts/validate-install-scopes.py` antes de concluir.

## Stop Conditions

Pare sem demanda/escopo/run aprovado; sem orchestration skill; com must-ask
pendente; síntese ou experience wave impossível sem inventar; plano inválido;
run-plan blocker/out-of-scope; overlap; trabalho material sem owner/exceção;
necessidade de nova pergunta durante execução; validator de estado ausente; ou
dependência/handoff/gate da implementação indisponível. Estas stop conditions
cobrem implementação, write safety e resumability mínima; não cobrem
availability, failure, timeout, handoff ou validator do
`execution-knowledge-cataloger`. Um cataloger interrompido no checkpoint final e
reconciliado como `partial` com reason e `minimum_next_path` é terminal para a
conclusão genérica. Não declare conclusão com outra condição ativa.

## Resume Contract

Registre demanda, run directory, agentes selecionados/pulados e motivos,
handoffs, gates, síntese, experience checkpoint/waves, plano, fase/task atual,
agent runs, targets, owners, validators, completion/evidence states, capture
IDs, knowledge target/status/reason/minimum next path, blockers, backlog, status
e próximo passo. Retome sem reiniciar quando suficiente.
