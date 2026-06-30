---
name: loki:init
type: command
status: draft
domain: consumer-bootstrap
aliases:
  - init-loki
required_skills:
  - loki-init
  - loki-retrospectiva-tecnica
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - consumer documentation bootstrap
    - multi-agent fan-out and serial consolidation
    - consumer write boundaries
  handoff_effort:
    research: medium
    coding: low
    documentation_transient: medium
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to command frontmatter where supported."
---

# loki:init

## Purpose

Inicializar um projeto consumidor recem-instalado com Loki criando ou auditando
`docs/**`, criando estado operacional retomavel em `planos/000-init-loki/**`,
inventariando o estado atual do projeto, acionando agentes especialistas por
envelope controlado e consolidando documentacao duradoura minima para futuros
workflows Loki.

`loki:init` e o nome canonico do pacote. `init-loki` pode existir como
alias/adaptador quando o runtime instalado suportar alias, mas nao cria um novo
namespace canonico.

## Inputs

- `consumer_project_root`: default diretorio atual.
- `docs_root`: default `docs`.
- `plan_root`: default `planos/000-init-loki`.
- `mode`: default `full-init`; opcoes futuras `refresh-docs`, `audit-only` e
  `agent-only:<agent-name>`.
- `engine_hint`: opcional.
- `project_type_hint`: opcional.
- `max_scan_depth`: opcional.
- `include_patterns`: opcional.
- `exclude_patterns`: opcional.

## Outputs

Documentacao duradoura permitida:

- `docs/index.xml`.
- `docs/loki-init/README.md`.
- `docs/loki-init/project-inventory.md`.
- `docs/loki-init/technology-context.md` ou
  `docs/loki-init/engine-context.md`.
- `docs/loki-init/open-questions.md`.
- `docs/loki-init/conflicts-and-decisions.md`.
- `docs/loki-init/<agent-name>/**` para inventarios factuais de agentes de
  dominio.

Estado operacional permitido:

- `planos/000-init-loki/tasks.md`.
- `planos/000-init-loki/task-1.1.md` quando o init materializar tasks.
- `planos/000-init-loki/interaction/fase1/**`.
- `planos/000-init-loki/builds/fase1/**`.
- `planos/000-init-loki/retrospetivas/fase1/**`.

## Allowed Writes

- `docs/**` no projeto consumidor.
- `planos/000-init-loki/**` no projeto consumidor.

A execucao explicita de `loki:init` aprova somente esses destinos. Se esses
diretorios ja existirem, preservar conteudo e entrar em modo merge/audit; nunca
sobrescrever silenciosamente.

## Forbidden Writes

- Runtime, engine, assets, dados gerados, build outputs, dependencias e codigo
  do consumidor.
- `.agents/**`, `.codex/**`, `.claude/**`.
- `AGENTS.md` e `CLAUDE.md`.
- Qualquer `<consumer_runtime_surfaces>` ou `<sensitive_write_patterns>` sem
  plano posterior, skill tecnica aplicavel, validators e gate humano.

## Required Skills

- `loki-init` para executar este workflow no Codex.
- `loki-retrospectiva-tecnica` para cada agente invocado registrar a propria
  retrospectiva antes de encerrar.
- `loki-index-navigator` quando `docs/index.xml` existir e precisar ser lido.
- `<technology_required_skills>` somente quando o inventario, o usuario ou um
  agente especialista declararem uma tecnologia especifica.

## Agent Init Write Policy

Durante `loki:init`, agentes classificados como
`init_inventory_domain_writer` recebem uma excecao estreita de escrita: cada um
pode escrever somente dentro do proprio `target_inventory_dir` em
`docs/loki-init/<agent-name>/`. O agente pode criar multiplos `.md` dentro
dessa pasta quando isso ajudar a leitura, mas nao pode escrever fora de
`docs/loki-init/<agent-name>/**`.

O conteudo da pasta deve satisfazer o contrato universal e o contrato por
especialidade em `docs/loki-init-inventory-contracts.md`. O workflow valida a
pasta inteira; nomes de arquivos, quantidade de documentos e secoes internas nao
sao parte do contrato.

