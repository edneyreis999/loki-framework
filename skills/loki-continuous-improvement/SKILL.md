---
name: loki-continuous-improvement
description: Run the Loki `loki-continuous-improvement` command bundle in Codex. Promote validated retrospective learnings into the correct durable consumer or package surface through capability-aware digestion, evidence classification, root-cause analysis, normative gates, serial writes, verification, or evidence-backed backlog.
when_to_use:
  - "Use when validated retrospective learnings may belong in consumer docs, routing context, reusable skills, commands, agents, templates, validators, package policy, manifest, or backlog."
  - "Use when multiple retrospectives require capability preflight, read-only digests, deduplication, root-cause boundaries, evidence classification, normative approval, and resumable candidates."
argument-hint: "[retrospective_source or analytic_inference_sources, optional interactions, builds, target_surface, package_root, scope]"
arguments:
  required: []
  optional:
    - learning_sources
    - retrospective_source
    - interactions
    - builds
    - analytic_inference_sources
    - target_surface
    - package_root
    - scope
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - durable package policy promotion
  - command, skill, agent, template, validator, or manifest changes
  - broad normative change with cross-adapter impact
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-continuous-improvement/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: continuous-improvement
required_skills:
  - lf-command-creator
  - lf-agent-creator
  - lf-skill-creator
required_commands:
  - loki-retrospectiva-tecnica
status: draft
used_by:
  - loki-continuous-improvement
---

# loki-continuous-improvement

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: learning_sources
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Retrospectivas, audits, completion/evidence manifests e execution-knowledge entries validadas com lineage; sem promocao direta.
  - key: retrospective_source
    input_type: path[file_or_directory] | list[path[file]]
    requirement: conditional
    default: null
    description: Retrospectiva técnica, diretório ou lista de retrospectivas concluídas, pausadas claramente ou relativas a dificuldade realmente resolvida; obrigatória quando nenhuma fonte especializada de inferência for fornecida.
  - key: analytic_inference_sources
    input_type: list[path[file] | mapping]
    requirement: conditional
    default: []
    description: Relatórios persistidos de deep analysis com inference_events/generated_candidates ou retrospectivas com analytic_inference_candidates; cada item entra unreviewed e sem autorização de mutação.
  - key: interactions
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Decisões humanas, approvals, defaults e rejeições que delimitam promoção e escopo.
  - key: builds
    input_type: list[path_or_mapping]
    requirement: optional
    default: []
    description: Builds, validators, tasks, diffs e validações humanas usados apenas como evidência transitória.
  - key: target_surface
    input_type: path_or_artifact_type
    requirement: optional
    default: null
    description: Superfície duradoura candidata; é hipótese a classificar, não autorização de escrita.
  - key: package_root
    input_type: path[directory]
    requirement: optional
    default: null
    description: Raiz do pacote quando o candidato puder afetar artefato Loki consolidado.
  - key: scope
    input_type: string_or_mapping
    requirement: optional
    default: null
    description: Escopo positivo, limites, fora de escopo e restrições da melhoria.
```

Exija pelo menos uma fonte em `retrospective_source` ou
`analytic_inference_sources`. Quando presente, valide que
`retrospective_source` resolve apenas arquivos legíveis de retrospectiva ou um
diretório legível enumerável. Valide que cada `analytic_inference_source` é um
relatório persistido de deep analysis ou retrospectiva com locator exato e
bloco especializado reconhecível. Valide existência de paths em
`learning_sources`, `analytic_inference_sources`, `interactions`, `builds` e `package_root`, tipos das
mappings e compatibilidade
entre `scope` e `target_surface`. Rejeite fontes ainda em execução, dificuldades
não resolvidas, destinos transitórios tratados como normativos e qualquer path
fora do escopo, explicando como corrigir.

Mantenha `package_root` e o `consumer_root` interno distintos: o primeiro limita contratos,
schemas, scripts, policy e docs do pacote; o segundo é resolvido do `pwd` canônico e ancora exclusivamente
`destination_scope: consumer-operational-state` no layout fixo
`<consumer_root>/.loki/analytic-inference/v2`. O estado vivo usa
`registry.xml`, indices `index.xml`, records `rev-N.xml` e events `.xml`. Exija que o command seja iniciado
na raiz do consumidor; não aceite parâmetro de root, metadata de adapter, Git,
ambiente, fontes ou descoberta de `.loki` como override.

O unico layout de catalogo suportado e XML v2; JSON nao e destino ativo,
fallback de lookup ou alvo de mutacao deste command.

Identifique e solicite cada informação obrigatória ausente. Não invente fonte,
evidência, escopo, destino, classificação, causa, approval ou gate; não avance
enquanto a lacuna impedir avaliação segura.

Quando houver fonte especializada, carregue condicionalmente
[lf-analytic-inference](../lf-analytic-inference/SKILL.md) e valide schema v1,
status exatamente `unreviewed`, identidade, capture/lineage, provenance e
locator antes de qualquer intake. Relatório ou retrospectiva sem item material
é uma fonte válida somente quando registra lista vazia e motivo não vazio.

Execution-knowledge entries são fontes adicionais: valide schema, lineage,
sanitização e promotion status não aplicado. Elas não substituem a
retrospectiva elegível, análise de causa raiz nem gates.

Normalize objetivo, parâmetros, fontes, evidências transitórias, erro observado
quando aplicável, atritos de execução, escopo, restrições, destino candidato,
allowed/forbidden writes, approvals, gates, lacunas e, quando aplicável, os
locators e tipos das fontes especializadas, roots canônicas e suas fontes. Durante Input não faça
digests, pesquisa, classificação, proposta, promoção, escrita nem declaração de
sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referências adicionais que esse arquivo ordenar.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
