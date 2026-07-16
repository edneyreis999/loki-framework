# Execution — loki-run-plan

## Purpose And Observable Contract

Este command é o orquestrador que executa uma task, fase ou plano aprovado sem depender
da memória da conversa, usando leitura paralelizável, escrita serializada,
validators, gates humanos materiais e estado retomável.

- Início: registro normalizado do Input, plano aprovado legível, fase/task
  resolvida, dependências e fronteiras de escrita conhecidas.
- Conclusão: todas as tasks do escopo terminal selecionado atingiram estado terminal, validators e
  gates aplicáveis foram processados, estado do plano e evidências foram
  atualizados, e não resta condição de parada ativa.
- Resultado verificável: artefatos autorizados, status coerentes em `tasks.md` e
  `task-N.M.md`, evidências em `builds/faseN/`, handoffs terminais e
  `LokiRunState` suficiente para retomada.
- Saídas obrigatórias: `Execution Brief`, artefatos ou diffs da fase, lista de
  tasks executadas/bloqueadas/puladas com motivo, resultados de validators,
  registros de gates e handoffs, completion/evidence state, plano atualizado e
  `LokiRunState`. Retrospectiva só é recomendada quando explicitamente prevista.

## Execution Profile

```yaml
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
```

## Orchestrator Responsibilities

Coordene as fases Input, Execution e Response. Decomponha a execução em unidades
com responsáveis identificáveis; selecione agentes apropriados; forneça contexto
autocontido a cada subagente; acompanhe cada handoff até sucesso, falha, bloqueio
ou parada explícita; aplique validators, gates e approvals; e consolide status,
artefatos, evidências, riscos e próximos passos. Delegar não transfere a
responsabilidade pelo progresso nem pelo estado global do fluxo.

## Dependencies

```yaml
required_skills:
  - lf-run-plan-execution
required_commands: []
```

Carregue `lf-run-plan-execution` antes de planejar ou aplicar a execução. Não há
skill técnica default do core. Carregue `<technology_required_skills>` somente
quando a task, o usuário, o contexto detectado ou retrospectiva aprovada exigir;
a skill selecionada deve declarar `<consumer_runtime_surfaces>`, validators e
`<human_validation_gate>` aplicáveis.

## Allowed And Forbidden Writes

Antes da primeira escrita, derive do plano e enumere como `allowed_writes`:

- `TASKS_MD`, task files da fase alvo e registros da fase em
  `interaction/faseN/`, somente para estado e decisões autorizadas;
- `target_files` de domínio, conteúdo, runtime, configuração, dados, scripts ou
  assets explicitamente autorizados pela task ativa e atribuídos a owner único;
- build reports e evidências autorizadas em `builds/faseN/`;

`forbidden_writes` inclui qualquer superfície fora da task ativa; fases não
selecionadas; targets sem owner; `.claude/**`, `.agents/**` e `.codex/**` sem
approval posterior específico; e runtime, engine, framework, dados persistidos
ou superfície sensível sem plano, owner, skill técnica quando exigida,
validators e gate humano. Não amplie silenciosamente o escopo; pare quando um path ou permissão
adicional for necessário.

## Preflight, DAG And Execution Brief

1. Consuma o registro normalizado; não reinterprete o pedido bruto de modo
   ambíguo.
2. Resolva paths relativos e absolutos. Pare se path obrigatório estiver
   ausente, ambíguo ou fora do plano ativo.
3. Leia diretamente `TASKS_MD`, todos os `task-N.M.md` da fase e os interaction
   records aplicáveis. Artefatos ignorados, untracked ou ausentes do status do
   VCS continuam obrigatórios e devem ser conferidos com `find`, `rg`,
   `sed` ou equivalente.
4. Resolva `EXECUTION_SCOPE`: `task` limita a uma task, `fase` a uma fase e
   `plano` abrange todas as fases retomáveis. Confira status, ordem topológica, dependências, referências, validators,
   observable validation, Human Loop, Definition of Done e resume notes. Não
   execute fora do escopo terminal solicitado.
5. Transforme a entrada em plano de execução com etapas, dependências,
   responsáveis, handoffs, possíveis escritas, validators, gates e critérios de
   conclusão. Detecte sobreposição e atribua owner único por arquivo.
6. Antes da primeira escrita, produza um `Execution Brief` com objetivo da fase,
   tasks em ordem, dependências pendentes, fontes lidas, arquivos e superfícies
   prováveis, skills sugeridas e origem, approvals existentes, validators,
   human gates, riscos, blockers e próximo passo.
7. Replaneje explicitamente quando um resultado invalidar ordem, dependência,
   owner, escopo, validator, gate ou etapa posterior. Registre a mudança e não
   prossiga com plano obsoleto.

