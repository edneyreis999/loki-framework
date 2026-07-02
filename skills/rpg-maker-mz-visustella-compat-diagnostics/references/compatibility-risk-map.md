# VisuStella Compatibility Risk Map

Use this reference when a VisuStella MZ symptom may involve plugin order,
dependencies, compatibility, performance, or cross-domain interaction.

## Global Risk Rules

- Core Engine is the common foundation. Do not analyze dependent VisuStella
  behavior as vanilla-only when Core Engine or other VisuStella plugins are
  active.
- Lower-tier plugins normally belong above higher-tier extensions in Plugin
  Manager order.
- Battle Core is the foundation for most battle-domain extensions and Action
  Sequence behavior.
- Plugin Manager parameters, notetags, comment tags, plugin commands, event
  payloads, and runtime plugin behavior can all override or combine with each
  other.
- Runtime symptoms require Playtest or another approved human validation gate.

## Family Risk Map

| Family | Typical Risks | First Route |
| --- | --- | --- |
| Core Engine | base parameter mismatch, input/menu/window behavior, image loading, UI defaults, system commands, compatibility foundation | plugin-index, plugin-parameters |
| Battle Core and Action Sequence extensions | missing Battle Core, extension command unavailable, missing `MECH: Action Effect`, cleanup not run, target loop issue, camera/impact/inject reset missing | action-sequences, battle-mechanics |
| ATB and TP systems | project not in expected battle mode, speed/interrupt/gauge formula mismatch, actor/enemy/system command payload issue, TP mode unlock mismatch | battle-mechanics, plugin-parameters, plugin-commands |
| Battle AI and Aggro | AI condition not met, target weighting mismatch, provoke/taunt/aggro priority misunderstood, state/tag target mismatch | battle-mechanics, notetags |
| Skills/States/Passives/Visual State Effects | passive cache, state target support, aura/miasma dead rules, slip timing, visual overlay/tone/opacity performance, buff/debuff popup behavior | battle-mechanics, notetags, plugin-parameters |
| Progression and Economy | AP/SP source mismatch, shop visibility differs from purchase enablement, More Currencies proxy mismatch, inherited data order/override issue, passive unlock state mismatch | progression-economy, notetags, plugin-commands |
| Events and Movement | event template/caller mismatch, spawned/morphed event identity, label/icon/popup timing, region/terrain behavior, movement command context | events-presentation, plugin-commands |
| Message, Picture Busts, DragonBones | text code/context mismatch, word wrap/localization display, picture ID/anchor/tone/scale issue, DragonBones armature naming/assets, visual layering/performance | events-presentation, plugin-commands, plugin-parameters |
| Options, Save, Debugger | option persistence/rebind issue, autosave command timing, current slot/description/picture mismatch, global switches/variables, debug-only feature leaking into runtime assumptions | events-presentation, plugin-parameters |

## Performance And Runtime Notes

- Visual State Effects, camera, impact, inject, DragonBones, overlays, pictures,
  bust animation, and large inherited database setups can create performance or
  timing risks that static review cannot fully validate.
- Save/load, autosave, options persistence, global switches/variables, and
  debug-only features can affect state across sessions. Treat these as
  human-validation gated.
- If a symptom appears only during battle, event playback, save/load, or input
  interaction, label it `runtime-pending` until validated.

## Write Gate Mapping

| Proposed Fix | Required Gate |
| --- | --- |
| edit data JSON, note fields, events, Common Events, event payloads, database objects | `rpg-maker-mz-data-json` |
| edit plugin parameters, activation, load order, plugin files, PluginManager integration, `js/plugins.js` | `rpg-maker-mz-plugin-workflow` |
| inspect active order, plugin list, event callers, object IDs, assets, save surfaces | `rpg-maker-mz-project-inventory` |
| prove visual, timing, input, audio, save/load, battle, event, or performance behavior | Playtest or another approved human validation gate |
