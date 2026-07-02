---
name: rpg-maker-mz-visustella-notetags
description: Use when generating, reviewing, locating, or validating VisuStella MZ notetags or comment tags for RPG Maker MZ actors, classes, skills, items, weapons, armors, enemies, states, maps, events, troops, note fields, formulas, inheritance, costs, targeting, states, visuals, or plugin-specific note syntax.
when_to_use:
  - "Use for VisuStella MZ notetags, note fields, comment tags, or plugin-specific note syntax in RPG Maker MZ data."
  - "Use when deciding which actor, class, skill, item, weapon, armor, enemy, state, map, event, page, troop, or Common Event surface should hold a tag."
  - "Use with rpg-maker-mz-data-json before any write to data/*.json, note fields, event comments, troop events, maps, or database objects."
argument-hint: "[project_root, plugin_name, object_type, intended_tag]"
arguments:
  required: []
  optional:
    - project_root
    - plugin_name
    - object_type
    - intended_tag
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
  - the correct note/comment target is unclear
  - a tag uses JavaScript, formulas, IDs, costs, targeting, state effects, or inheritance
  - runtime behavior must be validated in game
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-notetags/SKILL.md"
  references:
    notetag_targets: "references/notetag-targets.md"
    plugin_notetag_index: "references/plugin-notetag-index.md"
    validation_checklist: "references/notetag-validation-checklist.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-notetags

## Purpose

Guide RPG Maker MZ work involving VisuStella MZ notetags and comment tags. This
skill helps choose the correct object, note field, comment surface, and related
plugin family. It does not authorize writes to consumer data files.

## Procedure

1. Confirm the work is RPG Maker MZ and VisuStella MZ is installed, named, or
   likely relevant. Use `rpg-maker-mz-project-inventory` when plugin evidence,
   database files, active plugins, or object IDs are unknown.
2. Identify whether the requested change is a notetag, comment tag, parameter,
   plugin command, or Action Sequence. Route away from this skill when the main
   surface is not note/comment syntax.
3. Read `references/notetag-targets.md` to choose the correct RPG Maker MZ data
   object and storage surface.
4. Read `references/plugin-notetag-index.md` to narrow the VisuStella plugin or
   family.
5. Read `references/notetag-validation-checklist.md` before proposing or
   reviewing a tag.
6. Before editing `data/*.json`, database objects, maps, events, troops, note
   fields, or event comments, load and follow `rpg-maker-mz-data-json`.
7. If the tag changes battle, map, UI, visual, save/load, economy, targeting,
   state, input, or Action Sequence behavior, keep runtime validation pending
   until Playtest or another approved human validation gate.

## Inputs

- RPG Maker MZ project evidence or project root.
- VisuStella plugin/family or desired behavior.
- Target object type, object ID/name, note field, comment surface, or symptom.

## Outputs

- Recommended object and note/comment surface.
- Relevant plugin/family route.
- Required `rpg-maker-mz-data-json` gate before data writes.
- Validation checklist result and runtime validation status.

## References

- Read [notetag-targets.md](references/notetag-targets.md) for valid RPG Maker
  MZ target objects and write gates.
- Read [plugin-notetag-index.md](references/plugin-notetag-index.md) for a
  concise plugin/family index of notetag topics.
- Read [notetag-validation-checklist.md](references/notetag-validation-checklist.md)
  before writing or reviewing a tag.

## Limits

- Do not edit `data/*.json` from this skill alone.
- Do not place a tag on an object type unless the target object is explicitly
  supported by the plugin/family reference.
- Do not treat Plugin Manager parameters or event plugin commands as notetags.
- Do not declare runtime behavior validated without Playtest or another
  approved human validation gate.
