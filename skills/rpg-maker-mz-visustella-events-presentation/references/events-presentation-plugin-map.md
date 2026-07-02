# VisuStella Events And Presentation Plugin Map

Use this reference to route VisuStella MZ event, movement, message, picture,
UI, options, save, debugger, DragonBones, and presentation work. This map is a
compact routing aid, not complete plugin documentation.

## Domain Rule

Events and presentation tasks often combine plugin commands, event JSON, Plugin
Manager parameters, assets, maps, Common Events, and runtime-only visual/input
behavior. Route semantics here, but preserve data-json, plugin-workflow, and
human-validation gates.

## Plugin Families

| Plugin Or Family | Main Surfaces | Route To |
| --- | --- | --- |
| Events and Movement Core | map tags, event tags, page comment tags, custom page conditions, event templates, spawn/morph/location, event labels/icons/popups, event timers, auto movement, dash, call event, region/terrain rules, VS8 sprites | notetags, plugin commands, parameters, data-json |
| DragonBones Union | DragonBones armatures, battlers, map sprites, pictures, general/battler/map sprite settings, runtime DragonBones commands, asset naming and setup | notetags, plugin commands, parameters, diagnostics |
| Message Core | advanced text codes, auto-color, macros, word wrap, choice window behavior, language switching, picture text, select windows, message/choice/picture/select commands | plugin commands, parameters, data-json, human-validation |
| Visual Novel Picture Busts | bust enter/exit, graphic change, mirror, origin, movement, fade, scale, tone/tint, animation, anchor/position defaults | plugin commands, parameters, human-validation |
| Options Core | option categories, keyboard/gamepad rebind, basic/accessibility/function/data options, audio/UI/playtest categories, master volume shortcut | parameters, diagnostics, human-validation |
| Save Core | autosave, save commands, current slot, save description/picture, global switches/variables, save styles, confirmation windows, actor graphics | plugin commands, parameters, data-json, human-validation |
| Debugger | F9/debug replacement, switches/variables, Common Event launch, teleport, quick commands, battle testing, inventory, buffs/states, map events | parameters, diagnostics, human-validation |
| Core Engine presentation surfaces | picture control, text popups, screen shake, UI/window defaults, keyboard input, image loading | plugin commands, parameters, diagnostics |

## Surface Routing

| User Signal | Primary Route | Required Gate When Writing |
| --- | --- | --- |
| event template, spawn, morph, event location, event label, event icon, event popup, event timer | `rpg-maker-mz-visustella-plugin-commands` | `rpg-maker-mz-data-json` |
| map/event/page notetag or page comment condition | `rpg-maker-mz-visustella-notetags` | `rpg-maker-mz-data-json` |
| message text code, macro, word wrap, choice command, select command | plugin commands or parameters | data-json or plugin-workflow |
| visual novel bust command, picture text, fade, movement, scale, tone/tint | plugin commands | data-json for event payloads; human-validation |
| DragonBones battler/map sprite/picture setup | notetags, plugin commands, parameters | data-json, plugin-workflow, asset validation as task requires |
| options categories, controls, volume shortcut, playtest options | parameters and diagnostics | plugin-workflow; human-validation |
| autosave/save command, current slot, save description/picture, global variables | plugin commands or parameters | data-json or plugin-workflow; Playtest |
| debugger features, quick commands, battle testing, map/event debugging | parameters and diagnostics | plugin-workflow; human-validation |

## Runtime Gate Notes

- Message readability, word wrap, choice behavior, text speed, localization,
  picture/bust placement, DragonBones animation, input rebinding, autosave,
  save/load restoration, and debug menus are perceptible runtime behavior.
- Static review can verify structure and routing; it cannot prove player-facing
  visuals, timing, input, or save/load behavior.
- Use Playtest or another approved human validation gate before declaring these
  behaviors valid.

## Boundary

This reference routes event/presentation work only. It does not authorize
consumer data writes, plugin changes, asset changes, or save manipulation.
