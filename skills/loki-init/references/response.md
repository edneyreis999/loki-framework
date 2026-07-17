# Response — loki-init

## Response

Use este contrato para respostas intermediarias e terminais. Derive o estado
dos artefatos persistidos no `plan_root` e dos paths materializados em disco;
nao use memoria da conversa como fonte autoritativa.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: XML valido, estavel e parseavel, sem prosa fora de
  `command_response`, com `summary`, `status`, `artifacts`,
  `operational_state`, `investigator_handoffs`, `packet_registry`,
  `publication_batches`, `coverage`, `catalogador_publications`, `evidence`,
  `gates`, `risks`, `next_action` e `loki_init_state`.
- `Humano`: Markdown claro, conciso e acionavel, com no maximo 7.000
  caracteres; priorize resultado, blockers exatos, riscos e proxima acao.
- `Both`: Markdown legivel por pessoa e recuperavel por outra LLM, sem limite
  rigido.

Se outro consumidor for escolhido, aplique seu formato. Se estiver indefinido e
a escolha alterar o formato, resolva antes de responder.

## Required Field Contract

Respostas `Both` intermediarias e terminais usam exatamente estes campos de
primeiro nivel, na mesma ordem do asset `../assets/response-template.md`:

1. `Status`
2. `Resumo`
3. `Roots, modo e caller`
4. `Artefatos`
5. `Estado operacional`
6. `Investigator handoffs`
7. `Packet registry`
8. `Publication batches`
9. `Coverage`
10. `Publicacoes do catalogador`
11. `Evidencias e validators`
12. `Gates e approvals`
13. `Riscos ou blockers`
14. `Proxima acao e retomada`
15. `loki_init_state`

Campos sem ocorrencias usam `none`; nao omita o campo. Lists e tabelas podem
ser compactadas, mas cada registro aplicavel preserva os subcampos definidos no
template.

## Status Semantics

- `completed`: escrita selecionada concluida, reconciliation `committed` e
  todos os requisitos materiais terminais no depth exigido.
- `audited`: `audit-only` terminou sem escrita e reportou o estado observado.
- `partial`: escopo parcial terminou honestamente ou existe gap nao compativel
  com conclusao global, sem ocultar o blocker.
- `needs-input`: uma decisao, approval ou dado humano exato e necessario.
- `blocked`: dependencia, integrity check, writer, coverage, validator, gate ou
  recovery condition impede progresso seguro.
- `stopped`: stop condition encerrou a tentativa atual; informe checkpoint e
  condicao exata para retomar.

Nunca declare `completed` quando existir qualquer um destes estados:

- packet `pending`, `accepted` sem destino terminal, ou orfao; packet aceito
  deve estar `materialized`, `superseded` ou `blocked` explicado;
- qualquer publication batch cujo lifecycle nao seja `committed`: `planned`,
  `dispatched`, `write-applied`, `validated` ou `blocked`. `blocked` e terminal
  somente para bookkeeping de recovery e resultado `blocked`/`partial`; nunca
  e conclusao bem-sucedida. Todo batch aplicavel deve estar `committed` para
  permitir `completed`;
- requirement `pending` ou `deferred`, `mapped` para `required_depth: deep`,
  `blocked`, ou coverage sem evidence refs aceitas;
- materializacao ausente, ref/hash divergente, root apenas bootstrap, ou final
  reconciliation diferente de `committed`;
- validator falho/inconclusivo, gate/approval material pendente, handoff aberto,
  catalogador init ativo ou stop condition ativa.

## Intermediate Response

Para pergunta, conflito, gate ou stop condition, preencha todos os campos do
asset com o estado atual. Declare a decisao exata necessaria, o primeiro estado
nao terminal, a evidencia lida do disco, artefatos ja seguros, blockers e a
condicao minima de retomada. Nao antecipe uma resposta terminal nem declare
conclusao.

## Terminal Response

Para `Both`, preencha integralmente `../assets/response-template.md`:

- identifique `consumer_project_root`, `docs_root`, `plan_root`, mode,
  `calling_workflow` e cada `write_mode` realmente usado;
- reporte artefatos docs e plano separadamente, com status, refs e hashes de
  materializacao quando aplicavel;
- reporte investigator handoffs, packets comuns e de tecnologia e packets por
  dominio, sem copiar payloads integrais;
- mostre acceptance e materialization separadamente. Estados relevantes do
  packet sao `received`, `accepted`, `batched`, `materialized`, `rejected`,
  `blocked` e `superseded`; preserve revision, hash, continuation e refs;
- mostre todo batch aplicavel com caller/mode, lifecycle, checkpoint, packet
  set, targets, hashes e materialization refs; batch `blocked` nunca pode ser
  omitido e exige `blocker` e `recovery_action` explicitos;
- mostre coverage por `domain_id` e `requirement_id`, com `required_depth:
  map|deep`, state, evidence refs, materialized refs e reason;
- mostre bootstrap, publication batches e final reconciliation como operacoes
  separadas do `catalogador`, sempre com `calling_workflow: loki-init` e o
  `write_mode` exato;
- diferencie completion records de session evidence sanitizada e nao duplique
  payload bruto de packet, runtime transcript, token dump ou raciocinio privado;
- termine com a proxima acao, owner, checkpoint atual e `resume_condition`
  suficientes para continuar sem a conversa.

Diagnostique blockers pelo ledger, payloads, hashes, snapshots e paths atuais em
disco. Se um artefato estiver ausente, divergente ou ilegivel, diga exatamente
qual ref/path falhou e qual recovery action e segura; nao invente estado.

## XML Shape For LLM

```xml
<command_response>
  <status></status>
  <summary></summary>
  <roots_mode_and_caller></roots_mode_and_caller>
  <artifacts></artifacts>
  <operational_state></operational_state>
  <investigator_handoffs></investigator_handoffs>
  <packet_registry></packet_registry>
  <publication_batches></publication_batches>
  <coverage></coverage>
  <catalogador_publications></catalogador_publications>
  <evidence></evidence>
  <gates></gates>
  <risks></risks>
  <next_action></next_action>
  <loki_init_state></loki_init_state>
</command_response>
```
