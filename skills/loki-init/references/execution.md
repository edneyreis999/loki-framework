# Execution — loki-init

## Purpose And Observable Contract

Este command orquestra a criacao, atualizacao ou auditoria de documentacao
duradoura de um consumidor sem modificar seu runtime. Discovery e investigacao
sao read-only; o orquestrador aceita packets, controla coverage, batches,
ledger e evidence; somente `catalogador` materializa consumer docs.

- Inicio: Input normalizado, roots resolvidos dentro das fronteiras aprovadas,
  modo valido, capability/catalog preflight e estado retomavel carregado ou
  inicializado.
- Conclusao de escrita: common discovery e investigadores selecionados estao
  terminais; packets, batches, coverage e materializacoes estao reconciliados;
  a reconciliacao final passou; validators e gates aplicaveis foram registrados;
  e nao resta stop condition ativa.
- Conclusao de auditoria: `audit-only` leu e validou as superficies permitidas,
  nao escreveu arquivo e reportou estado observado, gaps e proximo passo.
- Resultado verificavel: consumer `docs/**` foi escrito somente por chamadas
  seriais do `catalogador`; `planos/000-init-loki/**` contem o ledger resumido e
  payloads operacionais retomaveis escritos somente pelo orquestrador; runtime e
  superficies proibidas permaneceram intactos.
- Saidas: cumpra `references/response.md`; ate a revisao especifica dessa
  Response, inclua no estado e no resumo todos os campos operacionais definidos
  aqui, mesmo quando o template ainda nao os apresentar individualmente.

`loki-init` e a identidade canonica. `init-loki` pode ser alias de adapter, sem
criar outro workflow.

## Command Contract

```yaml
command_contract:
  name: "loki-init"
  purpose: "Materializar ou auditar documentacao inicial por packets aceitos e um catalogador serial."
  start_condition: "Input normalizado, roots seguros, modo valido e preflights concluidos."
  completion_condition: "Todo trabalho selecionado, packet, batch, coverage, validator e gate esta terminal; escrita exige reconciliacao final committed."
  outputs:
    - "consumer docs materializados pelo catalogador, quando o modo permite escrita"
    - "loki_init_state e payloads operacionais no plan root, quando o modo permite escrita"
    - "resposta terminal conforme references/response.md"
  allowed_writes:
    - "<consumer_project_root>/docs/** somente pelo catalogador"
    - "<consumer_project_root>/planos/000-init-loki/** somente pelo orquestrador"
  forbidden_writes:
    - "<consumer_runtime_surfaces>"
    - "<sensitive_write_patterns>"
    - ".agents/**"
    - ".codex/**"
    - ".claude/**"
    - "AGENTS.md"
    - "CLAUDE.md"
  required_skills: []
  required_commands: []
  validators:
    - "packet, batch, lifecycle, ownership, coverage, docs integrity and boundary validators"
  human_gates:
    - "approval"
    - "interview"
    - "human-validation"
  stop_conditions:
    - "missing input, permission, dependency, writer, validator, gate, handoff destination or safe resume state"
  resume_contract: "loki_init_state plus immutable packet/batch artifacts is sufficient without conversation memory or a live agent instance"
```

## Execution Profile And Dependencies

```yaml
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - consumer documentation bootstrap
    - resumable multi-agent investigation
    - serial consumer-doc publication
    - consumer write boundary ambiguity
required_skills: []
required_commands: []
```

Carregue `lf-index-navigator` somente quando `docs/index.xml` existir e precisar
ser lido. Carregue `<technology_required_skills>` somente depois de tecnologia
concreta ser sustentada por fonte ou decisao. `lf-domain-context-preflight` nao
e precondicao automatica dos investigadores init, do `catalogador` ou dos
agentes support-only: ele se aplica ao preflight cotidiano de um domain Write
Agent e sera adotado pelos contratos desses agentes em sua migracao propria.

Leia integralmente
[`docs/loki-init-inventory-contracts.md`](../../../docs/loki-init-inventory-contracts.md)
antes de criar coverage plans ou envelopes. Esse contrato define requisitos,
profundidade e cobertura; nao concede autoria documental a investigadores.

## Authority And Write Boundaries

