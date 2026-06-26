---
name: loki-rpg-maker-mz-plugin-workflow
description: Reference the required RPG Maker MZ plugin workflow for creating, editing, validating, or activating plugins under `js/plugins`, including helper plugins, plugin metadata, PluginManager integration, plugin commands, `plugins.js`, syntax checks, and activation gates.
when_to_use:
  - "Use when creating, editing, validating, or activating RPG Maker MZ plugins under js/plugins or js/plugins.js."
  - "Use when plugin metadata, PluginManager integration, plugin commands, syntax checks, activation review, or playtest gates are required."
argument-hint: "[plugin goal, plugin file, parameters, activation need]"
arguments:
  required: []
  optional:
    - plugin_goal
    - plugin_file
    - parameters
    - activation_need
disable-model-invocation: false
user-invocable: false
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: coding
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - plugin activation or runtime behavior is affected
  - integration touches PluginManager or plugin commands
  - playtest gate is required
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-rpg-maker-mz-plugin-workflow/SKILL.md"
shell: {}
type: skill-dependency
status: reference
source_policy: dependency-reference-not-copy
---

# loki-rpg-maker-mz-plugin-workflow

## Role In Loki

Dependencia obrigatoria para criar, editar, validar ou ativar plugins RPG Maker MZ em `js/plugins/` e `js/plugins.js` no projeto consumidor.

## Inputs

- Objetivo do plugin ou patch.
- Arquivo plugin alvo.
- Parametros ou plugin commands.
- Necessidade de ativacao.

## Outputs Expected By Loki

- Plugin helper ou proposta de alteracao.
- Header RPG Maker MZ minimo quando aplicavel.
- Evidencia de `node -c`.
- Instrucao de ativacao ou alteracao controlada em `plugins.js`.
- Gate de Playtest quando plugin ativo afetar runtime.

## Allowed Writes

Nenhuma escrita e autorizada por este arquivo. A permissao real vem da task ativa, da skill instalada no ambiente e dos gates do plano.

## Forbidden Writes

- Patch direto em `rmmz_*.js` como default.
- Ativacao silenciosa sem approval.
- Validar comportamento de plugin sem Playtest quando runtime for afetado.

## Gates

- `node -c`
- `plugin-header-check`
- `activation-review`
- `playtest` para plugin ativo.

## Source Boundary

Este arquivo declara o contrato minimo esperado da skill no pacote Loki. Ele nao depende de uma copia local em `.agents/` para ser entendido.
