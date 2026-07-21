---
title: Workflow de Execucao de Plano do Loki
type: plan-execution-workflow
status: draft
created: 2026-06-26
self_contained: true
---

# Workflow de Execucao de Plano do Loki

Este e o guia humano canonico para entender como uma descricao pequena do que
deve ser implementado vira plano executavel, depois codigo ou artefato aplicado,
e finalmente evidencia para o [Workflow de Aprendizado do Loki](loki-learning-workflow.md).

![[loki-plan-execution-workflow.excalidraw.md]]

## Ideia central

O Loki nao deve pular de uma frase curta direto para escrita em runtime,
framework, engine ou arquivos sensiveis. O fluxo transforma intencao em
evidencia, evidencia em plano, plano em tasks retomaveis, tasks em escrita
serializada e resultado validado em aprendizado.

Quando a frase inicial ainda estiver vaga, `loki-demand-text-improver` pode
enriquece-la antes da escolha entre os caminhos operacionais. Esse passo e
terminal: entrega apenas um Markdown enriquecido e exige uma nova escolha do
usuario para qualquer analise, decisao, plano ou execucao.

A execucao termina quando a fase tem artefatos, validadores, evidencias e
estado atualizado. Aprendizado duradouro nao nasce automaticamente nessa etapa:
ele passa pelo workflow de aprendizado.

## Dois caminhos operacionais

`loki-demand-text-improver` e uma preparacao opcional anterior aos dois
caminhos. Ele nao exige um estado de sessao especifico, recebe um `destination`
existente e gravavel e usa naming deterministico: `<stem>-improved.md` para
arquivo ou `improved-demand.md` para texto inline. Input invalido, destino
inseguro ou colisao bloqueiam sem escrita.

O caminho manual continua sendo explicito: uma rota de analise
(`loki-tech-analysis` por padrao ou `loki-deep-analysis` opt-in),
`loki-human-decision-preflight`, `loki-generate-action-plan`,
`loki-enrich-tasks` quando aplicavel e `loki-run-plan` por fase ou task.

Quando for util separar a preparacao deterministica da investigacao,
`loki-generate-inferences` e um fork opcional antes de `loki-deep-analysis`.
Ele recebe uma entrada de analise, fontes locais permitidas e um diretorio
existente e aprovado abaixo de `<consumer-root>/planos/`, sem symlink ou
traversal. Deriva exatamente
`request_controls={discovery_limit: policy.values.catalog_limit}`. Seleciona
somente candidatos relevantes, investigaveis, sustentados por proveniencia
observavel, validos/compativeis, nao duplicatas exatas e dentro do limite;
rejeita irrelevantes, invalidos, incompativeis, inverificaveis e duplicatas
exatas. Preserva near duplicates separadas e adia somente evidencia essencial,
compatibilidade ou contexto ainda nao resolvido, ou candidato elegivel fora do
`discovery_limit`. Custo e impacto nao pertencem ao candidato nem influenciam
essa disposicao pre-investigacao. Antes da approval, resolve target versionado
por slug/digest e menor `-vN` ausente. A approval vincula diretorio canonico,
target exato, basename/versao, before-state/snapshot e um create exclusivo.
Colisao posterior invalida a approval e bloqueia sem retry; exige nova resolucao
e nova approval.
Cria somente esse unico output e termina
em `pre-investigation-complete`; nao executa investigacao, fan-out, handoff,
agent run, web research, CI, catalog mutation ou workflow downstream. A rota
seguinte e sempre escolhida manualmente em novo pedido; este fork nao a invoca.

O caminho integrado v2 usa `loki-agentic-development` quando o usuario quer
sair de uma demanda simples para analise agentica, gates materiais antes do
plano, plano gerado e execucao autonoma. Esse fluxo usa
`lf-agentic-orchestration` para selecionar agentes, registrar estado XML,
controlar fan-out, reports, digest e backlog. Ele preserva `loki-run-plan` como
executor manual e como executor delegado quando o plano chega na etapa de
execucao.