O orquestrador e owner exclusivo de discovery comum, selecao, packet intake,
acceptance, coverage, batching, checkpoints, `loki_init_state`, completion
records recebidos e captura de session evidence. Ele pode criar ou atualizar
somente os paths exatos sob o `plan_root` aprovado. Payloads extensos ficam em
artefatos separados; `tasks.md` mantem o ledger resumido e autoritativo.

`catalogador` e o unico writer de consumer `docs/**`, inclusive
`project-inventory.md`, technology/engine context, roots de dominio,
READMEs, conflitos, perguntas e `docs/index.xml`. Toda mutacao de consumer docs
e um handoff ao `catalogador`; o orquestrador, investigadores e support-only
nunca criam, editam, movem ou removem esses paths.

`consumer-docs-fallback: prohibited`. Se `catalogador` estiver ausente,
indisponivel ou falhar preflight, bloqueie toda escrita em consumer docs e
preserve resume state. Nao use escrita direta, outro agente ou o orquestrador
como fallback. Package `docs/**`, quando resolvido sob o package root, e classe
`package-documentation` distinta e nao recebe autoridade deste command.

Os 15 investigadores nao recebem `allowed_writes` em consumer docs. Support-only
nao recebe escrita documental. Escritas no plan root nunca autorizam escrita em
docs. Fora de docs root e plan root, proiba runtime, engine, codigo, assets,
dados, config, dependencias, outputs gerados, `.agents/**`, `.codex/**`,
`.claude/**`, `AGENTS.md`, `CLAUDE.md` e qualquer escape por traversal ou
symlink divergente.

Em `audit-only`, `allowed_writes` e vazio para todos, inclusive plan root e
catalogador. Produza somente a resposta da sessao; nao "atualize o estado" para
registrar a auditoria.

## Mode Semantics

| Mode | Investigacao | Consumer docs | Plan state | Honest terminal meaning |
| --- | --- | --- | --- | --- |
| `full-init` | common + todos os requeridos | bootstrap, batches e final reconciliation | write | `completed` somente com coverage global terminal |
| `refresh-docs` | redescoberta dirigida por frescor e coverage | somente deltas aceitos, depois reconciliation | write | `completed` para o refresh selecionado; gaps globais preservados |
| `audit-only` | leitura e validacao somente | none | none | `audited`, nunca `completed` por materializacao nova |
| `agent-only:<agent>` | common minimo + um investigador selecionado | bootstrap se necessario, batches do agente e reconciliation parcial | write | `partial-completed`/`blocked`; nunca coverage global completed |

`agent-only` nao permite nome desconhecido, support-only ou `catalogador`. Em
refresh, nao reinvestigue packet aceito sem invalidacao observavel de fonte,
coverage ou frescor. Em audit, nunca dispare modo init com escrita.

## Preflight And Plan

1. Carregue `loki_init_state` e payloads referenciados diretamente do disco;
   arquivos ignorados ou untracked contam quando existem e validam.
2. Valide roots, mode, approvals, merge policy, filtros, current docs snapshot,
   symlinks e write boundaries. Nao sobrescreva silenciosamente.
3. Verifique capability real de delegacao do adapter antes de alegar
   indisponibilidade. Registre ferramenta, limites configurado/observado e
   degradacao; disponibilidade de namespace nao prova tags ou write authority.
4. Resolva uma fonte de catalogo que declare `supported_project_types`, base
   `core`, `agent_project_tag_policy` e `agents[].project_tags`. `manifest.yaml`
   pode ser fonte quando instalado e legivel, nunca dependencia universal.
5. Selecione exatamente um `selected_project_type` suportado. Hint e hipotese;
   conflito material vira interview antes do fan-out. `core` e base tag, nao
   project type.
6. Crie matriz `available -> required -> selected -> planned -> invoked |
   blocked | skipped`, com razoes, classes, coverage plan e status.
7. Monte DAG, envelopes autocontidos, checkpoints, owners, validators, gates,
   success/failure destinations e stop conditions. Replaneje quando uma fonte,
   capability, acceptance, coverage, batch, validator ou gate invalidar etapa
   dependente.
