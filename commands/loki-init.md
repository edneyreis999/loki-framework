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
- `<technology_required_skills>` somente quando o inventario ou o usuario
  declararem uma tecnologia especifica.
- `loki-retrospectiva-tecnica` para retrospectiva por agente selecionado.

## Workflow

1. Preflight e escopo:
   - confirmar `consumer_project_root`, `docs_root` e `plan_root`;
   - declarar allowed writes e forbidden writes;
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
   - registrar evidencia, confianca, skills tecnicas sugeridas, superficies
     sensiveis, validators e human gates;
   - produzir `docs/loki-init/technology-context.md` ou
     `docs/loki-init/engine-context.md`.
4. Fan-out paralelo por `agent_init_envelope`:
   - selecionar agentes por perfil detectado, nao por hardcode de engine;
   - dar a cada agente um documento alvo, inventario alvo, retrospectiva alvo,
     fontes permitidas, budget e forbidden writes;
   - agentes atuais permanecem `read-only` ou `proposal-only`; quando o runtime
     nao permitir escrita, eles retornam conteudo estruturado e o orquestrador
     grava nos allowed writes;
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
  write_mode: "proposal-only-or-orchestrator-write"
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
- Contexto de tecnologia registra evidencia, confianca e skills sugeridas sem
  hardcode de engine.
- Cada agente selecionado tem documento, inventario e retrospectiva, ou falha
  estruturada equivalente.
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
    detected_engines: []
    git_available: false
  agent_outputs: {}
  agent_inventories: {}
  agent_retrospectives: {}
  conflicts: []
  open_questions: []
  validators_run: []
  blocked_by: []
  next_recommended_command: ""
```
