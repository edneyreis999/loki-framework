# VisuStella Parameter Surfaces

Use this reference to decide where a VisuStella setting lives and which Loki
gate applies before any write.

## Surface Map

| Surface | Typical Storage | Required Gate Before Write |
| --- | --- | --- |
| Plugin Manager parameter value | `js/plugins.js` `parameters` entry for the active plugin | `rpg-maker-mz-plugin-workflow` |
| Plugin activation or enabled flag | `js/plugins.js` plugin list | `rpg-maker-mz-plugin-workflow` |
| Plugin load order or dependency order | `js/plugins.js` plugin list order | `rpg-maker-mz-plugin-workflow`; route order diagnosis through the VisuStella index or diagnostics skill when available |
| Helper plugin or plugin command registration | `js/plugins/*.js` and PluginManager APIs | `rpg-maker-mz-plugin-workflow` |
| Runtime result of a parameter | battle, map, UI, input, save, audio, picture, message, or event behavior | Playtest or another approved human validation gate |
| Object-specific override | RPG Maker MZ note fields or event comments | `rpg-maker-mz-data-json` plus `rpg-maker-mz-visustella-notetags` |
| Event-time action | map events, troop events, or Common Events | `rpg-maker-mz-data-json` plus `rpg-maker-mz-visustella-plugin-commands` |

## Decision Checklist

1. Confirm the exact plugin name as installed. VisuStella plugin display names
   and file names can differ.
2. Confirm the plugin is active and above/below dependencies as expected before
   treating a parameter as effective.
3. Separate global default from object override. Many VisuStella systems use
   Plugin Manager parameters as defaults and notetags or commands as local
   overrides.
4. Preserve the existing `js/plugins.js` structure. Do not hand-edit serialized
   parameter blobs without the plugin workflow gate.
5. For formulas, JavaScript snippets, or script-like parameter fields, review
   the parameter context and target runtime data before writing.
6. For UI, options, save, input, battle, movement, picture, message, audio, or
   Action Sequence behavior, mark runtime validation as pending until Playtest.

## Common Misroutes

- A tag inside an actor, class, skill, item, enemy, state, map, event, or troop
  is a notetag/comment-tag task, not a parameter task.
- A command inserted into an event list is a plugin-command task, not a
  parameter task.
- `<Custom Action Sequence>` and Common Event Battle Core commands belong to
  the Action Sequence skill, even when a Battle Core parameter affects defaults.
- Load-order fixes are not pure parameter changes; they affect plugin
  activation and require `rpg-maker-mz-plugin-workflow`.

## Observable Output Shape

A good parameter answer should say:

- the likely plugin/family;
- the parameter area or ambiguity;
- whether project inventory is needed to confirm active values;
- that `rpg-maker-mz-plugin-workflow` is required before editing
  `js/plugins.js`;
- which Playtest gate remains for runtime behavior.