8. Confirme que nenhum writer de consumer docs esta ativo. No maximo uma chamada
   init do `catalogador` pode estar em `dispatched`, `writing`, `running` ou
   `write-applied`.

## Common Discovery Before The First Docs Write

O orquestrador executa discovery read-only sequencial. Mapeie arvore ate
`max_scan_depth`; aplique includes/excludes; filtre binarios, gerados e arquivos
grandes; registre manifests, comandos, stack, areas, docs existentes, concerns,
lacunas, superficies sensiveis e Git quando disponivel. Nao escreva docs.

Produza sob o plan root pelo menos:

- um `common inventory` research packet schema v1;
- um `technology context` research packet schema v1;
- um packet ou registro imutavel de selecao e coverage plan dos investigadores.

Trate os packets comuns como research packets: identidade, revision, SHA-256,
sources, fatos/inferencias tipados, coverage delta, acceptance e continuation.
Eles devem estar `accepted` no registry antes da primeira escrita em docs. A
classificacao de tecnologia registra evidencia, confianca, selected type,
skills candidatas, superficies sensiveis, validators e gates sem hardcode de
engine.

## Agent Classification And Bootstrap Order

Construa `inventory_required` como uniao ordenada sem duplicatas dos agentes com
tag base `core` e dos agentes com `selected_project_type`. Para
`software-development`, somente `core` e valido enquanto nao houver agente com
essa tag. Classifique os seguintes 15 papeis como
`init_inventory_domain_investigator`, read-only/proposal-only no init:

- `audio-designer`, `balance-economy-designer`, `game-business-analyst`,
  `game-designer`, `game-product-owner`, `gameplay-engineer`, `level-designer`,
  `narrative-designer`, `narrative-qa`, `quest-content-designer`,
  `scene-presentation-designer`, `technical-artist`, `technical-implementer` e
  `ux-ui-designer`.

Classifique apenas `catalogador` como `init_serial_cataloger`. Classifique
`standards-curator`, `retrospective-digester`, `execution-context-reader`,
`source-researcher` e `bibliotecario` como `init_support_only`. Support-only
retorna resultado estruturado read-only/proposal-only e nunca recebe consumer
docs writes. Investigador nao chama catalogador.

A ordem obrigatoria e:

1. capability e catalog preflight;
2. common discovery e classificacao de projeto/tecnologia;
3. selecao dos investigadores e coverage plan por requirement/domain;
4. acceptance dos packets comuns e checkpoint do registry;
5. checkpoint do bootstrap como `dispatched` antes do handoff;
6. primeira escrita de docs: uma chamada serial ao `catalogador` com
   `calling_workflow: loki-init` e `write_mode: init-bootstrap-cataloger`;
7. validacao e commit do bootstrap;
8. somente entao fan-out dependente dos investigadores.

O bootstrap materializa common inventory, technology context, navegacao inicial
e README substancial para cada investigador cuja invocacao sera tentada. Cada
README inclui identidade, selection reason, escopo, fontes comuns, status real e
coverage plan. Root existente ou README criado nao equivale a coverage terminal.
Falha posterior deve ser reconciliada como `blocked` ou `invocation-failed`.

## Self-Contained Handoffs

Todo handoff declara objetivo, unidade, fatos, decisoes, restricoes, fontes,
dependencias, scope, targets, `allowed_writes`, `forbidden_writes`, owner,
identidades/parentage, success/failure criteria e destinations, validators,
gates, approvals, formato de output e proximo destino. Nao use "continue" ou
"contexto acima". Acompanhe-o ate sucesso, falha, bloqueio ou stop explicito.

Envelope minimo de investigador:

```yaml
investigator_handoff:
  calling_workflow: "loki-init"
  run_id: ""
  handoff_id: ""
  investigator: ""
  investigator_invocation_id: ""
  init_class: "init_inventory_domain_investigator"
  execution_mode: "read-only | proposal-only"
  objective: ""
  topic_scope: []
  selected_project_type: ""
  selection_reason: []
  common_packet_refs: []
  accepted_packet_registry_refs: []
  coverage_plan_refs: []
  pending_requirement_ids: []
  sources_already_read: []
  continuation_cursor: "initial | <opaque-logical-cursor>"
  allowed_writes: []
  forbidden_writes:
    - "docs/**"
    - "planos/000-init-loki/**"
    - "<consumer_runtime_surfaces>"
  output:
    packet_batch: "1..N loki_init_research_packet schema v1 artifacts returned to orchestrator"
    invocation_completion: "compact completion record"
    continuation: "continue | complete | blocked plus cursor"
  success_destination: "loki-init packet intake"
  failure_destination: "loki-init blocker intake"
```

