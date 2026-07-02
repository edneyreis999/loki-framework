# VisuStella Plugin Command Surfaces

Use this reference to identify where a VisuStella plugin command lives and which
gate applies before any write.

## Surface Map

| Surface | Typical File | Required Gate |
| --- | --- | --- |
| Map event command list | `data/MapXXX.json` | `rpg-maker-mz-data-json` |
| Event page command list | `data/MapXXX.json` | `rpg-maker-mz-data-json` |
| Troop event command list | `data/Troops.json` | `rpg-maker-mz-data-json` |
| Common Event command list | `data/CommonEvents.json` | `rpg-maker-mz-data-json` |
| Action Sequence Common Event | `data/CommonEvents.json` plus skill/item link | `rpg-maker-mz-data-json` and `rpg-maker-mz-visustella-action-sequences` |
| Plugin command registration or implementation | `js/plugins/*.js` PluginManager APIs | `rpg-maker-mz-plugin-workflow` |
| Plugin activation, command availability, or parameterized command behavior | `js/plugins.js` and active plugin list | `rpg-maker-mz-plugin-workflow` |

## Runtime Command Types

- Event flow: call event, movement, dash, event labels/icons/popups/timers,
  event location, copied/template event behavior.
- Narrative/presentation: message commands, choices, select flows, pictures,
  visual novel bust movement/fade/scale/tone/animation.
- Save/options/system: autosave, save commands, system toggles, debug/export.
- Battle resources: ATB, TP, aggro, skill costs, state turns, AP/SP, passive
  skill state operations.
- Economy/shop/items: shop commands, purify commands, item/equip actor
  commands, Skill Shop commands.
- Visual/runtime assets: DragonBones commands, picture commands, animation,
  audio, screen shake, text popup.

## Gate Rules

- A command already present in a consumer event can be reviewed read-only with
  project evidence.
- Creating, deleting, reordering, or changing command payloads requires
  `rpg-maker-mz-data-json`.
- Adding a new helper plugin command or changing a command definition requires
  `rpg-maker-mz-plugin-workflow`.
- If command behavior depends on active plugin order, load order, or
  parameters, confirm with project inventory and plugin workflow before writing.
- Any command that affects visible runtime behavior needs Playtest or another
  approved human validation gate.

## Common Misroutes

- A Plugin Manager setting is a parameter task, not a plugin-command task.
- A note field tag is a notetag task, not a plugin-command task.
- A Battle Core Action Sequence Common Event is an Action Sequence task, even
  though it uses plugin commands internally.