Essa excecao nao autoriza `docs/index.xml`, `planos/000-init-loki/tasks.md`,
runtime, assets, dados, `.agents/**`, `.codex/**`, `.claude/**`, `AGENTS.md` ou
`CLAUDE.md`.

`catalogador` e classificado como `init_final_cataloger`. Ele nao recebe
`target_inventory_dir`, nao participa do fan-out paralelo de inventarios e e
invocado uma vez, em etapa serial final, depois que as pastas dos agentes de
dominio foram produzidas e validadas. O envelope do `catalogador` deve declarar
fontes, destinos de catalogacao e writes exatos; essa classe nao autoriza
inventario proprio em `docs/loki-init/**`.

Todo agente invocado, incluindo `init_inventory_domain_writer`,
`init_final_cataloger` e `init_support_only`, recebe tambem uma excecao estreita
para invocar `loki:retrospectiva-tecnica` ao terminar seu trabalho e escrever
somente o proprio `target_retrospective` exato em
`planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md`. Essa
excecao nao autoriza docs duradouros, inventarios finais, runtime, codigo,
assets, config, `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.codex/**` ou
`.claude/**`.

Agentes `init_support_only` nao geram inventario em `docs/loki-init/**` por
default. Eles podem ser invocados para leitura, pesquisa, validacao,
classificacao ou orientacao, retornam resultado estruturado para o orquestrador
e escrevem somente a propria retrospectiva tecnica quando invocados.

O init nao usa handoff como substituto para pasta de inventario de
`init_inventory_domain_writer` nem para retrospectiva tecnica por agente: o
agente escreve a propria pasta autorizada e a propria retrospectiva autorizada.

`init_inventory_domain_writer`:

- `audio-designer`
- `balance-economy-designer`
- `branching-narrative-designer`
- `dialogue-editor`
- `game-business-analyst`
- `game-designer`
- `game-product-owner`
- `gameplay-engineer`
- `level-designer`
- `narrative-designer`
- `narrative-qa`
- `quest-content-designer`
- `runtime-qa`
- `scene-presentation-designer`
- `technical-artist`
- `technical-implementer`
- `tools-pipeline-engineer`
- `ux-ui-designer`

`init_final_cataloger`:

- `catalogador`

`init_support_only`:

- `standards-curator`
- `retrospective-digester`
- `execution-context-reader`
- `source-researcher`
- `bibliotecario`

## Workflow

1. Preflight e escopo:
   - confirmar `consumer_project_root`, `docs_root` e `plan_root`;
   - declarar allowed writes e forbidden writes;
   - quando o workflow selecionar agent fan-out, declarar explicitamente a
     intencao de usar subagents/delegacao e executar preflight de capacidade
     antes de declarar agentes indisponiveis;
   - declarar que agentes `init_inventory_domain_writer` escrevem somente no
     proprio `target_inventory_dir` e nunca usam handoff como substituto dessa
     pasta;
   - declarar que o contrato de conteudo dos inventarios vem de
     `docs/loki-init-inventory-contracts.md`;
   - declarar que `catalogador` e `init_final_cataloger`, roda somente depois
     do fan-out de inventarios e nao recebe pasta de inventario propria;
   - declarar que todo agente invocado deve executar
     `loki:retrospectiva-tecnica` ao concluir sua parte e escrever somente o
     proprio `target_retrospective`;
   - verificar que o adaptador consegue conceder a cada agente invocado escrita
     escopada no proprio `target_retrospective`; se nao conseguir, registrar o
     agente como `blocked` ou `skipped` com motivo concreto antes do fan-out;
   - em Codex, projetar esse preflight como descoberta direcionada de
     capacidade multi-agent/subagent, por exemplo via `tool_search`; tratar
     namespaces concretos de ferramenta como evidencia da sessao atual, nao
     como contrato universal do pacote;
   - executar tambem preflight de catalogo de agentes antes da selecao: ler
     `manifest.yaml` como fonte estruturada primaria de agentes,
     `supported_project_types`, `agent_project_tag_policy` e
     `agents[].project_tags`;
   - quando superficies aprovadas do adaptador existirem, como `.codex/agents`,
     `.agents/agents`, `agents/`, `codex/agents/` ou inventario equivalente de
     agentes, usa-las como evidencia de disponibilidade/capacidade, nao como
     fonte primaria de tags de aplicabilidade;
   - registrar fonte do catalogo de agentes, agentes disponiveis,
     `supported_project_types`, tag base, tags por agente e limitacoes de
     descoberta; leitura de `.codex/**` ou `.agents/**` nao autoriza escrita
     nesses caminhos;
   - criar ou auditar `docs/` e `planos/000-init-loki/`;
   - criar ou auditar `interaction/fase1`, `builds/fase1` e
     `retrospetivas/fase1` quando o init precisar registrar interacoes,
     evidencias operacionais ou retrospectivas por agente;
   - parar se o usuario pedir destino fora de `docs/**` ou
     `planos/000-init-loki/**`.