Cada invocacao emite de 1 a N packets versionados e um cursor. A instancia viva
e opcional: o trabalho logico continua por reinvocacao do mesmo papel com
registry, coverage pendente, fontes ja lidas e cursor. Nunca exija session resume
do provider. O investigator fica terminal apenas quando seu coverage plan esta
terminal ou ha blocker explicito.

Envelope de `catalogador` exige `calling_workflow: loki-init`, exatamente um
destes `write_mode`: `init-bootstrap-cataloger`, `init-publication-batch` ou
`init-final-reconciliation`, approval `granted`, `exclusive_write_owner:
catalogador`, docs snapshot, targets/roots, packet/ledger refs imutaveis,
validators, gates e destinations. Caller ausente/desconhecido, mode ausente ou
par cruzado falha antes da primeira escrita.

## Packet Intake And Acceptance

Para cada packet retornado, antes de continuar o investigador ou montar batch:

1. parseie `loki_init_research_packet` com `schema_version="1"`;
2. valide `run_id`, investigator/invocation, packet ID, revision, sequence,
   canonical SHA-256 e lineage;
3. valide sources attempted/read, source refs de cada fato, tipos de finding,
   scope, coverage delta, publication intent e continuation;
4. compare com registry: mesmo ID/revision/hash e no-op registrado; mesmo ID com
   conteudo divergente e rejeitado; revision maior so entra com `supersedes`
   exato para ID/revision/hash aceito anterior;
5. classifique `accepted | rejected | superseded` com razoes; packet rejeitado
   nunca entra em batch nem satisfaz coverage;
6. persista payload e checkpoint de acceptance no plan root; so depois marque o
   registry aceito e continue.

Packet aceito e imutavel. O registry mantem status de materializacao separado:
`unbatched | batched | materialized | blocked`. Todo accepted packet deve chegar
a `materialized`, `superseded` ou `blocked` explicado antes da conclusao. Packet
`pending`, `accepted` sem destino terminal ou sem continuation vira orfao e
bloqueia reconciliacao final.

## Coverage Contract

Cada requirement tem ID estavel, domain ID, `required_depth: map | deep`, estado
e evidence refs. Estados operacionais sao `pending | mapped | covered |
not_found | not_applicable | deferred | blocked`.

- `map` e terminal com `mapped`, `covered`, `not_found` ou `not_applicable`,
  sustentado por evidence aceita.
- `deep` e terminal com `covered`, `not_found` ou `not_applicable`, sustentado
  por evidence aceita; `mapped` nao satisfaz deep.
- `deferred` nunca e terminal para status global `completed`.
- `blocked` e terminal somente para resultado global `blocked` ou parcial
  explicitamente permitido pelo mode; nunca vira sucesso silencioso.
- bootstrap root/README nao altera coverage para terminal.

Atualize a coverage matrix apenas depois de acceptance. Uma revisao superseded
remove sua contribuicao ativa e aponta para a nova evidence. Coverage sem packet
aceito e invalida.

## Publication Batches And Serial Catalogador

Agrupe somente packets aceitos, coerentes e ainda nao materializados. Cada
`loki_init_publication_batch` schema v1 possui conjunto imutavel e ordenado de
IDs/revisions/hashes, `run_id`, `batch_id`, `idempotency_key`, `batch_hash`,
checkpoint anterior, before-state hash, docs snapshot, coverage esperado,
validators e success/failure destinations.

Lifecycle obrigatorio:

| Before | Allowed after | Checkpoint/effect |
| --- | --- | --- |
| `planned` | `dispatched`, `blocked` | persista batch imutavel e dispatch checkpoint antes da chamada |
| `dispatched` | `write-applied`, `blocked` | uma chamada serial do catalogador; nenhum outro init writer ativo |
| `write-applied` | `validated`, `blocked` | registre retorno, targets, before/after hashes e materialization refs |
| `validated` | `committed`, `blocked` | validators passam antes de commit no ledger |
| `committed` | none | terminal; retries identicos sao no-op |
| `blocked` | none | terminal com motivo e recovery action |

