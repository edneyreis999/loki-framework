---
name: loki:init
type: command
status: draft
domain: consumer-bootstrap
aliases:
  - init-loki
required_skills:
  - loki-init
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
- `docs/loki-init/<perspective>-context.md`.
- `docs/loki-init/inventories/<agent-name>-inventory.md`.

Estado operacional permitido:

- `planos/000-init-loki/tasks.md`.
- `planos/000-init-loki/task-1.1.md` quando o init materializar tasks.
- `planos/000-init-loki/interaction/fase1/**`.
- `planos/000-init-loki/builds/fase1/**`.
- `planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md`.

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
- `loki-index-navigator` quando `docs/index.xml` existir e precisar ser lido.
- `<technology_required_skills>` somente quando o inventario, o usuario ou um
  agente especialista declararem uma tecnologia especifica.
- `loki-retrospectiva-tecnica` para retrospectiva por agente selecionado.

## Workflow

1. Preflight e escopo:
   - confirmar `consumer_project_root`, `docs_root` e `plan_root`;
   - declarar allowed writes e forbidden writes;
   - quando o workflow selecionar agent fan-out, declarar explicitamente a
     intencao de usar subagents/delegacao e executar preflight de capacidade
     antes de declarar agentes indisponiveis;
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
     `retrospetivas/fase1`;
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
   - registrar matriz
     `available -> inventory_required -> selected -> invoked | blocked | skipped`
     com motivo, documento alvo, inventario alvo e retrospectiva alvo;
   - se houver limite pratico ou configurado de concorrencia, executar fan-out
     em lotes conservadores; em Codex, quando nenhum limite menor for conhecido,
     usar `agents.max_threads` quando disponivel ou o default documentado de 6
     como teto inicial, registrando qualquer limite observado diferente;
   - dar a cada agente um documento alvo, inventario alvo, retrospectiva alvo,
     fontes permitidas, budget e forbidden writes;
   - agentes atuais permanecem `read-only` ou `proposal-only`; quando o runtime
     nao permitir escrita em documentos finais ou inventarios, eles retornam
     conteudo estruturado e o orquestrador grava nos allowed writes;
   - quando o workflow exigir retrospectiva tecnica por agente, permitir que
     cada agente escreva somente o proprio `target_retrospective` no diretorio
     de retrospectivas da fase ativa; se o runtime nao suportar essa excecao,
     exigir `retrospective_handoff` e registrar a limitacao;
   - fechar ou liberar agentes concluidos antes de abrir novo lote quando o
     runtime exigir capacidade limitada;
   - nenhum agente escreve no mesmo arquivo que outro.
5. Retrospectiva por agente:
   - apos documento e inventario ou falha estruturada, cada agente selecionado
     deve produzir retrospectiva em
     `planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md`;
   - a retrospectiva registra fontes lidas, validadores, atritos, lacunas,
     limites de contexto, decisoes e riscos.
6. Consolidacao serial:
   - validar existencia de documentos, inventarios e retrospectivas;
   - consolidar conflitos e lacunas em
     `docs/loki-init/conflicts-and-decisions.md` e
     `docs/loki-init/open-questions.md`;
   - atualizar `docs/index.xml`;
   - atualizar `planos/000-init-loki/tasks.md`;
   - recomendar o proximo comando Loki adequado.

## Agent Init Envelope

Cada agente selecionado recebe um envelope com este formato minimo:

```yaml
agent_init_envelope:
  agent: "<agent-name>"
  purpose: ""
  project_tags: []
  selection_reason: []
  target_document: "docs/loki-init/<perspective>-context.md"
  target_inventory: "docs/loki-init/inventories/<agent-name>-inventory.md"
  target_retrospective: "planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md"
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
  context_budget:
    max_files_per_agent: 0
    max_lines_per_agent_artifact: 0
    max_deep_read_bytes_per_agent: 0
  write_mode:
    final_artifacts: "proposal-only-or-orchestrator-write"
    retrospective: "direct-target-retrospective-or-retrospective-handoff"
```

## Output Contracts

Documento por agente:

- titulo, agente, escopo, status e data;
- fatos com fontes;
- inferencias separadas de hipoteses;
- areas ou dominios cobertos;
- lacunas e `Do Not Assume`;
- validadores recomendados;
- `Context Budget Used`.

Inventario por agente:

- `Status`: complete, partial ou blocked;
- `Sources Attempted`;
- `Sources Read`;
- `Evidence Map`;
- `Missing Evidence`;
- `Minimum Next Question`;
- `Do Not Assume`;
- `Context Budget Used`.

Retrospectiva por agente:

- objetivo e resultado;
- documentos e inventarios produzidos ou falha estruturada;
- validadores executados, nao aplicaveis ou pendentes;
- decisoes e gates humanos;
- atritos, limites de contexto e aprendizados;
- riscos residuais e proximo passo.

Falhas estruturadas sao artefatos validos quando um agente nao conseguir gerar
conteudo util, mas nunca podem desaparecer silenciosamente.

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
- `inventory_required` e exatamente a uniao ordenada dos agentes marcados com
  `core` e dos agentes marcados com `selected_project_type`; todo agente
  requerido esta em `selected`, `invoked`, `blocked` ou `skipped` com motivo.
- `software-development` pode selecionar somente `core` enquanto nao houver
  agentes especializados com essa tag.
- Cada agente selecionado tem documento, inventario e retrospectiva, ou falha
  estruturada equivalente.
- Retrospectivas escritas por agentes `proposal-only` ficam restritas ao
  `target_retrospective` exato sob `planos/000-init-loki/retrospetivas/fase1/`.
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
- Um agente selecionado nao retorna documento, inventario, retrospectiva ou
  falha estruturada.
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
  agent_inventories: {}
  agent_retrospectives: {}
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
    selected: []
    planned: []
    invoked: []
    blocked: []
    skipped: []
    skipped_reasons: {}
    target_documents: {}
    target_inventories: {}
    target_retrospectives: {}
    batch_limit_configured: null
    batch_limit_observed: null
    write_mode_by_agent: {}
  conflicts: []
  open_questions: []
  validators_run: []
  blocked_by: []
  next_recommended_command: ""
```