## Fluxo

1. O usuario traz uma descricao curta, feedback, PRD, NSD ou pedido direto.
2. Se a demanda precisar ser esclarecida sem ainda analisa-la ou planeja-la,
   use `loki-demand-text-improver`. O command termina no Markdown enriquecido e
   nao aciona automaticamente analise tecnica, decision preflight, action plan,
   `loki-agentic-development` ou execucao. O usuario deve escolher o proximo
   passo em um novo pedido.
3. Use `loki-agentic-development` quando a intencao for executar o caminho
   integrado v2 de demanda para analise, plano e execucao autonoma. Se o
   usuario quiser controle manual por etapa, siga os passos seguintes.
4. Se a entrada vier de observacao humana, bug percebido ou validacao manual,
   use `loki-feedback` antes de propor solucao. Ele investiga uma pergunta por
   vez e registra diagnostico sem escrever automaticamente.
5. Antes de uma investigacao profunda, use opcionalmente
   `loki-generate-inferences` para persistir um unico core de preparacao
   deterministico sob `planos/`. Ele termina antes da investigacao, sem
   dispatch, CI, pesquisa web, mutacao de catalogo ou proxima chamada
   automatica; uma pessoa escolhe manualmente a proxima rota permitida.
6. Use `loki-tech-analysis` quando a decisao exigir evidencias, hipoteses,
   riscos, superficies afetadas, pesquisa condicionada, validators ou gates.
   Quando as fontes forem ruidosas, desconhecidas ou multi-fonte, acione
   `source-researcher` em modo read-only antes da matriz de decisao.
   Quando a demanda exigir descoberta de tecnologias, consulta seletiva a um
   catalogo de inferencias, candidatos contextuais ou investigacoes
   independentes, use `loki-deep-analysis` de forma opt-in nessa mesma etapa,
   antes do decision preflight. Ele nao aninha `loki-tech-analysis`; seu report,
   eventos e candidatos nao alteram o catalogo nem constituem validacao de
   runtime.
7. Use `loki-human-decision-preflight` quando a analise ou brief tiver
   perguntas humanas pendentes antes do plano. Ele separa `must_ask_now`,
   `can_delegate_to_plan`, `can_validate_later` e
   `do_not_ask_llm_can_determine`.
8. Use `loki-generate-action-plan` para transformar a analise aprovada e as
   decisoes humanas registradas em
   `tasks.md`, `task-N.M.md`, dependencias, human loops, validators e estado de
   retomada.
9. Antes da execucao, use `loki-enrich-tasks` quando retrospectivas, builds,
   interactions ou aprendizados locais puderem reduzir ambiguidade da fase
   atual. Pesquisa externa continua condicionada: a frase exata deve ser
   mostrada ao usuario antes da busca.
10. Use `loki-run-plan` para executar uma fase ou task aprovada. Ele carrega
   `lf-run-plan-execution` e `lf-domain-context-preflight`, monta um
   `Execution Brief`, resolve contexto e
   bloqueia escrita quando faltar decisao, validator, approval ou gate humano.
11. Cada agente executa preflight pessoal: consulta a menor documentacao,
   registra freshness, conflitos, lacunas e fontes atuais, que prevalecem sobre
   docs stale. `bibliotecario` apenas localiza a menor leitura suficiente; o
   preflight nunca autocorrige docs.
12. `execution-context-reader` pode ler `DIR_ANALISE`, tasks, docs e fontes
   locais em modo read-only para extrair apenas o que afeta a fase alvo. Quando
   nao houver `DIR_ANALISE` e as referencias da task forem insuficientes, ele
   faz uma pre-analise local minima antes da primeira escrita.
13. Se a lacuna sem `DIR_ANALISE` for ampla, ruidosa ou multi-fonte demais para
   a fase de execucao, pause antes de escrever e use `source-researcher` para
   produzir evidencia que revise ou complemente o `Execution Brief`.
