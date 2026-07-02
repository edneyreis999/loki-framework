# VisuStella Battle Mechanics Checklist

Use this checklist before designing, reviewing, or debugging VisuStella MZ
battle mechanics.

## Preflight

- Confirm RPG Maker MZ project evidence and active VisuStella plugin list.
- Confirm the owning battle plugin or family; if unclear, use
  `rpg-maker-mz-visustella-plugin-index`.
- Confirm plugin tier, dependency, and load order when behavior depends on
  Battle Core, ATB, TP, AI, aggro, visual states, or Action Sequence extensions.
- Confirm the requested operation: lookup, design review, diagnosis, data write,
  Plugin Manager change, or runtime validation.

## Surface Checks

### Damage, Criticals, And Targeting

- Identify whether the change belongs to a Plugin Manager parameter, notetag,
  formula, target scope, Action Sequence command, or vanilla RPG Maker MZ field.
- For damage/heal/effect-applying Action Sequences, verify
  `MECH: Action Effect` or an explicit equivalent.
- Confirm target scope, target loop, random/current/next target behavior, and
  cleanup before declaring sequence flow coherent.

### Skills, States, Passives, Aura, And Miasma

- Confirm target object type: skill, item, actor, class, enemy, state, weapon,
  armor, troop, or trait-bearing object.
- Use `rpg-maker-mz-visustella-notetags` for tag syntax and target support.
- Check passive state cache assumptions, unlock conditions, state category,
  reapply behavior, turn handling, aura/miasma range, dead-state behavior, and
  slip damage/healing timing.

### ATB And TP

- Confirm the battle system mode and whether the project uses TPB/ATB behavior.
- Check ATB speed, interrupt rules, cast behavior, field gauge, gauge color,
  skill/item speed, actor/enemy/system commands, TP modes, and TP gain formula.
- Use parameters for global settings and notetags/plugin commands for object or
  event-specific overrides.

### Battle AI And Aggro

- For AI, confirm AI style, AI level, rating variance, skill conditions, target
  conditions, and TGR weighting.
- For aggro, check priority order: provoke/taunt/aggro when applicable.
- Confirm actor/enemy command payloads before changing aggro, TP, ATB, state
  turns, skill costs, or battle resources in events.

### Battle UI And Visuals

- Check Battle Core layout, command windows, battle log, HP/status gauges,
  state overlays, response popups, motion, tone, opacity, hover/breathing, and
  sideview/DragonBones dependencies.
- Treat visual state effects, camera, impact, inject, audio, motion, and timing
  as runtime-pending until Playtest.

## Write Gate Mapping

| Target | Required Gate |
| --- | --- |
| database objects, note fields, skills, items, enemies, states, troops, Common Events, event command lists | `rpg-maker-mz-data-json` |
| plugin parameters, plugin files, plugin metadata, PluginManager integration, activation, load order, `js/plugins.js` | `rpg-maker-mz-plugin-workflow` |
| active plugin list, plugin order, object IDs, callers, Common Event ownership | `rpg-maker-mz-project-inventory` |
| battle behavior, timing, damage, AI choices, target loops, visuals, audio, input | Playtest or another approved human validation gate |

## Stop Conditions

- Plugin ownership or active order is unknown and affects the answer.
- The task asks for a write but no target file, object ID, gate, or task
  authorization exists.
- A runtime claim is needed but no Playtest or human validation gate exists.
- The proposed fix relies only on vanilla RPG Maker MZ source while active
  VisuStella battle plugins may override the behavior.
