---
name: rpg-maker-mz-visustella-progression-economy
description: Use when designing, reviewing, or debugging VisuStella MZ progression, economy, items, equipment, skills, shops, currencies, AP/SP, equip passives, skill learning, skill shops, More Currencies, Database Inherit, Items and Equips Core, trait sets, costs, requirements, shop visibility, or inheritance between RPG Maker MZ database objects.
when_to_use:
  - "Use for VisuStella MZ progression, economy, items, equipment, skill learning, skill shops, currencies, AP/SP, equip passives, costs, requirements, shop visibility, and database inheritance."
  - "Use when the task mentions More Currencies, Database Inherit, Items and Equips Core, Skill Learn System, Skill Shop, Equip Passive System, trait sets, cost notetags, requirements, or shop visibility."
  - "Use with rpg-maker-mz-data-json before writing RPG Maker MZ database objects or event data."
argument-hint: "[project_root, plugin_name, economy_surface, intended_change]"
arguments:
  required: []
  optional:
    - project_root
    - plugin_name
    - economy_surface
    - intended_change
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - costs, requirements, inheritance, currencies, or shop visibility affect multiple database objects
  - AP/SP, equip passives, skill learn, skill shop, or More Currencies behavior requires runtime validation
  - the task may touch data JSON, plugin parameters, or plugin command payloads
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-progression-economy/SKILL.md"
  references:
    progression_economy_plugin_map: "references/progression-economy-plugin-map.md"
    progression_economy_checklist: "references/progression-economy-checklist.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-progression-economy

## Purpose

Guide RPG Maker MZ work involving VisuStella MZ progression and economy
systems. This skill covers AP/SP, skill learning, skill shops, equip passives,
multiple currencies, item/equipment/shop behavior, trait sets, costs,
requirements, visibility rules, and database inheritance.

This skill is semantic guidance only. It does not authorize writes to consumer
RPG Maker MZ data, plugin files, Plugin Manager configuration, save state, or
runtime surfaces.

## Procedure

1. Confirm the work is RPG Maker MZ and that VisuStella progression/economy
   plugins are installed, named, or likely relevant. Use
   `rpg-maker-mz-project-inventory` when active plugins, object IDs, shop
   callers, Common Events, or plugin order are unknown.
2. Identify the progression/economy surface: AP, SP, skill learn, skill shop,
   equip passive, state-based passive, More Currencies cost/proxy, item/equip
   access, shop status, trait set, Database Inherit, cost formula, requirement,
   show/hide condition, or plugin command.
3. Read `references/progression-economy-plugin-map.md` to narrow the plugin
   family and likely MVP surface skill.
4. Read `references/progression-economy-checklist.md` before proposing,
   reviewing, or debugging a progression/economy change.
5. Load the smallest MVP VisuStella skill needed:
   - `rpg-maker-mz-visustella-plugin-parameters` for global defaults, windows,
     vocabulary, AP/SP settings, shop settings, currency listing, inheritance
     defaults, or item/equip menu settings;
   - `rpg-maker-mz-visustella-notetags` for costs, requirements, visibility,
     inheritance, passive setup, learnable skills, AP/SP, currencies, shops, or
     item/equip database syntax;
   - `rpg-maker-mz-visustella-plugin-commands` for AP/SP changes, shop opening,
     passive learning, actor/equip commands, purify commands, or shop commands;
   - `rpg-maker-mz-visustella-compat-diagnostics` when behavior may depend on
     tier, dependency, plugin order, inheritance timing, missing tags, or plugin
     conflict.
6. Use `rpg-maker-mz-data-json` before any write to `data/*.json`, database
   objects, actors, classes, skills, items, weapons, armors, states, enemies,
   events, shops, Common Events, note fields, or event command lists.
7. Use `rpg-maker-mz-plugin-workflow` before changing plugin files,
   PluginManager integration, plugin parameters, activation, load order, or
   `js/plugins.js`.
8. Require Playtest or another approved human validation gate before declaring
   economy behavior, shop flow, AP/SP awards, skill learning, passive unlocks,
   inheritance effects, or save/load-sensitive progression validated.

## Inputs

- RPG Maker MZ project evidence or project root.
- VisuStella plugin/family, economy surface, database object, shop/event flow,
  or symptom.
- Intended operation: lookup, design review, diagnosis, planning, or write.

## Outputs

- Progression/economy plugin route and surface classification.
- Required MVP skill and RPG Maker MZ write gate.
- Checklist result for costs, requirements, currency, AP/SP, inheritance,
  passive states, shop visibility, or item/equipment behavior.
- Runtime validation status and Playtest requirement when behavior must be
  verified in game.

## References

- Read [progression-economy-plugin-map.md](references/progression-economy-plugin-map.md)
  for plugin families, surfaces, and routing.
- Read [progression-economy-checklist.md](references/progression-economy-checklist.md)
  before designing, reviewing, or debugging progression/economy behavior.

## Limits

- Do not create consumer-specific balance sheets, prices, reward curves, or
  economy rules from this skill alone.
- Do not edit consumer database JSON or plugin configuration from this skill
  alone.
- Do not duplicate `rpg-maker-mz-data-json`; use it for structured writes.
- Do not declare progression/economy runtime behavior validated without
  Playtest or another approved human validation gate.
