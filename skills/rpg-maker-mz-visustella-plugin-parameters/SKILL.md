---
name: rpg-maker-mz-visustella-plugin-parameters
description: Use when configuring, reviewing, diagnosing, or documenting VisuStella MZ Plugin Manager parameters, global defaults, plugin-specific settings, tier-dependent behavior, UI/menu/save/options settings, battle defaults, formulas, visual defaults, or parameter values stored through js/plugins.js.
when_to_use:
  - "Use for VisuStella MZ Plugin Manager parameters, plugin defaults, formulas, UI/menu/save/options settings, battle defaults, visual defaults, or parameter values stored through js/plugins.js."
  - "Use before changing VisuStella parameter values, activation assumptions, tier-dependent settings, or load-order-sensitive defaults."
  - "Use with rpg-maker-mz-plugin-workflow before any write to js/plugins.js, plugin metadata, plugin files, or PluginManager integration."
argument-hint: "[project_root, plugin_name, parameter_area, intended_change]"
arguments:
  required: []
  optional:
    - project_root
    - plugin_name
    - parameter_area
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
  - a parameter write would touch js/plugins.js or plugin activation
  - plugin tier, dependency, or load order affects the parameter
  - runtime behavior, UI, save, input, battle, or visual behavior must be validated
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-plugin-parameters/SKILL.md"
  references:
    parameter_surfaces: "references/parameter-surfaces.md"
    plugin_parameter_index: "references/plugin-parameter-index.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-plugin-parameters

## Purpose

Guide RPG Maker MZ work involving VisuStella MZ Plugin Manager parameters and
parameter values persisted through `js/plugins.js`. This skill supplies
semantic routing and review checklists. It does not authorize writes to
consumer projects.

## Procedure

1. Confirm the work is RPG Maker MZ and VisuStella MZ is installed, named, or
   likely relevant. Use `rpg-maker-mz-project-inventory` when local plugin
   evidence, active order, or exact plugin names are unknown.
2. Identify the parameter surface: global/core defaults, UI/menu/window,
   save/options/input, battle defaults, progression/economy, event/presentation
   settings, visual defaults, formulas, plugin tier/order, or plugin-specific
   settings.
3. Read `references/parameter-surfaces.md` before deciding whether the work is
   lookup-only, planning, diagnosis, or a `js/plugins.js` write.
4. Read `references/plugin-parameter-index.md` to narrow the plugin family and
   the likely parameter area.
5. Use the smallest next context:
   - route broad plugin ownership, tier, dependency, or load-order questions to
     `rpg-maker-mz-visustella-plugin-index`;
   - route note/comment syntax to `rpg-maker-mz-visustella-notetags`;
   - route event payloads to `rpg-maker-mz-visustella-plugin-commands`;
   - route Battle Core Action Sequence behavior to
     `rpg-maker-mz-visustella-action-sequences`.
6. Before changing any Plugin Manager value, plugin activation, plugin metadata,
   helper plugin, PluginManager integration, or `js/plugins.js`, load and follow
   `rpg-maker-mz-plugin-workflow`.
7. Require Playtest or another approved human validation gate before declaring
   parameter-driven runtime behavior validated.

## Inputs

- RPG Maker MZ project evidence or project root.
- VisuStella plugin name, family, parameter area, symptom, or desired setting.
- Intended operation: lookup, review, diagnosis, planning, or write.

## Outputs

- Parameter family or plugin route.
- Required write gate, especially `rpg-maker-mz-plugin-workflow` for
  `js/plugins.js`.
- Notes about tier, dependency, activation, and runtime validation.
- Recommendation for a narrower VisuStella skill when parameters are not the
  main surface.

## References

- Read [parameter-surfaces.md](references/parameter-surfaces.md) for parameter
  locations, write boundaries, and review checklist.
- Read [plugin-parameter-index.md](references/plugin-parameter-index.md) for a
  concise plugin/family index of parameter areas.

## Limits

- Do not edit `js/plugins.js`, plugin files, plugin metadata, or PluginManager
  integration from this skill alone.
- Do not infer exact active parameter values without project inventory or the
  actual consumer `js/plugins.js`.
- Do not use note fields, plugin commands, or Action Sequences as parameter
  substitutes.
- Do not declare runtime behavior validated without Playtest or another
  approved human validation gate.