14. Skills tecnicas entram somente quando a task, o contexto, o usuario ou uma
   retrospectiva aprovada exigir aquela tecnologia.
15. A implementacao acontece task por task, em ordem segura. Leitura pode ser
   paralela; escrita fica serializada por owner e arquivo. O owner pode ser o
   orquestrador ou um agente `scoped-writer` quando a task aprovada declarar
   `target_files`, validators e gates.
16. Tasks que tocam estado de inferencias do consumidor declaram
    `destination_scope: consumer-operational-state`, resolvem internamente o
    consumer root do `pwd` canonico e derivam somente
    `<consumer-root>/.loki/analytic-inference/v2/`. O owner exclusivo e
    `technical-implementer` em `task_scoped_writer`, com targets exatos e writes
    serializados por arquivo. Registry ausente ou vazio em leitura retorna
    `insufficient` e zero writes; instalacao e lookup nunca fazem bootstrap. O
    estado ativo usa `registry.xml`, indices `index.xml`, records `rev-N.xml` e
    events `.xml`. JSON nao e fallback de lookup nem fonte de catalogo
    suportada. O layout v1 e rejeitado antes de processamento; JSON de policy,
    request, approval e output permanece control plane, nao estado de catalogo.
    O pacote distribui somente contratos, schemas, scripts, fixtures e policy:
    nunca catalogo de producao, seed ou overlay.
17. Promocao e reorganizacao em `.loki` exigem validators, technical review e
    approval root-bound antes da mutacao. Purge exige dry-run completo e uma
    approval JIT independente, posterior, single-use e vinculada a root, IDs,
    paths, hashes e digests exatos. Nenhum score autoriza write ou delete.
18. Tasks de docs duradouros do consumidor pertencem exclusivamente ao
    `catalogador`, caller `loki-run-plan`, mode `task_scoped_writer`.
    Indisponibilidade bloqueia; nenhum fallback escreve esses targets.
19. Quando a task tocar runtime, integracao ativa, estado persistido, asset,
    artefato gerado ou comportamento perceptivel, `runtime-qa` produz checklist
    e evidencia esperada, mas nao substitui validacao humana.
20. Ao concluir, atualize `tasks.md`, `task-N.M.md`, `builds/faseN/`,
    `interaction/faseN/` e `LokiRunState` ou resumo equivalente com fase,
    task, arquivos afetados, validations, human loops, blockers e proximo
    passo.
21. No mesmo checkpoint, persista primeiro completion/evidence mínimo. Quando
    o evento for material, despache `execution-knowledge-cataloger` em paralelo
    para uma entry exclusiva; continue sem esperar e reconcilie depois um dos
    estados `captured`, `partial`, `failed`, `unsupported` ou
    `skipped-nonmaterial`. No final, cancele/interrompa captura não terminal sem
    bloquear a execução validada.
22. Quando a fase terminar, pausar claramente ou uma dificuldade real for
    resolvida, passe para `loki-retrospectiva-tecnica` e siga o
    [Workflow de Aprendizado do Loki](loki-learning-workflow.md), incluindo
    validators, gates, comandos/scripts, outputs inesperados, inferencias,
    mismatches de ambiente, correcoes humanas e desperdicios relevantes.
    Eventos e candidatos analiticos seguem depois para
    `loki-continuous-improvement`; captura ou score nunca os promove
    automaticamente.

## Artefatos participantes

### Commands

