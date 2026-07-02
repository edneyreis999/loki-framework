---
name: rpg-maker-mz-visustella-plugin-commands
description: Use when adding, reviewing, mapping, or debugging VisuStella MZ plugin commands in map events, troop events, Common Events, runtime event flows, message choices, save/autosave, movement, pictures, DragonBones, skills, shops, AP/SP, TP, ATB, aggro, or other PluginManager command surfaces.
when_to_use:
  - "Use for VisuStella MZ plugin commands in map events, troop events, Common Events, and runtime event flows."
  - "Use when mapping command payloads for message choices, save/autosave, movement, pictures, DragonBones, skills, shops, AP/SP, TP, ATB, aggro, or PluginManager command surfaces."
  - "Use with rpg-maker-mz-data-json before event JSON writes and rpg-maker-mz-plugin-workflow before plugin command registration, plugin files, activation, or PluginManager integration changes."
argument-hint: "[project_root, plugin_name, event_surface, command_goal]"
arguments:
  required: []
  optional:
    - project_root
    - plugin_name
    - event_surface
    - command_goal
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
  - event command payload structure or command IDs are unclear
  - command behavior depends on plugin activation, PluginManager integration, or load order
  - runtime behavior requires Playtest
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-plugin-commands/SKILL.md"
  references:
    command_surfaces: "references/plugin-command-surfaces.md"
    command_index: "references/plugin-command-index.md"
    payload_checklist: "references/event-payload-checklist.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-plugin-commands

## Purpose

Guide RPG Maker MZ work involving VisuStella MZ plugin commands in events,
troop events, Common Events, and runtime event flows. This skill maps command
surfaces and payload review. It does not authorize writes to consumer data or
plugin files.

## Procedure

1. Confirm the work is RPG Maker MZ and VisuStella MZ is installed, named, or
   likely relevant. Use `rpg-maker-mz-project-inventory` when active plugins,
   event callers, Common Event IDs, or command ownership are unknown.
2. Identify the command surface: map event, troop event, Common Event, Action
   Sequence Common Event, message flow, picture flow, save/autosave, movement,
   battle resource, shop/progression, DragonBones, or system/debug action.
3. Read `references/plugin-command-surfaces.md` to choose the data/plugin gate.
4. Read `references/plugin-command-index.md` to narrow the owning plugin or
   family.
5. Read `references/event-payload-checklist.md` before proposing, reviewing, or
   editing event command payloads.
6. Use `rpg-maker-mz-data-json` before any write to `data/*.json`, map events,
   troop events, Common Events, event command lists, or event payloads.
7. Use `rpg-maker-mz-plugin-workflow` before editing plugin files, plugin
   command registration, PluginManager integration, plugin activation,
   parameters, or `js/plugins.js`.
8. Route Battle Core Action Sequence command workflows to
   `rpg-maker-mz-visustella-action-sequences`.
9. Keep runtime validation pending until Playtest or another approved human
   validation gate.

## Inputs

- RPG Maker MZ project evidence or project root.
- VisuStella plugin/family, command name, event surface, or runtime symptom.
- Event target: map, event/page, troop, Common Event, or caller chain.

## Outputs

- Command surface and plugin/family route.
- Required data/plugin write gate.
- Payload checklist and unresolved IDs/parameters.
- Runtime validation status.

## References

- Read [plugin-command-surfaces.md](references/plugin-command-surfaces.md) for
  event surfaces and gate mapping.
- Read [plugin-command-index.md](references/plugin-command-index.md) for a
  concise plugin/family command index.
- Read [event-payload-checklist.md](references/event-payload-checklist.md)
  before writing or reviewing event command payloads.

## Limits

- Do not edit events, maps, troops, Common Events, plugin files, or
  `js/plugins.js` from this skill alone.
- Do not treat Action Sequences as generic plugin commands when setup/finish,
  target loops, `MECH: Action Effect`, or Common Event linkage matters.
- Do not validate runtime behavior without Playtest or another approved human
  validation gate.