Uma nova tentativa le o checkpoint e o estado atual antes de agir. Entrega e
`at-least-once` com efeitos idempotentes, nunca `exactly-once`. Mesmo batch ID,
key, hash e packet set ja committed retorna no-op sem escrita. ID/key reutilizado
com conteudo divergente bloqueia. Crash depois de docs write e antes do commit
exige comparar hashes/materialization refs: commit/reconcile o efeito completo,
aplique somente delta seguro se parcial ou bloqueie ambiguidade; nunca replay
cego. Nao dispare proximo batch enquanto o anterior nao estiver `committed` ou
`blocked` explicado.

## Completion Records And Session Evidence

O research packet contem findings, sources, coverage e continuation. O compact
completion record contem somente identidade/parentage, terminal status, resumo,
arquivos lidos ou retornados, packet/batch/materialization refs, validations,
gates, tentativas materiais, erros conhecidos, decisoes, riscos e proximo
destino. Ele nao carrega payload integral, runtime locator, token usage ou
raciocinio privado.

Depois do retorno, o evidence collector/orquestrador correlaciona `run_id`,
`agent_run_id`, `handoff_id`, agent e locators tipados; captura apenas snapshot
sanitizado quando suportado; registra SHA-256/integridade e estados
`complete | partial | pointer-only | unavailable | unsupported` por dimensao.
Token usage precisa de proveniencia run-scoped; cumulativo/account-window nao e
consumo por agente. Lacuna continua lacuna, sem auto-retrospectiva ou evidence
fabricada. O executing agent nunca descobre ou inventa seus IDs tecnicos.

## Final Reconciliation

So planeje `init-final-reconciliation` quando:

- common discovery, selecao e todo investigator iniciado estao terminais;
- todo packet esta `rejected`, `superseded`, `materialized` ou `blocked` com
  destino final; nenhum pending/accepted orfao existe;
- todo batch esta `committed` ou `blocked` explicado; nenhum planned,
  dispatched, write-applied ou validated permanece;
- coverage de cada requirement/domain respeita required depth e e terminal para
  o status solicitado; completed nao admite pending, deferred, mapped-for-deep
  ou blocker;
- todo root selecionado possui materializacao factual ou blocker honesto; root
  de bootstrap sozinho nao satisfaz a condicao;
- nao ha outro catalogador init ativo.

Persista um reconciliation dispatch checkpoint e invoque uma vez o
`catalogador` com `calling_workflow: loki-init` e `write_mode:
init-final-reconciliation`. Ele reconcilia roots, READMEs, gaps, conflitos,
perguntas, links, navegacao e `docs/index.xml`; retorna hashes, validators e
materialization refs. Valide antes de marcar `final_reconciliation.status:
committed`. Falha mantem estado retomavel e impede `completed`.

## Checkpoints And Resume Algorithm

Checkpointe atomicamente no plan root depois de: preflight; common discovery;
packet persistence; packet acceptance; bootstrap/batch/reconciliation
`planned`; imediatamente antes de cada catalogador call (`dispatched`); retorno
(`write-applied`); validators (`validated`); ledger commit; cada investigator
continuation; e mudanca terminal de coverage/blocker.

Ao retomar:

1. leia e valide ledger + hashes dos payloads; nao use memoria da conversa;
2. se packet ja aceito com mesmo ID/hash, nao reinvestigue nem reaceite; use o
   registry e cursor;
3. se investigator nao terminal, reinvoque logicamente com coverage pendente,
   sources read e cursor, independentemente da instancia anterior;
4. se batch/bootstrap/reconciliation esta `dispatched` ou `write-applied`, reabra
   docs e compare snapshot/hashes/materialization antes de qualquer retry;
5. se batch esta `committed`, nunca o reenvie; retry identico e no-op;
6. retome do primeiro estado nao terminal cuja dependencia esteja satisfeita;
7. divergencia, checksum mismatch ou lineage ambigua bloqueia e pede recovery,
   sem apagar conhecimento para forcar o snapshot.