2. Inventario comum sequencial:
   - mapear arvore de arquivos com filtros de binarios, gerados e arquivos
     grandes;
   - registrar docs existentes, manifestos, comandos, stack, areas, concerns,
     lacunas e superficies sensiveis suspeitas;
   - usar git como evidencia auxiliar quando disponivel, nunca como requisito;
   - produzir `docs/loki-init/project-inventory.md`.
3. Contexto de tecnologia:
   - detectar ou aplicar hints de tipo de projeto, engine e framework;
   - classificar `selected_project_type` em exatamente um valor de
     `supported_project_types` do `manifest.yaml`; `core` nao e tipo de
     projeto classificavel, e tag base sempre incluida;
   - quando `project_type_hint` existir, aceitar somente se ele estiver em
     `supported_project_types` ou registrar conflito/open question antes do
     fan-out;
   - registrar evidencia, confianca, skills tecnicas sugeridas, superficies
     sensiveis, validators e human gates;
   - registrar skills tecnicas candidatas como contexto para os agentes
     especialistas, sem executar regras de engine no workflow core;
   - produzir `docs/loki-init/technology-context.md` ou
     `docs/loki-init/engine-context.md`.
4. Fan-out paralelo por `agent_init_envelope`:
   - montar `inventory_required` pela uniao ordenada, sem duplicatas, dos
     agentes em `manifest.yaml` marcados com a tag base `core` e dos agentes
     marcados com `selected_project_type`;
   - registrar `inventory_required_reasons` por agente, apontando a tag que
     justificou a inclusao, por exemplo `project_tags: core` ou
     `project_tags: game-dev`;
   - usar `inventory_required` como lista selecionada para envelopes do init,
     limitada pela disponibilidade/capacidade do adaptador; se algum agente
     requerido nao for invocado, registrar `blocked` ou `skipped` com motivo
     concreto;
   - para `software-development`, enquanto nao houver agentes especializados
     com essa tag, selecionar somente agentes `core`;
   - dividir agentes selecionados entre `init_inventory_domain_writer`,
     `init_final_cataloger` e `init_support_only`;
   - retirar `catalogador` do conjunto de inventarios paralelos mesmo quando
     ele estiver presente no catalogo de agentes ou em `inventory_required`;
   - registrar matriz
     `available -> inventory_required -> selected -> invoked | blocked | skipped`
     com motivo, classe de init, pasta alvo quando aplicavel e tipo de
     resultado esperado, incluindo `target_retrospective` por agente invocado;
   - se houver limite pratico ou configurado de concorrencia, executar fan-out
     em lotes conservadores; em Codex, quando nenhum limite menor for conhecido,
     usar `agents.max_threads` quando disponivel ou o default documentado de 6
     como teto inicial, registrando qualquer limite observado diferente;
   - dar a cada agente `init_inventory_domain_writer` uma pasta alvo, contrato
     de inventario, fontes permitidas, envelope de escrita exato para
     `target_inventory_dir` e forbidden writes;
   - exigir que cada agente `init_inventory_domain_writer` escreva dentro do
     proprio `target_inventory_dir`; se nao houver conteudo util, o agente deve
     escrever falha estruturada dentro desse mesmo diretorio;
   - dar a cada agente `init_support_only`, quando invocado, fontes permitidas e
     forbidden writes, sem documento alvo obrigatorio;
   - dar a todo agente invocado o comando de retrospectiva, o
     `target_retrospective` exato, allowed write exclusivo para esse arquivo e
     instrucao para registrar atritos materiais antes de encerrar;
   - exigir que todo agente invocado execute `loki:retrospectiva-tecnica` sobre
     a propria execucao e escreva o proprio `target_retrospective`;
   - fechar ou liberar agentes concluidos antes de abrir novo lote quando o
     runtime exigir capacidade limitada;
   - nenhum agente escreve no mesmo arquivo que outro.
