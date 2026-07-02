---
name: rpg-maker-mz-visustella-action-sequences
description: Use when creating, translating, reviewing, or debugging VisuStella Battle Core Action Sequences for RPG Maker MZ skills or items, including <Custom Action Sequence>, Common Event plugin commands, setup and finish flow, movement, animations, MECH Action Effect, target loops, projectiles, camera, impact, inject, zoom, timing, and XML example matching.
when_to_use:
  - "Use for VisuStella Battle Core Action Sequences on RPG Maker MZ skills or items."
  - "Use when the task mentions <Custom Action Sequence>, Common Event Battle Core plugin commands, setup/finish flow, MECH Action Effect, target loops, movement, animations, projectiles, camera, impact, inject, zoom, timing, or XML example matching."
  - "Use with rpg-maker-mz-visustella-notetags, rpg-maker-mz-visustella-plugin-commands, and rpg-maker-mz-data-json before any consumer data write."
argument-hint: "[project_root, skill_or_item, sequence_goal, common_event]"
arguments:
  required: []
  optional:
    - project_root
    - skill_or_item
    - sequence_goal
    - common_event
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: coding
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - target loop, Action Effect, Common Event linkage, or cleanup is unclear
  - sequence uses camera, impact, inject, projectile, JavaScript, or extension-only command groups
  - runtime behavior must be validated in battle
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-action-sequences/SKILL.md"
  references:
    command_index: "references/action-sequence-command-index.md"
    patterns: "references/action-sequence-patterns.md"
    example_index: "references/action-sequence-example-index.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-action-sequences

## Purpose

Guide creation, translation, review, and debugging of VisuStella Battle Core
Action Sequences. Action Sequences combine skill/item notetags, Common Events,
Battle Core plugin commands, event payload structure, and runtime Playtest.

This skill is semantic guidance only. It does not authorize writes to consumer
RPG Maker MZ data, Common Events, skills, items, plugin files, or `js/plugins.js`.

## Procedure

1. Confirm the work is RPG Maker MZ, VisuStella Battle Core is active or
   expected, and the task is truly an Action Sequence task.
2. Use `rpg-maker-mz-project-inventory` when active plugin evidence, Common
   Event IDs, skill/item IDs, or event callers are unknown.
3. Load `rpg-maker-mz-visustella-notetags` for skill/item note fields such as
   `<Custom Action Sequence>`, auto/bypass tags, and Common Event key tags.
4. Load `rpg-maker-mz-visustella-plugin-commands` for Battle Core plugin
   commands inside the Common Event.
5. Load `rpg-maker-mz-data-json` before any write to `data/*.json`, skills,
   items, Common Events, event command lists, or effect lists.
6. Read `references/action-sequence-command-index.md` to choose command groups.
7. Read `references/action-sequence-patterns.md` before generating or reviewing
   a sequence flow.
8. Read `references/action-sequence-example-index.md` when matching a requested
   motion, combo, projectile, teleport, cast, or multi-target pattern to an
   internal example family.
9. If the sequence should apply the current action's damage, healing, buffs,
   debuffs, state effects, item effects, or skill effects, verify the presence
   of `MECH: Action Effect` or an explicit equivalent such as emulated
   item/skill effect. If absent, call it out as a blocker or justify why no
   action effect is needed.
10. Require Playtest or another approved human validation gate before declaring
    timing, visuals, damage, target loops, camera, impact, audio, cleanup, or
    battle behavior validated.

## Inputs

- RPG Maker MZ project evidence or project root.
- Skill/item ID or name, Common Event ID/name, target scope, and desired visual
  or mechanical behavior.
- Existing sequence, XML example name, natural-language brief, or runtime
  symptom.

## Outputs

- Required notetag/Common Event/effect linkage.
- Recommended command groups and pattern.
- `MECH: Action Effect` review result when action effects are expected.
- Required data-json and Playtest gates.
- Example family route when matching against bundled patterns.

## References

- Read [action-sequence-command-index.md](references/action-sequence-command-index.md)
  for command groups and dependency notes.
- Read [action-sequence-patterns.md](references/action-sequence-patterns.md) for
  setup/action/finish, target loops, projectiles, camera, impact, inject, and
  cleanup patterns.
- Read [action-sequence-example-index.md](references/action-sequence-example-index.md)
  for the validated internal XML example index.

## Limits

- Do not edit Common Events, skills, items, or `data/*.json` from this skill
  alone.
- Do not promise a sequence works without Playtest.
- Do not omit `MECH: Action Effect` for damaging/healing/effect-applying
  sequences unless the sequence intentionally uses an explicit equivalent.
- Do not treat camera/impact/inject extension commands as available unless the
  relevant VisuStella extension plugin is active.
