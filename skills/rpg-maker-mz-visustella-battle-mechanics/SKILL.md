---
name: rpg-maker-mz-visustella-battle-mechanics
description: Use when designing, reviewing, or debugging VisuStella MZ battle mechanics beyond vanilla RPG Maker MZ, including Battle Core, Skills and States Core, Auto Skill Trigger, Life State Effects, Visual State Effects, ATB, TP modes, Battle AI, Aggro, targeting, damage styles, criticals, gauges, passive states, slip damage, auras, miasmas, and battle UI behavior.
when_to_use:
  - "Use for VisuStella MZ battle mechanics that are not explained by vanilla RPG Maker MZ alone."
  - "Use when the task mentions Battle Core, Skills and States Core, Auto Skill Trigger, Life State Effects, Visual State Effects, ATB, TP modes, Battle AI, Aggro, targeting, damage styles, criticals, gauges, passive states, slip damage, auras, miasmas, or battle UI behavior."
  - "Use with the MVP VisuStella surface skills when a battle task touches Plugin Manager parameters, notetags, plugin commands, or Action Sequences."
argument-hint: "[project_root, plugin_name, battle_surface, intended_change]"
arguments:
  required: []
  optional:
    - project_root
    - plugin_name
    - battle_surface
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
  - battle behavior differs from vanilla RPG Maker MZ
  - battle plugin tier, dependency, or load order affects the answer
  - damage, target selection, state behavior, AI, ATB, TP, aggro, or battle UI must be validated
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-battle-mechanics/SKILL.md"
  references:
    battle_plugin_map: "references/battle-plugin-map.md"
    battle_mechanics_checklist: "references/battle-mechanics-checklist.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-battle-mechanics

## Purpose

Guide RPG Maker MZ work involving VisuStella MZ battle mechanics and battle UI
behavior. This skill routes battle-domain questions to the smallest relevant
VisuStella surface skill and domain reference.

This skill is semantic guidance only. It does not authorize writes to consumer
RPG Maker MZ data, plugin files, Plugin Manager configuration, assets, save
state, generated files, or runtime surfaces.

## Procedure

1. Confirm the work is RPG Maker MZ and that VisuStella battle plugins are
   installed, named, or likely relevant. Use `rpg-maker-mz-project-inventory`
   when active plugins, plugin order, database IDs, Common Events, troop events,
   or runtime ownership are unknown.
2. Identify the battle surface: damage/critical/targeting, Action Sequence,
   skill/state behavior, passive state, aura/miasma, slip damage/healing,
   life/death state effect, visual state effect, ATB, TP mode, Battle AI,
   aggro/provoke/taunt, element/status menu, battle layout, gauge, or battle UI.
3. Read `references/battle-plugin-map.md` to narrow the plugin family, tier,
   dependency, and likely surface skill.
4. Read `references/battle-mechanics-checklist.md` before proposing,
   reviewing, or debugging a battle mechanic.
5. Load the smallest MVP VisuStella skill needed for the actual surface:
   - `rpg-maker-mz-visustella-plugin-parameters` for Plugin Manager defaults,
     battle windows, gauges, formulas, ATB/TP settings, AI defaults, aggro
     settings, or visual defaults;
   - `rpg-maker-mz-visustella-notetags` for actor, class, skill, item, weapon,
     armor, enemy, state, troop, or battle note/comment syntax;
   - `rpg-maker-mz-visustella-plugin-commands` for event, troop, Common Event,
     ATB, aggro, TP, state-turn, skill-cost, actor/enemy, or battle runtime
     commands;
   - `rpg-maker-mz-visustella-action-sequences` for Battle Core Action
     Sequences, `<Custom Action Sequence>`, Common Event sequence commands,
     `MECH: Action Effect`, camera, impact, inject, projectile, or target loops;
   - `rpg-maker-mz-visustella-compat-diagnostics` when the symptom may be tier,
     dependency, plugin order, compatibility, missing effect, or performance.
6. Use `rpg-maker-mz-data-json` before any write to `data/*.json`, database
   objects, skills, items, enemies, troops, states, Common Events, maps, event
   command lists, or note fields.
7. Use `rpg-maker-mz-plugin-workflow` before any write to plugin files,
   PluginManager integration, plugin metadata, plugin parameters, activation,
   load order, or `js/plugins.js`.
8. Require Playtest or another approved human validation gate before declaring
   battle behavior, damage, target selection, state effects, AI decisions, ATB
   timing, TP gain, aggro priority, visual state effects, battle UI, camera, or
   Action Sequence playback validated.

## Inputs

- RPG Maker MZ project evidence or project root.
- VisuStella battle plugin name, family, mechanic, symptom, or intended change.
- Affected database object, troop, Common Event, action sequence, plugin
  parameter, command payload, or runtime behavior.

## Outputs

- Battle plugin or mechanic route.
- Required MVP surface skill and RPG Maker MZ write gate.
- Checklist result for mechanic, target, formula, gauge, AI, aggro, ATB/TP,
  state, passive, visual, or UI concerns.
- Runtime validation status and Playtest requirement when behavior is
  perceptible.

## References

- Read [battle-plugin-map.md](references/battle-plugin-map.md) for battle
  plugin families, tiers, dependencies, surfaces, and routing.
- Read [battle-mechanics-checklist.md](references/battle-mechanics-checklist.md)
  before designing, reviewing, or debugging battle mechanics.

## Limits

- Do not duplicate full Action Sequence instructions; use
  `rpg-maker-mz-visustella-action-sequences`.
- Do not turn battle design tuning into a package-wide rule for every consumer
  project.
- Do not edit `data/*.json`, plugin files, Plugin Manager values, assets, or
  `js/plugins.js` from this skill alone.
- Do not validate battle behavior without Playtest or another approved human
  validation gate.
