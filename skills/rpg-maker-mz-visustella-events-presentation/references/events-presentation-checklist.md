# VisuStella Events And Presentation Checklist

Use this checklist before designing, reviewing, or debugging VisuStella MZ
event and presentation workflows.

## Preflight

- Confirm RPG Maker MZ project evidence and active VisuStella plugin list.
- Confirm map/event/Common Event IDs, plugin command ownership, active plugin
  order, and affected assets when relevant.
- Confirm whether the task touches event data, plugin parameters, assets,
  runtime visuals, input, options, save/load, or debug features.
- If the requested behavior is a symptom rather than a known plugin surface,
  route to `rpg-maker-mz-visustella-compat-diagnostics`.

## Event Flow Checks

- Identify event surface: map event, event page, Common Event, troop event,
  move route, page comment, switch/variable, or plugin command payload.
- For Events and Movement Core, check event template, spawn, morph, location,
  labels, icons, popups, timers, auto movement, dash, call-event, and
  region/terrain behavior separately.
- Confirm caller chain and execution context before editing Common Events or
  event command lists.

## Message, Choice, Text, And Localization Checks

- Distinguish text codes, macros, replacements, auto-color, word wrap, text
  speed, language switching, message window settings, choice settings, and
  select windows.
- Confirm whether the behavior is stored in plugin parameters or event command
  payloads.
- Treat readability, wrapping, input, and localization display as
  human-validation pending.

## Picture, Bust, And DragonBones Checks

- For Visual Novel Picture Busts, confirm picture ID, position, anchor, origin,
  graphic, expression, enter/exit, fade, move, scale, tone, tint, and animation
  flow.
- For DragonBones, confirm armature naming, battler/map sprite/picture context,
  configured settings, relevant notetag/comment tag, command payload, and asset
  availability.
- Do not treat asset presence, animation timing, or visual layering as validated
  without Playtest or another human validation gate.

## Options, Save, And Debugger Checks

- For Options Core, confirm category, option type, keyboard/gamepad binding,
  UI/audio/playtest group, and whether options should persist.
- For Save Core, confirm autosave enable/request/execute/force flow, current
  slot, save description, save picture, global switches/variables, confirmation
  window, and save style.
- For Debugger, confirm whether quick commands, Common Event launch, teleport,
  inventory, battle testing, map events, or switch/variable editing is intended
  only for playtest/debug contexts.

## Write Gate Mapping

| Target | Required Gate |
| --- | --- |
| maps, events, Common Events, event command lists, note fields, comments, database objects, `data/*.json` | `rpg-maker-mz-data-json` |
| plugin parameters, plugin files, PluginManager integration, activation, load order, `js/plugins.js` | `rpg-maker-mz-plugin-workflow` |
| active plugins, event callers, map IDs, asset ownership, save surface inventory | `rpg-maker-mz-project-inventory` |
| visuals, input, event timing, message readability, picture/bust layout, DragonBones animation, options, save/load, debugger behavior | `human-validation` or Playtest |

## Stop Conditions

- A write target, object ID, event caller, plugin command owner, or plugin
  activation state is unknown.
- The task asks for runtime proof without human-validation or Playtest.
- The change would alter assets, saves, maps, events, or plugin config without
  explicit task authorization and the relevant gate.