## Authoritative `loki_init_state`

Estenda estado existente; nao o substitua nem embuta payloads extensos:

```yaml
loki_init_state:
  schema_version: "2"
  consumer_project_root: ""
  docs_root: "docs"
  plan_root: "planos/000-init-loki"
  mode: "full-init"
  current_phase: ""
  status: "pending | running | partial-completed | audited | blocked | completed"
  created_or_audited_paths: []
  discovery:
    files_scanned: []
    files_deep_read: []
    ignored_patterns: []
    project_areas: []
    detected_project_types: []
    selected_project_type: ""
    detected_engines: []
    git_available: false
    common_inventory_packet_refs: []
    technology_context_packet_refs: []
    selection_packet_refs: []
  capability_and_catalog:
    capability_preflight: ""
    discovery_method: ""
    catalog_source: []
    supported_project_types: []
    agent_project_tag_policy: {}
    agent_project_tags: {}
    compatible_tools_found: []
    available: []
    required: []
    selected: []
    blocked: []
    skipped: []
  investigator_registry:
    <agent>:
      init_class: "init_inventory_domain_investigator"
      selection_reasons: []
      status: "planned | invoked | continuing | complete | blocked | skipped"
      invocation_ids: []
      continuation_cursor: ""
      sources_already_read: []
      pending_requirement_ids: []
      completion_record_refs: []
      evidence_manifest_refs: []
  packet_registry:
    <packet_id>:
      revision: 1
      hash: ""
      investigator: ""
      path: ""
      acceptance_status: "pending | accepted | rejected | superseded"
      materialization_status: "unbatched | batched | materialized | blocked"
      supersedes_ref: ""
      continuation_status: "continue | complete | blocked"
      batch_id: ""
      materialization_refs: []
      blocker: ""
  coverage_matrix:
    <requirement_id>:
      domain_id: ""
      required_depth: "map | deep"
      state: "pending | mapped | covered | not_found | not_applicable | deferred | blocked"
      evidence_packet_refs: []
      materialization_refs: []
      reason: ""
  bootstrap:
    operation_id: ""
    idempotency_key: ""
    hash: ""
    status: "not-planned | planned | dispatched | write-applied | validated | committed | blocked"
    packet_refs: []
    selected_domain_roots: []
    materialization_refs: []
  publication_batches:
    <batch_id>:
      idempotency_key: ""
      hash: ""
      path: ""
      packet_refs: []
      previous_checkpoint_ref: ""
      before_state_hash: ""
      status: "planned | dispatched | write-applied | validated | committed | blocked"
      catalogador_run_id: ""
      targets: []
      materialization_refs: []
      blocker: ""
  final_reconciliation:
    operation_id: ""
    idempotency_key: ""
    ledger_hash: ""
    status: "not-planned | planned | dispatched | write-applied | validated | committed | blocked"
    materialization_refs: []
    blockers: []
  catalogador_single_writer:
    active_run_id: ""
    active_mode: ""
    active_status: "none | dispatched | writing | write-applied"
    last_terminal_run_id: ""
  completion_records: []
  session_evidence: []
  conflicts: []
  open_questions: []
  validators_run: []
  gates: []
  blocked_by: []
  completed_steps: []
  next_recommended_command: ""
  next_action: ""
  resume_condition: ""
```

## Validators And Lifecycle Assertions

Execute e registre validator, resultado, evidencia e justificativa de N/A:

1. somente docs root e plan root mudaram; no plan root apenas orquestrador e em
   docs apenas catalogador; nenhum investigator possui docs `allowed_writes`,
   target inventory dir ou direct-target writer mode;
2. common inventory e technology packets foram aceitos antes da primeira docs
   write, que e `catalogador/init-bootstrap-cataloger`;
3. caller/mode exatos existem em toda chamada e caller ausente, mode desconhecido
   ou par cruzado falha antes de escrever;
4. no maximo um catalogador init esta ativo e nenhum fallback de consumer docs
   existe quando ele esta indisponivel;
5. todo packet parseia, correlaciona identidade/hash/sources/facts/coverage/
   continuation; retry identico e no-op; divergencia sem lineage e rejeitada;
