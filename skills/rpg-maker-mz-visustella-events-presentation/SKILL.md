---
name: rpg-maker-mz-visustella-events-presentation
description: Use when configuring, reviewing, or debugging VisuStella MZ event, movement, message, picture, visual novel, animation, UI, options, save, debugger, text code, localization, DragonBones, event template, spawn, morph, label, icon, popup, bust, or presentation workflows that extend RPG Maker MZ runtime behavior.
when_to_use:
  - "Use for VisuStella MZ event, movement, message, picture, bust, animation, UI, options, save, debugger, localization, text code, DragonBones, or presentation workflows."
  - "Use when the task mentions Events and Movement Core, DragonBones Union, Message Core, Visual Novel Picture Busts, Options Core, Save Core, Debugger, event templates, spawn/morph/location, labels, icons, popups, busts, choices, text codes, or save/autosave behavior."
  - "Use with plugin commands, parameters, notetags, data-json, and human-validation gates when runtime visual, input, save/load, or event flow behavior is affected."
argument-hint: "[project_root, plugin_name, presentation_surface, intended_change]"
arguments:
  required: []
  optional:
    - project_root
    - plugin_name
    - presentation_surface
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
  - event flow, visual presentation, input, options, save/load, or DragonBones behavior is affected
  - task may touch maps, Common Events, event commands, pictures, plugin parameters, or save/autosave behavior
  - runtime or human-validation gate is required
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-events-presentation/SKILL.md"
  references:
    events_presentation_plugin_map: "references/events-presentation-plugin-map.md"
    events_presentation_checklist: "references/events-presentation-checklist.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-events-presentation

## Purpose

Guide RPG Maker MZ work involving VisuStella MZ event flow, movement,
messages, pictures, busts, UI, options, save/autosave, debugger, localization,
DragonBones, and presentation workflows.

This skill is semantic guidance only. It does not authorize writes to consumer
RPG Maker MZ data, maps, events, plugin files, Plugin Manager configuration,
assets, save files, generated files, or runtime surfaces.

## Procedure

1. Confirm the work is RPG Maker MZ and that VisuStella event/presentation
   plugins are installed, named, or likely relevant. Use
   `rpg-maker-mz-project-inventory` when active plugins, event IDs, map IDs,
   Common Events, plugin order, asset ownership, or save surfaces are unknown.
2. Identify the surface: event movement, event template, spawn/morph/location,
   labels/icons/popups, message text codes, choices, macros, localization,
   picture text, visual novel busts, DragonBones battlers/map sprites/pictures,
   options, save/autosave, debugger, UI windows, or runtime presentation.
3. Read `references/events-presentation-plugin-map.md` to narrow the plugin
   family and MVP surface skill.
4. Read `references/events-presentation-checklist.md` before proposing,
   reviewing, or debugging event/presentation behavior.
5. Load the smallest MVP VisuStella skill needed:
   - `rpg-maker-mz-visustella-plugin-commands` for event commands, message
     commands, choice commands, picture/bust commands, save/autosave commands,
     DragonBones runtime commands, event movement commands, or debugger flows;
   - `rpg-maker-mz-visustella-plugin-parameters` for message/window defaults,
     text codes, word wrap, option categories, save styles, DragonBones
     settings, event labels/icons, movement settings, or picture defaults;
   - `rpg-maker-mz-visustella-notetags` for map/event/page comments,
     DragonBones setup, event movement tags, map sprite tags, or visual setup
     stored in database notes/comments;
   - `rpg-maker-mz-visustella-compat-diagnostics` when the symptom may be
     missing plugin activation, load order, command availability, unsupported
     surface, save/options issue, visual glitch, or performance.
6. Use `rpg-maker-mz-data-json` before any write to `data/*.json`, maps,
   events, event pages, event command lists, Common Events, note fields,
   comments, troops, or database objects.
7. Use `rpg-maker-mz-plugin-workflow` before changing plugin files,
   PluginManager integration, plugin parameters, activation, load order, or
   `js/plugins.js`.
8. Mark `human-validation` or Playtest as required before declaring visuals,
   input, timing, event reachability, message readability, picture/bust
   placement, DragonBones animation, options behavior, save/load behavior,
   debugger behavior, or runtime flow validated.

## Inputs

- RPG Maker MZ project evidence or project root.
- VisuStella plugin/family, event/presentation surface, map/event/Common Event
  target, UI/picture/save/options target, or runtime symptom.
- Intended operation: lookup, review, diagnosis, planning, or write.

## Outputs

- Event/presentation plugin route and surface classification.
- Required MVP skill and RPG Maker MZ write gate.
- Checklist result for event flow, message, picture, bust, DragonBones,
  options, save/autosave, debugger, or visual/runtime behavior.
- Explicit human-validation or Playtest status when behavior is perceptible.

## References

- Read [events-presentation-plugin-map.md](references/events-presentation-plugin-map.md)
  for plugin families, surfaces, and routing.
- Read [events-presentation-checklist.md](references/events-presentation-checklist.md)
  before designing, reviewing, or debugging event/presentation behavior.

## Limits

- Do not edit maps, events, pictures, assets, saves, plugin files, or data JSON
  from this skill alone.
- Do not create consumer project docs or project-specific presentation policy
  from this skill.
- Do not replace UX, scene presentation, narrative, audio, technical art, or
  runtime QA agents; use this as technical VisuStella context.
- Do not declare runtime visual/input/save behavior validated without
  human-validation or Playtest.