## Context And Source Handoffs

- Com `DIR_ANALISE`, delegue a uma ou mais instâncias de
  `execution-context-reader` em modo read-only a extração apenas dos fatos
  relevantes à fase, paralelizando por fonte ou lote pequeno independente.
- Sem `DIR_ANALISE`, quando as referências das tasks forem insuficientes,
  delegue ao `execution-context-reader` uma pré-análise local mínima do codebase
  e docs permitidos.
- Se a lacuna for ampla, ruidosa, pré-decisional ou multifonte, pare antes da
  escrita e delegue a `source-researcher` em modo read-only a produção de
  evidência que revise ou complemente o `Execution Brief`. Para lacuna estreita
  de fase, prefira `execution-context-reader`.

Resolva lacunas críticas antes de implementar. Não escreva sem referência
executável, approval, validator, skill técnica exigida ou decisão humana
obrigatória não coberta pelo plano ou por registro humano.

## Agents, Self-Contained Envelopes And Handoffs

Delegue leitura, pesquisa, implementação, teste e revisão ao agente que possua a
responsabilidade correspondente sempre que possível. Use:

- `technical-implementer` como Write Agent `scoped-writer` para target files
  técnicos; mantenha-o proposal-only quando escrita sensível ainda depender de
  decisão, skill ou gate;
- `gameplay-engineer` como `scoped-writer` para mecânicas, código/config de
  gameplay e superfícies runtime aprovadas;
- `narrative-designer`, `quest-content-designer` ou equivalente para conteúdo,
  diálogo, quests,
  escolhas, cenas, tuning e outros targets de domínio declarados;
- `runtime-qa` para checklist, reports e evidência de comportamento perceptível,
  runtime, integração ativa, estado persistido ou artefato gerado. Esse handoff
  pode acompanhar proposta/escrita técnica, mas nunca substitui validação humana.

Use delegação suportada pelo runtime somente quando o usuário tiver solicitado
delegação ou trabalho paralelo, ou quando o contrato de orquestração ativo já a
autorizar explicitamente. Se a política ativa não autorizar subagentes, registre
que o agente apropriado está indisponível; qualquer escrita pelo orquestrador
continua sujeita à exceção, ao envelope e ao completion record definidos abaixo.

Antes de invocar qualquer subagente, entregue um envelope autocontido com:

- objetivo, motivo e unidade atribuída;
- fatos, decisões, restrições, paths, documentos e evidências relevantes;
- dependências e resultados anteriores necessários;
- escopo, `allowed_writes`, `forbidden_writes`, owner e target files;
- critérios de sucesso, falha, conclusão e parada;
- validators, gates e approvals;
- formato da saída, evidências esperadas, destino e condições do handoff.

Não delegue com referências implícitas como “continue”, “use o contexto acima”
ou “faça o restante”. Para cada handoff registre origem, destino, objetivo,
entrada entregue, resultado esperado, status, evidência recebida e próximo
destino. Acompanhe até estado terminal; invocação isolada não conclui a unidade.

## Write Ownership And Serialization

Execute tasks uma por vez na ordem topológica. Leituras e handoffs read-only ou
proposal-only independentes podem ocorrer em paralelo; consolide retornos antes
de liberar escrita dependente. Toda criação, modificação, movimentação ou remoção
de arquivo deve ser entregue a um Write Agent apropriado com envelope completo.
Um único owner pode escrever cada arquivo em cada momento. Detecte escopos
sobrepostos, serialize operações compartilhadas e interrompa writers
concorrentes.

Antes de cada escrita, confirme task ativa, arquivo, superfície,
`<domain_ids>`, integration point, owner, `scoped_write_domains`,
`allowed_writes`, validators e gate. Um agente só pode atuar como
`scoped-writer` quando a task aprovada declarar target files, allowed writes,
owner exclusivo, validators e gates.

Escrita direta pelo orquestrador é exceção permitida apenas depois de verificar
e registrar que nenhum Write Agent apropriado está disponível; conveniência,
velocidade ou tamanho da mudança não justificam a exceção. Antes dela, declare
target files, `allowed_writes`, `forbidden_writes`, owner único, validators,
gates/approvals, critérios de sucesso/falha e evidências. Se o envelope não
cobrir a mudança, pare. Sempre registre no completion record o tipo de
implementação, motivo da ausência, oportunidade e escopo de um futuro Write
Agent, evidências e riscos observados. O orquestrador captura evidence ou gap;
nunca usa retrospectiva como fallback.

## Task Execution And Evidence

Para cada task na ordem topológica dentro do escopo terminal:

1. Confirme dependências concluídas e reconcilie o estado com evidência em disco.
2. Entregue contexto e envelope ao responsável e acompanhe o handoff.
3. Consolide o retorno e execute os validators antes de liberar dependentes.
4. Registre em `builds/faseN/` comando/checklist, resultado e evidência, ou
   justificativa objetiva quando um validator não se aplicar.
5. Execute checkpoint obrigatório antes de liberar dependentes: atualize task
   file, `TASKS_MD` e `LokiRunState` com status, arquivos afetados,
   validations/evidências, Human Loop, `next_action`, blockers e próxima task
   resolvida pela DAG; atualize interaction records quando autorizado.
6. Não marque comportamento perceptível, runtime, integração, persistência ou
   output gerado como validado sem validator aplicável e confirmação do gate
   humano exigido.

Após checkpoint válido, resolva automaticamente a próxima task pronta na DAG e
continue, sem resposta terminal intermediária. A resposta terminal só ocorre
quando o escopo selecionado acabar, o usuário cancelar, ou uma stop condition
real permanecer ativa. Se o host expuser compactação de contexto, faça-a somente
depois de persistir o checkpoint; indisponibilidade ou falha não bloqueia a
continuação a partir do estado persistido.

Ao concluir a fase, recomende retrospectiva técnica apenas quando o plano a
previr explicitamente, incluindo arquivos afetados, validators, gates, riscos residuais,
comandos/scripts, outputs inesperados, inferências úteis e incorretas, mismatches
de ambiente, correções do usuário e desperdícios a evitar.

## Validators

- `TASKS_MD` existe, é legível e referencia a fase alvo; todos os task files
  foram localizados por leitura direta ou a ausência é blocker.
- Dependências e DAG foram conferidas antes da execução.
- Cada task tem referência, validator, Human Loop, out of scope, Definition of
  Done e resume notes suficientes.
- O `Execution Brief` existe antes da primeira escrita.
- Cada escrita respeita task, owner, target files, allowed/forbidden writes,
  scoped domains, validators e gates; nenhuma sobreposição concorrente existe.
- Validators foram executados ou objetivamente justificados, com evidência.
- Handoffs atingiram estado terminal e runtime/percepção não foi declarado
  validado sem controle humano aplicável.
- Status em `tasks.md`, task files, builds e interactions são coerentes com a
  evidência real.
- `LokiRunState` permite retomada sem memória da conversa.

Quando a task tocar command, skill, agent, template, validator, manifest ou
política de pacote, execute também os checks de packaging declarados na task,
incluindo atualização de inventário quando aplicável, scan de referências
proibidas e `technical-review`. Não invente que um check passou.

## Human Gates And Non-Ceremonial Resolution

- `approval`: política, instalação, promoção ou escrita sensível.
- `human-validation`: comportamento perceptível, runtime, integração ativa,
  estado persistido ou artefato gerado.
- `technical-review`: mudança em command, skill, agent, template ou validator.
- `interview`: fase, task, path, requisito ou decisão material ambígua.

A coluna `Human Loop` e os gates de uma task aprovada documentam a natureza da
revisão, mas não impõem parada automática quando a execução segue exatamente o
que o plano já autorizou. Trate como aprovado o que estiver explicitamente no
plano, em artefato aprovado de fase anterior ou em confirmação humana
registrada.

Pare e marque o status humano real somente se houver decisão nova fora do
plano, desvio necessário, impossibilidade de executar como descrito, validator
falho/inconclusivo, escrita sensível sem autorização específica ou validação
runtime/perceptível ainda não confirmada. Explique por que o plano não bastou e
liste concretamente o que falta. Não use `technical-review` como checkpoint
cerimonial.

## Stop Conditions

Pare diante de entrada obrigatória ausente; path, fase, task ou ordem ambígua;
escopo/permissão insuficiente; dependência indisponível; referência executável
ausente; `Execution Brief` insuficiente; handoff sem destino; conflito de
writers; validator obrigatório ausente, falho ou inconclusivo; gate/approval
material pendente; decisão humana necessária; target fora da task; escrita
sensível sem skill/owner/validator/gate; ou `scoped-writer` sem envelope
completo. Não declare conclusão enquanto qualquer condição permanecer ativa.

## Resume Contract

Mantenha `LokiRunState` com plano e paths resolvidos, escopo terminal, fase, task atual, status,
`Execution Brief`, DAG e dependências, fontes lidas, handoffs e seus estados,
owners, allowed/forbidden writes, arquivos afetados, validations e evidências,
Human Loop, approvals/gates, etapas concluídas, blockers, riscos, próxima ação e
condição necessária para continuar. Preserve a evidência e retome desse estado;
não reinicie o fluxo quando ele bastar.
