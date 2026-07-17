---
name: loki-init
description: Run the Loki `loki-init` command bundle in Codex. Bootstrap, refresh or audit consumer documentation through read-only investigators, accepted research packets, serial catalogador bootstrap/publication/reconciliation, resumable planos/000-init-loki state, evidence, validators, gates, and strict write boundaries.
when_to_use:
  - "Use when bootstrapping or auditing Loki consumer documentation and planos/000-init-loki state."
  - "Use when initialization requires project classification, resumable investigator fan-out, packet acceptance, serial catalogador publication, terminal coverage, completion records, evidence capture, validators, and resumable state without touching consumer runtime."
argument-hint: "[consumer_project_root, docs_root, plan_root, mode, engine_hint, project_type_hint, max_scan_depth, include_patterns, exclude_patterns]"
arguments:
  required: []
  optional:
    - consumer_project_root
    - docs_root
    - plan_root
    - mode
    - engine_hint
    - project_type_hint
    - max_scan_depth
    - include_patterns
    - exclude_patterns
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to command frontmatter where supported."
escalation_signals:
  - consumer documentation bootstrap
  - resumable investigator fan-out and serial catalogador publication
  - consumer write boundary ambiguity
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-init/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: consumer-bootstrap
aliases:
  - init-loki
required_skills: []
required_commands: []
status: draft
used_by:
  - loki-init
---

# loki-init

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: consumer_project_root
    input_type: path[directory]
    requirement: optional
    default: "."
    description: Raiz existente e legivel do projeto consumidor; o diretorio atual e o default.
  - key: docs_root
    input_type: relative_path[directory]
    requirement: optional
    default: "docs"
    description: Destino de documentacao dentro do projeto consumidor.
  - key: plan_root
    input_type: relative_path[directory]
    requirement: optional
    default: "planos/000-init-loki"
    description: Destino do estado operacional retomavel dentro do projeto consumidor.
  - key: mode
    input_type: enum_or_agent_mode
    requirement: optional
    default: "full-init"
    description: full-init, refresh-docs, audit-only ou agent-only:<agent-name>.
  - key: engine_hint
    input_type: string
    requirement: optional
    default: null
    description: Tecnologia ou engine sugerida, tratada como hint e nao como fato.
  - key: project_type_hint
    input_type: string
    requirement: optional
    default: null
    description: Tipo de projeto candidato, validado contra supported_project_types do manifest.
  - key: max_scan_depth
    input_type: integer
    requirement: optional
    default: null
    description: Profundidade maxima positiva para descoberta; null usa limite seguro inferido sem ampliar escopo.
  - key: include_patterns
    input_type: list[glob]
    requirement: optional
    default: []
    description: Patterns adicionais permitidos na descoberta local.
  - key: exclude_patterns
    input_type: list[glob]
    requirement: optional
    default: []
    description: Patterns a excluir, incluindo binarios, gerados e arquivos grandes quando aplicavel.
```

Resolva `consumer_project_root` como diretório existente e legível. Normalize
`docs_root` e `plan_root` sem travessia, symlink divergente ou escape da raiz;
eles devem resolver respectivamente dentro de `docs/**` e
`planos/000-init-loki/**`. Valide `mode`, inteiro positivo para
`max_scan_depth`, listas de globs e ausência de conflito entre includes e
excludes. Trate hints como hipóteses e valide `project_type_hint` posteriormente
contra o manifest. Se diretórios já existirem, selecione merge/audit e proíba
sobrescrita silenciosa.

Rejeite entrada inválida com correção acionável. Como não há parâmetro
obrigatório sem default, peça informação somente quando ambiguidade de root,
destino, modo ou conflito impedir execução segura; não invente path, tecnologia,
tipo, approval ou escopo.

Normalize objetivo, parâmetros, roots resolvidos, modo, hints, filtros, escopo,
restrições, destinos, `allowed_writes`, `forbidden_writes`, approvals, gates e
lacunas para Execution. Durante Input não faça inventário, fan-out, pesquisa,
criação/auditoria de docs, alteração de arquivos nem declaração de sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referências adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