5. Consolidacao serial:
   - validar existencia de `target_inventory_dir` para cada
     `init_inventory_domain_writer` selecionado;
   - validar que cada `target_inventory_dir` cobre o conteudo minimo aplicavel
     de `docs/loki-init-inventory-contracts.md`;
   - validar existencia de `target_retrospective` escrito por cada agente
     invocado;
   - invocar `catalogador` uma vez como `init_final_cataloger`, usando as pastas
     de inventario validadas como fontes e somente os destinos exatos de
     catalogacao declarados no proprio envelope;
   - consolidar conflitos e lacunas em
     `docs/loki-init/conflicts-and-decisions.md` e
     `docs/loki-init/open-questions.md`;
   - atualizar `docs/index.xml`;
   - atualizar `planos/000-init-loki/tasks.md`;
   - recomendar o proximo comando Loki adequado.

## Agent Init Envelope

Cada agente `init_inventory_domain_writer` selecionado recebe um envelope com
este formato minimo:


```yaml
agent_init_envelope:
  agent: "<agent-name>"
  project_tags: []
  selection_reason: []
  init_class: "init_inventory_domain_writer"
  target_inventory_dir: "docs/loki-init/<agent-name>/"
  inventory_contract: "docs/loki-init-inventory-contracts.md"
  target_retrospective: "planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md"
  allowed_writes:
    - "docs/loki-init/<agent-name>/**"
    - "planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md"
  allowed_sources:
    - "docs/loki-init/project-inventory.md"
    - "docs/loki-init/technology-context.md"
    - "docs/index.xml"
    - "<agent-specific-source>"
  forbidden_writes:
    - ".agents/**"
    - ".codex/**"
    - ".claude/**"
    - "AGENTS.md"
    - "CLAUDE.md"
    - "<consumer_runtime_surfaces>"
  completion_retrospective:
    command: "loki:retrospectiva-tecnica"
    required: true
    timing: "after assigned work and before agent completion"
    source_scope:
      - "own execution trace"
      - "own target_inventory_dir or structured support result"
      - "own validations, blockers, useful and bad inferences, tool friction and residual risks"
  write_mode:
    final_artifacts: "direct-target-inventory-dir"
    retrospective: "direct-target-retrospective"
```

Agentes `init_support_only` invocados recebem envelope sem
`target_inventory_dir` e com
`write_mode.final_artifacts: "structured-support-result-only"`, mas recebem
`target_retrospective`, `completion_retrospective` e allowed write exclusivo
para a propria retrospectiva.

`catalogador` recebe envelope de `init_final_cataloger` somente na consolidacao
serial. Esse envelope deve listar as pastas de inventario validadas em
`allowed_sources`, declarar destinos de catalogacao exatos em `allowed_writes` e
manter o proprio `target_retrospective`.

## Output Contracts

Pasta de inventario de agente `init_inventory_domain_writer`:

- `target_inventory_dir` em `docs/loki-init/<agent-name>/`;
- conteudo minimo universal e por especialidade definido em
  `docs/loki-init-inventory-contracts.md`;
