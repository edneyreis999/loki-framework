# VisuStella Plugin Map

Use this reference to route broad RPG Maker MZ VisuStella work by plugin
family, tier, dependency, surface and domain. This map is intentionally concise:
it helps choose the next skill or reference, not implement the full feature.

## Global Rule

VisuStella MZ extends RPG Maker MZ through Plugin Manager parameters, notetags,
comment tags, plugin commands, runtime plugin behavior and Action Sequences.
When VisuStella is involved, do not assume vanilla RPG Maker MZ source explains
the behavior.

## Tiers And Load Order

- Core Engine is the foundation and should be treated as Tier 0.
- Battle Core and other core family plugins often sit below Core Engine and
  above their extensions.
- Higher-tier plugins usually depend on lower-tier plugins in the same family.
- When tier, dependency or load order is part of the question, route to
  `rpg-maker-mz-visustella-compat-diagnostics` once that skill exists. Until
  then, report that compatibility diagnosis is a dedicated future route and
  keep `rpg-maker-mz-plugin-workflow` as the gate for `js/plugins.js`.

## Families

| Family | Representative Plugins | Common Surfaces | Route To |
| --- | --- | --- | --- |
| Core Engine | Core Engine | base parameters, UI/menu/window settings, gold, image loading, keyboard input, basic notetags, system plugin commands, compatibility foundation | parameters, notetags, plugin commands, diagnostics |
| Battle | Battle Core, Action Sequence Camera Core, Action Sequence Impact, Skills and States Core, TP System, Active Turn Battle, Battle AI, Aggro Control, Elements Status Menu Core, Life State Effects, Visual State Effects, Auto Skill Trigger | battle parameters, battle notetags, Action Sequences, battle plugin commands, target/damage/resource/state mechanics | action-sequences, battle-mechanics, notetags, plugin commands, parameters |
| Skill Progression | Skill Learn System, Skill Shop, Equip Passive System | AP/SP, learned skills, shop visibility, costs, requirements, passive setup and unlocks | progression-economy, notetags, plugin commands, parameters |
| Gameplay And Movement | Events and Movement Core, DragonBones Union, More Currencies | map/event/page tags, movement commands, pictures/sprites, currencies, event runtime control | events-presentation, progression-economy, notetags, plugin commands |
| Narrative And Presentation | Message Core, Visual Novel Picture Busts | text codes, choices, macros, word wrap, localization, picture busts, message and picture commands | events-presentation, plugin commands, parameters |
| Quality Of Life | Database Inherit, Items and Equips Core, Options Core, Save Core, Debugger | inheritance, item/equip/shop UI, options, save/autosave, debug/export flows | progression-economy, events-presentation, diagnostics |

## Surface Signals

| User Signal | Likely Surface | Next Route |
| --- | --- | --- |
| "plugin parameter", "Plugin Manager", "default", "setting", "formula", "js/plugins.js" | Plugin Manager parameters | `rpg-maker-mz-visustella-plugin-parameters` when available; also `rpg-maker-mz-plugin-workflow` before writes |
| "notetag", "note field", "comment tag", actor/class/skill/item/enemy/state/map/event/troop note | note/comment syntax and placement | `rpg-maker-mz-visustella-notetags` when available; also `rpg-maker-mz-data-json` before writes |
| "plugin command", event command, Common Event payload, map/troop event runtime action | PluginManager command surface | `rpg-maker-mz-visustella-plugin-commands` when available; also `rpg-maker-mz-data-json` before event JSON writes |
| "Action Sequence", `<Custom Action Sequence>`, MECH, camera, impact, target loop, XML example | Battle Core Action Sequence workflow | `rpg-maker-mz-visustella-action-sequences` when available; also data JSON and Playtest gates |
| ATB, TP, Battle AI, Aggro, state visuals, passive states, criticals, gauges, targeting | battle mechanics | `rpg-maker-mz-visustella-battle-mechanics` when available |
| AP, SP, skill shop, More Currencies, Database Inherit, item/equip/shop, unlocks, requirements | progression/economy | `rpg-maker-mz-visustella-progression-economy` when available |
| message, text code, picture bust, visual novel, DragonBones, event movement, options, save, debugger | events/presentation | `rpg-maker-mz-visustella-events-presentation` when available |
| no-effect tag, missing visual, conflict, order, dependency, performance, symptom unexplained by vanilla source | compatibility and diagnostics | `rpg-maker-mz-visustella-compat-diagnostics` when available |

## Current Package State

At the time this router was added, the full specialized family may not all be
installed yet. If a route points to a future skill, state the intended route and
continue with the existing RPG Maker MZ gate that controls the target files.

## Required Boundaries

- Use this map for routing only.
- Do not copy plugin-specific syntax from memory.
- Do not authorize writes from this reference.
- Do not declare runtime behavior validated without Playtest or another
  approved human validation gate.