6. accepted packet precede batch; packet set do batch e imutavel; lifecycle segue
   `planned -> dispatched -> write-applied -> validated -> committed` ou
   termina `blocked`;
7. todo accepted packet termina materialized, superseded ou blocked; nenhum
   packet orfao permanece;
8. coverage terminal respeita required depth; bootstrap root nao satisfaz
   coverage; completed rejeita pending/deferred, mapped-for-deep ou blocker;
9. final reconciliation so ocorre com investigadores, packets, batches e
   coverage terminais;
10. `docs/index.xml` parseia, paths e links tocados resolvem, campos minimos
    existem e nao ha entrada duplicada/orfa ou ID transitorio necessario a
    descoberta;
11. cada handoff tem completion record e o collector capturou session evidence
    sanitizada ou gap tipado, sem raciocinio privado nem token inventado;
12. nenhum runtime, build behavior, gameplay, UI, audio ou persistencia e
    declarado validado sem human-validation.

Fixtures/assertions minimas de cold start e resume:

| Fixture | Assertion |
| --- | --- |
| cold start | packets comuns accepted; primeira docs write e bootstrap catalogador |
| investigator continuation | nova instancia recebe cursor/registry e nao repete source/packet aceito |
| identical packet retry | mesmo ID/revision/hash resulta no-op |
| divergent packet retry | mesma identidade com hash divergente sem supersedes e rejected |
| batch lifecycle | somente transicoes da tabela passam |
| crash after write | hashes permitem reconcile/commit ou bloqueiam; nunca replay cego |
| committed batch resume | batch nao e redispatched |
| concurrent writers | segundo catalogador init e rejeitado antes da escrita |
| premature final | pending/deferred/orphan/deep-mapped bloqueia reconciliation completed |
| audit-only | zero writes em docs e plan root |

Use `python3 scripts/validate-loki-init-catalogador-contracts.py` para schemas,
caller/mode, ownership, single-writer, transitions e retry fixtures. O modo
`--enforce-current-tree` e gate pos-migracao: enquanto agents/callers posteriores
a esta task ainda nao tiverem migrado, registre a falha isolada como dependencia
futura; os checks task-scoped do bundle `loki-init` devem passar. Aplique tambem
entry/reference routing, command checklist 24/24, forbidden-reference scan
documentado, ownership scan focal, Markdown/frontmatter parse e `git diff
--check`.

## Human Gates

- `approval` antes de qualquer destino ou write scope sensivel nao coberto pelo
  Input normalizado; ausencia bloqueia sem ampliar autoridade.
- `interview` para root, mode, merge, classificacao ou conflito material
  ambiguo.
- `human-validation` antes de declarar clareza/navegabilidade nao deterministica
  ou comportamento de runtime, build, gameplay, UI, audio e persistencia.
- Alteração deste package contract, agent, skill, template ou validator é
  encaminhada somente para futura `loki-continuous-improvement` com
  `destination_scope: package`; este fluxo não invoca Writer nem Auditor do
  pacote, e teste automático não concede autoridade de escrita.

## Stop Conditions

Pare diante de root/mode/destino ambiguo; path escape; permission/approval
insuficiente; merge inseguro; catalog source ausente; dependency ou handoff sem
destino; packet/schema/hash/lineage invalido; coverage sem evidence; packet
orfao; writer concorrente; catalogador indisponivel; tentativa de fallback em
consumer docs; batch nao terminal; retry divergente; checksum mismatch;
validator necessario ausente/falho/inconclusivo; gate pendente; ou pedido de
runtime sem skill, validator e human-validation. Preserve o ultimo checkpoint,
registre `blocked_by`, `next_action` e `resume_condition`, e nao declare
conclusao enquanto qualquer condicao material permanecer.

## Terminal Handoff And Response

Antes da Response, confira status, artefatos, packets/batches/materialization
refs, coverage, validators, completion records, evidence states, handoffs,
gates, riscos, blockers, next action e resume condition. Encaminhe ao humano em
Markdown recuperavel conforme `references/response.md` e
`assets/response-template.md`. `completed` e proibido com validator, gate,
approval, handoff, packet, batch, coverage ou reconciliation material pendente.