- organizacao interna livre, com um ou mais `.md`;
- fatos atuais com fontes, separados de inferencias;
- cobertura e limites do que foi lido, mapeado ou nao encontrado;
- falha estruturada dentro da propria pasta quando nao houver conteudo util.

Resultado de `init_final_cataloger`:

- catalogacao dos inventarios finais ja produzidos;
- fontes de inventario consultadas;
- destinos de catalogacao escritos ou bloqueados;
- conflitos, lacunas ou itens nao catalogados que precisem ser preservados em
  consolidacao.

Resultado estruturado de agente `init_support_only` quando invocado:

- `Status`: complete, partial ou blocked;
- `Sources Attempted`;
- `Sources Read`;
- `Evidence Map`;
- `Missing Evidence`;
- `Minimum Next Question`;
- `Do Not Assume`;
- `Context Budget Used`.

Retrospectiva por agente invocado:

- `target_retrospective` em
  `planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md`;
- objetivo do agente, resultado entregue e status;
- artefatos escritos, consultados, descartados ou bloqueados;
- validacoes feitas, nao feitas, bloqueadas ou dependentes de gate humano;
- decisoes humanas, correcoes recebidas e pendencias percebidas;
- atritos materiais de execucao, inferencias uteis e incorretas, uso de
  comandos/scripts/ferramentas e mismatches de ambiente;
- caminho minimo recomendado para uma proxima execucao equivalente;
- aprendizados reutilizaveis e candidatos para `loki:continuous-improvement`
  somente quando houver fonte, evidencia, verificacao e gate claro.

Falhas estruturadas de `init_inventory_domain_writer` devem ser escritas dentro
do proprio `target_inventory_dir`. Falhas estruturadas de `init_support_only` ou
`init_final_cataloger` devem ficar no resultado estruturado ou em build report
quando forem materiais para retomada. Falhas materiais, dificuldades e atritos
da execucao de qualquer agente invocado devem tambem ser registrados no proprio
`target_retrospective`.

## Validators

- `docs/**` e `planos/000-init-loki/**` sao os unicos writes de consumidor.
- Nenhum arquivo em runtime, assets, dados gerados, `.agents/**`, `.codex/**`,
  `.claude/**`, `AGENTS.md` ou `CLAUDE.md` foi escrito.
- `docs/loki-init/project-inventory.md` existe ou a falha estruturada esta em
  `planos/000-init-loki/builds/fase1/`.
- Contexto de tecnologia registra evidencia, confianca, `selected_project_type`
  e skills sugeridas sem hardcode de engine.
- `selected_project_type` esta em `supported_project_types` lido de
  `manifest.yaml`.
- `agent_project_tag_policy.base_tag` e `core`, e `core` nao aparece em
  `supported_project_types`.
- Todo agente em `manifest.yaml` possui `project_tags` nao vazio, e cada tag e
  `core` ou pertence a `supported_project_types`.
- Todo `codex_agents[].source_agent` em `manifest.yaml` aponta para agente
  existente.
- Agent fan-out registra preflight de capacidade, metodo de descoberta,
  catalogo de agentes usado, tipos suportados, tags por agente, agentes
  disponiveis, inventario requerido, planejados, invocados, bloqueados e
  pulados, com motivos.
- Agent fan-out registra capacidade de escrita escopada para
  `target_retrospective` por agente invocado, ou motivo de bloqueio/pulo.
- Agent fan-out registra `init_inventory_domain_writers`,
  `init_final_cataloger` e `init_support_only_agents`.
- `inventory_required` e exatamente a uniao ordenada dos agentes marcados com
  `core` e dos agentes marcados com `selected_project_type`; todo agente
  requerido esta em `selected`, `invoked`, `blocked` ou `skipped` com motivo.
- `catalogador`, quando requerido ou disponivel para catalogacao, esta em
  `init_final_cataloger`, nao em `init_inventory_domain_writers`, e nao e
  invocado no fan-out paralelo de inventarios.
