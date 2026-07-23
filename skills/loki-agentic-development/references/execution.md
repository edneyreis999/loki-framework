# Execution — loki-agentic-development

## Execution

Use este contrato para a fase de execução.

## Purpose And Observable Contract

Este command orquestra demanda → análise agentic → decision preflight → análise
Markdown → uma chamada a `loki-implement-feature` → completion/evidence →
execution knowledge → digest/backlog. Ele adiciona POV, cross-review, síntese,
digest e backlog; não é alias, wrapper ou substituto do command unificado. Inicia com Input normalizado e
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

Carregue `lf-agentic-orchestration`, `lf-tech-analysis-authoring` e
`lf-execution-knowledge-capture`. Use, nessa ordem condicional,
`loki-human-decision-preflight` e `loki-implement-feature`.
Carregue também cada
`<technology_required_skills>` quando a demanda ou análise exigir tecnologia
específica. Allowed writes: estado/evidência e a análise Markdown dentro do run
aprovado; o child de implementação e production targets pertencem ao envelope
de `loki-implement-feature`. Forbidden: alterar o command unificado; `.claude/**`,
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
3. Consolide `analise/sintese.xml` com fatos, divergências, gates, abordagem,
   validators e stop conditions.
4. Registre `experience_juice_needed`; abra waves adicionais mínimas quando
   lacunas pós-MVP materiais existirem, sem lista fixa de agentes.
5. Execute decision preflight e não avance com `must_ask_now` pendente.
6. Materialize `analise/technical-analysis.md` com fontes, fatos, inferências,
   decisões, restrições, validators, gates e handoff direto completos. Valide o
   Markdown e seu digest antes de dispatch.
7. Invoque `loki-implement-feature` exatamente uma vez com a demanda original,
   `analysis_file: <run_directory>/analise/technical-analysis.md` e
   `plan_directory: <run_directory>/implementation/`. Não crie plano, DAG,
   target decisions, ciclos, retries, dashboard ou loop por fase no parent;
   essas autoridades pertencem ao command unificado.
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

Antes da chamada única, persista o locator/digest da demanda, análise Markdown,
plan directory reservado e `implementation_handoff_id`. Depois do retorno,
reconcilie a identidade, `loki_run_state`/digest, completion/evidence, validators
e dashboard fornecidos pelo command unificado. Divergência ou segundo handoff é
stop condition.

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
experience; zero must-ask pendente antes da análise Markdown; zero overlap
paralelo; um handoff unificado com inputs/digests exatos;
validators/evidência ou gap explícito por fase; zero
write fora de escopo. Aplique interview para decisões materiais pré-plano,
approval para instalação, política ou escrita sensível, e human-validation para
runtime. Quando esta execução identificar um candidato de pacote, registre somente o
encaminhamento para uma futura `loki-continuous-improvement` com
`destination_scope: package`; não invoque Writer nem Auditor do pacote. Pare se
qualquer controle concreto falhar ou estiver pendente; validator não substitui
gate humano.

Audite estaticamente que existe uma única identidade/call site de
`loki-implement-feature`, que recebe demand + Markdown analysis, e que nenhum
plano, DAG, retry, validation cycle ou dashboard paralelo é criado. Confirme
também que ordinary command discovery continua roteando diretamente ao command
unificado, nunca a este workflow avançado.

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
pendente; síntese ou experience wave impossível sem inventar; análise Markdown
inválida; unified-command blocker/out-of-scope; overlap; trabalho material sem
owner/exceção; demanda/análise/state digest divergente ou handoff duplicado;
necessidade de nova pergunta durante execução; validator de estado ausente; ou
dependência/handoff/gate da implementação indisponível. Estas stop conditions
cobrem implementação, write safety e resumability mínima; não cobrem
availability, failure, timeout, handoff ou validator do
`execution-knowledge-cataloger`. Um cataloger interrompido no checkpoint final e
reconciliado como `partial` com reason e `minimum_next_path` é terminal para a
conclusão genérica. Não declare conclusão com outra condição ativa.

## Resume Contract

Registre demanda, run directory, agentes selecionados/pulados e motivos,
handoffs, gates, síntese, experience checkpoint/waves, análise Markdown,
implementation handoff, fase/task atual,
agent runs, targets, owners, validators, completion/evidence states, capture
IDs, knowledge target/status/reason/minimum next path, blockers, backlog, status
e próximo passo. Preserve locator/digests da demanda/análise, plan directory,
handoff ID e as referências/digest do current run state e dashboard devolvidos.
Retome o mesmo handoff/estado sem loop por fase ou reinício quando suficiente.
