---
name: "<namespace:command-name>"
type: command
status: draft
domain: "<domain>"
required_skills: []
execution_profile:
  model_class: "<frontier_reasoning|coding|generalist|long_context|fast_low_cost|specialist_generalist_human_like>"
  default_effort: "<low|medium|high>"
  max_effort: "<medium|high|xhigh>"
  escalation_signals: []
  handoff_effort:
    research: "<low|medium|high>"
    coding: "<medium|high>"
    documentation_transient: "<low|medium>"
    documentation_durable: "<high>"
    validator: "<low|medium>"
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# <namespace:command-name>

## Purpose

<Resultado esperado em uma frase.>

## Inputs

- <Entrada obrigatoria 1>
- <Entrada opcional ou contextual>

## Outputs

- <Artefato, decisao ou proposta produzida>

## Allowed Writes

- <Paths ou superficies permitidas>

## Forbidden Writes

- `.claude/**`
- `.agents/**`
- `.codex/**`
- <Paths ou superficies proibidas>

## Required Skills

- <Skill obrigatoria quando aplicavel>

## Execution Profile

- `model_class`: <classe provider-neutral de `docs/model-effort-guidance.md`>
- `default_effort`: <effort normal do comando>
- `max_effort`: <maior effort permitido por sinais de escalamento>
- `escalation_signals`: <quando subir effort/model class>
- `handoff_effort`: <effort esperado por tipo de handoff>
- `adapter_projection`: <como Codex, Claude Code ou outro adaptador deve tratar o metadado>

Contratos canonicos devem preferir classes e effort a IDs fixos de modelo.

## Handoffs

- <Agente ou subprocesso em read-only/proposal-only>

## Validators

- <Check automatico exigido>

## Human Gates

- <interview | approval | runtime-validation | technical-review | domain-approval | visual-ux-confirmation>

## Packaging Checks

- <Se o comando fizer parte do pacote, declarar namespace, impacto em manifest/docs e validacoes de estrutura/autocontencao.>

## Stop Conditions

- <Situacao que pausa ou encerra a execucao>

## Resume Contract

<Onde salvar estado, pergunta pendente, arquivos afetados, validacoes e proximo passo.>