| Command | Contribuicao no workflow |
| --- | --- |
| `loki-feedback` | Normaliza feedback humano, investiga causas e evita escrever com premissas fracas. |
| `loki-demand-text-improver` | Enriquece uma demanda antes da analise ou do plano e termina em um Markdown, sem iniciar workflow downstream. |
| `loki-generate-inferences` | Prepara opt-in um unico core deterministico sob `planos/` antes da investigacao; termina sem dispatch, CI, web research, mutacao de catalogo ou chamada downstream. |
| `loki-tech-analysis` | Converte demanda em analise baseada em evidencias, riscos, alternativas, validators e gates. |
| `loki-deep-analysis` | Oferece uma rota opt-in assistida por catalogo antes de decision preflight e action planning, sem aninhar a analise padrao, mutar catalogo ou validar runtime. |
| `loki-human-decision-preflight` | Classifica decisoes humanas pendentes antes do plano e evita perguntar o que a LLM deve resolver por fonte local. |
| `loki-agentic-development` | Orquestra o caminho integrado v2 de demanda para analise agentica, gates, plano, execucao autonoma, reports, digest e backlog. |
| `loki-generate-action-plan` | Cria plano faseado retomavel com `tasks.md`, tasks individuais, dependencias e human loops. |
| `loki-enrich-tasks` | Melhora apenas a fase atual usando aprendizados transitorios, sem promover regra duradoura. |
| `loki-run-plan` | Orquestra execucao aprovada, exige preflight pessoal, reserva docs do consumidor ao `catalogador`, registra estado e valida evidencias. |
| `loki-retrospectiva-tecnica` | Captura o que realmente aconteceu depois da execucao para alimentar aprendizado. |

### Skills

| Skill | Contribuicao no workflow |
| --- | --- |
| `loki-feedback` | Define o protocolo de uma pergunta por vez, hipoteses com evidencia e proposta so depois de contexto suficiente. |
| `lf-tech-analysis-authoring` | Padroniza analise tecnica, mapa de fontes, matriz de decisao, pesquisa condicionada e handoff para plano. |
| `lf-analytic-inference` | Compartilha consulta seletiva, eventos, snapshots, score e elegibilidade sem permitir mutacao automatica do catalogo. |
| `lf-analytic-inference-preparation` | Produz o core deterministico e read-only de pre-investigacao, sem dispatch, CI, pesquisa web, mutacao de catalogo ou replay byte a byte. |
| `loki-human-decision-preflight` | Classifica perguntas humanas antes do plano e registra quando o proximo passo ja pode seguir para action planning. |
| `loki-agentic-development` | Wrapper Codex para carregar o contrato integrado v2. |
| `lf-agentic-orchestration` | Regras reutilizaveis de preflight de agentes, fan-out, estado XML, gates, reports, liveness, invalidacao, digest e backlog. |
| `lf-action-plan-authoring` | Garante que o plano tenha fases, tasks, dependencias, referencias, validators, gates e retomada por disco. |
| `loki-enrich-tasks` | Injeta aprendizados na task certa do plano ativo, preservando fontes sensiveis e sem criar norma duradoura. |
| `lf-run-plan-execution` | Faz preflight, `Execution Brief`, ordem topologica, roteamento de contexto com ou sem `DIR_ANALISE`, escrita serializada, validators e `LokiRunState`. |
| `lf-execution-knowledge-capture` | Define materialidade, entry exclusiva, estados degradados e a regra não bloqueante de checkpoint. |
| `lf-domain-context-preflight` | Consulta docs e fontes atuais, registra freshness, conflitos e lacunas sem autocorrigir documentacao. |
| Skills tecnicas opcionais | Entram apenas quando a superficie exige tecnologia especifica, como runtime, engine, framework, dados ou plugins. |

### Agents