- `software-development` pode selecionar somente `core` enquanto nao houver
  agentes especializados com essa tag.
- Cada agente `init_inventory_domain_writer` selecionado materializou o proprio
  `target_inventory_dir`.
- Cada `target_inventory_dir` foi validado contra
  `docs/loki-init-inventory-contracts.md`.
- `catalogador` foi invocado no maximo uma vez, somente depois da validacao das
  pastas de inventario.
- Cada agente invocado escreveu o proprio `target_retrospective` usando
  `loki:retrospectiva-tecnica`.
- Nenhum agente escreveu retrospectiva de outro agente.
- Nenhum agente `init_support_only` escreveu `docs/loki-init/**`,
  `docs/index.xml`, `planos/000-init-loki/tasks.md` ou runtime; a unica escrita
  direta permitida para `init_support_only` e o proprio `target_retrospective`.
- `docs/index.xml` foi criado ou atualizado quando documentos duradouros foram
  criados.
- `planos/000-init-loki/tasks.md` e resume state refletem status, conflitos,
  validators e proximo comando recomendado.
- Nenhum comportamento perceptivel, runtime, integracao ativa, save/load,
  gameplay, UI, audio, build ou estado persistido e declarado validado sem
  human-validation posterior.

## Human Gates

- `approval`: necessario para qualquer destino fora de `docs/**` e
  `planos/000-init-loki/**`.
- `technical-review`: necessario para alterar contrato do pacote, agentes,
  skills, templates ou validators.
- `human-validation`: necessario antes de declarar runtime, comportamento
  perceptivel, integracoes, build, gameplay, UI, audio ou estado persistido como
  validado.

## Stop Conditions

- O root do consumidor e ambiguo ou nao foi resolvido.
- A execucao exigiria escrever fora de `docs/**` ou
  `planos/000-init-loki/**`.
- Existe conflito com arquivos existentes e nao ha regra segura de merge/audit.
- O comando nao consegue produzir inventario comum minimo ou falha estruturada.
- Um agente `init_inventory_domain_writer` selecionado nao consegue escrever o
  proprio `target_inventory_dir` nem falha estruturada dentro dele.
- Um agente invocado nao consegue escrever o proprio `target_retrospective`.
- `catalogador` teria que rodar antes da validacao das pastas de inventario ou
  sem envelope de `init_final_cataloger` com fontes e writes exatos.
- O usuario pede validacao de runtime sem skill tecnica, validator e
  human-validation.

## Resume Contract

Manter `loki_init_state` em `planos/000-init-loki/tasks.md` ou em build report
equivalente com:

```yaml
loki_init_state:
  consumer_project_root: ""
  docs_root: "docs"
  plan_root: "planos/000-init-loki"
  current_phase: "fase1"
  status: ""
  created_or_audited_paths: []
  inventory:
    files_scanned: []
    files_deep_read: []
    ignored_patterns: []
    project_areas: []
    detected_project_type: []
    selected_project_type: ""
    detected_engines: []
    git_available: false
  agent_outputs: {}
  agent_fanout:
    capability_preflight: ""
    discovery_method: ""
    agent_catalog_source: []
    supported_project_types: []
    agent_project_tag_policy:
      base_tag: ""
      selection_rule: ""
    agent_project_tags: {}
    compatible_tools_found: []
    available: []
    inventory_required: []
    inventory_required_reasons: {}
    init_inventory_domain_writers: []
    init_final_cataloger: []
    init_support_only_agents: []
    selected: []
    planned: []
    invoked: []
    blocked: []
    skipped: []
    skipped_reasons: {}
    target_inventory_dirs: {}
    inventory_contracts: {}
    cataloger_outputs: {}
    target_retrospectives: {}
    retrospective_write_capability: {}
    support_outputs: {}
    retrospective_outputs: {}
    batch_limit_configured: null
    batch_limit_observed: null
    write_mode_by_agent: {}
  conflicts: []
  open_questions: []
  validators_run: []
  blocked_by: []
  next_recommended_command: ""
```