| Agent | Contribuicao no workflow |
| --- | --- |
| `execution-context-reader` | Extrai contexto relevante em modo read-only antes da escrita, incluindo pre-analise local minima quando faltam referencias executaveis. |
| `source-researcher` | Mapeia fatos, lacunas e conflitos em pesquisa multi-fonte antes de decisao, plano ou execucao, especialmente quando a lacuna pre-escrita e ampla demais para `execution-context-reader`. |
| `technical-implementer` | Writer exclusivo de `consumer-operational-state` sob `.loki/analytic-inference/v2/` quando a task declara consumer root canonico, targets exatos, validators e gates; fora desse envelope retorna proposta. |
| `runtime-qa` | Produz checklist de validacao e evidencia esperada para comportamento perceptivel ou runtime. |
| `bibliotecario` | Localiza, de forma estreita, a menor documentacao duradoura suficiente. |
| `catalogador` | Unico writer de `/docs` do consumidor, inclusive em tasks escopadas de `loki-run-plan`. |
| `execution-knowledge-cataloger` | Escreve uma entry run-local exclusiva a partir de fontes persistidas, sem tocar shared state nem promoção. |
| `standards-curator` | Entra depois da retrospectiva, quando houver candidato a regra duradoura ou backlog. |
| `gameplay-engineer` | Pode escrever mecanicas, codigo/config de gameplay ou dados aprovados quando a task atribuir `target_files` e skills/gates aplicaveis. |
| `narrative-designer` | Pode escrever conteudo narrativo, dialogos, escolhas e texto de dominio quando a task atribuir `target_files` e gates aplicaveis. |

## Gates e pontos de parada

- Pare antes de escrever se `FASE_ATUAL`, `TASKS_MD`, task alvo, referencias,
  validator, approval ou human loop estiverem ausentes ou ambiguos.
- Pare antes de escrever se o `Execution Brief` nao conseguir listar objetivo,
  dependencias, referencias, validators e human loops suficientes para execucao
  sem memoria da conversa.
- Nao execute plano inteiro quando o usuario pediu apenas uma fase ou task.
- Nao edite runtime, engine, framework, assets, dados persistidos,
  integracoes ou superficies sensiveis sem plano aprovado, skill tecnica
  aplicavel, owner de escrita, validator e gate humano.
- Nao acione agente `scoped-writer` sem `target_files`, `allowed_writes`,
  owner exclusivo, validators e gates suficientes.
- Nao trate `.loki` como docs do consumidor nem como artefato do pacote.
  `framework-artifact-writer` e `catalogador` nunca escrevem esse state root.
- Pare antes de promocao ou reorganizacao em `.loki` sem technical review e
  approval root-bound. Para purge, pare sem dry-run e approval JIT propria,
  posterior e ainda nao consumida.
- Pare se o preflight pessoal nao registrar fontes, freshness, conflitos,
  lacunas e suficiencia do contexto. Nao autocorrija docs nesse preflight.
- Se uma task exigir docs do consumidor, atribua ao `catalogador`; sua
  indisponibilidade bloqueia a task.
- Nao declare comportamento perceptivel como validado sem confirmacao humana.
- Nao transforme resultado de execucao diretamente em regra duradoura. A
  promocao acontece no workflow de aprendizado.

## Resultado esperado

Ao fim da execucao, outra LLM deve conseguir retomar pelo disco:

- qual fase ou task foi executada;
- qual `Execution Brief` guiou a escrita;
- quais fontes foram lidas;
- qual preflight pessoal registrou freshness, conflitos, lacunas e precedencia;
- quais arquivos foram alterados;
- qual owner escreveu cada arquivo quando houve agente `scoped-writer`;
- quais validators rodaram ou foram bloqueados;
- qual gate humano ficou pendente ou foi satisfeito;
- quais evidencias foram salvas;
- qual `LokiRunState` ou resumo equivalente permite retomada;
- qual bloco retomavel registra task, contexto, docs pendentes e proximo ponto;
- qual retrospectiva ou proximo passo deve alimentar o aprendizado, incluindo
  atritos materiais que a proxima execucao deve evitar.
- quais capture IDs, entry refs ou estados degradados preservam conhecimento sem
  depender da conversa.
# Evidence capture at completion

At each terminal handoff, the orchestrator correlates run, agent-run and
handoff IDs, then invokes a provider-neutral collector. The default artifact is
a sanitized, atomically published snapshot and checksum-bearing manifest. A
closed or unsupported adapter records a typed degraded state rather than an
automatic retrospective or synthetic token count.
