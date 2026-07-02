---
name: rpg-maker-mz-visustella-plugin-index
description: Route RPG Maker MZ VisuStella work to the right plugin documentation and skills when a task mentions VisuStella broadly, plugin names, tiers, dependencies, load order, obfuscated plugin source, plugin families, or uncertainty about which VisuStella reference to use.
when_to_use:
  - "Use when RPG Maker MZ work mentions VisuStella broadly, a VisuStella plugin name, plugin family, tier, dependency, load order, compatibility, or unclear plugin ownership."
  - "Use before assuming a behavior is vanilla RPG Maker MZ when VisuStella plugins may add or override it."
  - "Use to choose the smallest relevant VisuStella skill or reference instead of loading an entire plugin corpus."
argument-hint: "[project_root, plugin_name, feature_or_symptom, target_surface]"
arguments:
  required: []
  optional:
    - project_root
    - plugin_name
    - feature_or_symptom
    - target_surface
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
  - VisuStella plugin ownership, tier, dependency, or load order is unclear
  - a task may require data JSON, plugin parameter, or runtime validation gates
  - a symptom is not explained by vanilla RPG Maker MZ source
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-plugin-index/SKILL.md"
  references:
    plugin_map: "references/plugin-map.md"
    routing_checklist: "references/routing-checklist.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-plugin-index

## Purpose

Route RPG Maker MZ work that involves VisuStella MZ plugins to the smallest
useful skill or reference. Use this as the entrypoint when the request is broad,
plugin ownership is unclear, plugin tier/order matters, or vanilla RPG Maker MZ
source does not explain the requested feature or symptom.

This skill is read-only guidance. It does not authorize writes to RPG Maker MZ
data, plugins, Plugin Manager configuration, assets, save state, generated
files, or runtime surfaces.

## Procedure

1. Confirm that the project or request is RPG Maker MZ and that VisuStella is
   mentioned, detected, or likely relevant.
2. Identify the strongest routing signal:
   - exact plugin name or family;
   - tier, dependency, load order, activation, or compatibility concern;
   - target surface such as parameters, notetags, plugin commands, Action
     Sequences, battle mechanics, progression/economy, events/presentation, or
     diagnostics;
   - symptom that vanilla RPG Maker MZ source does not explain.
3. Read `references/plugin-map.md` when you need plugin-family, tier, dependency
   or domain mapping.
4. Read `references/routing-checklist.md` when choosing the next skill,
   deciding which gate applies, or handling uncertainty.
5. Select one or two next skills/references. Do not load the entire VisuStella
   family by default.
6. Preserve existing Loki gates:
   - use `rpg-maker-mz-project-inventory` for local project evidence, installed
     plugins, `js/plugins.js`, data ownership, plugin commands, event callers
     or runtime-surface inventory;
   - use `rpg-maker-mz-data-json` before editing `data/*.json`, note fields,
     Common Events, maps, events, troops or database objects;
   - use `rpg-maker-mz-plugin-workflow` before editing plugin files,
     PluginManager integration, plugin metadata, plugin parameters or
     `js/plugins.js`;
   - require Playtest or another approved human validation gate before
     declaring runtime behavior, visuals, timing, input, audio, save/load,
     gameplay feel or Action Sequences validated.
7. If no route is reliable, report the missing signal and ask for project
   inventory or a narrower plugin/surface target instead of guessing.

## Inputs

- RPG Maker MZ project root or evidence from inventory.
- Plugin name, family, tier, feature, symptom or target surface.
- Intended operation: lookup, diagnosis, planning, writing, or validation.

## Outputs

- Recommended next VisuStella skill or reference, ideally one or two items.
- Required RPG Maker MZ write gate when the task may touch data or plugins.
- Uncertainty notes when plugin ownership, tier, dependency or active project
  evidence is missing.
- Runtime validation gate when behavior must be tested in game.

## References

- Read [plugin-map.md](references/plugin-map.md) for plugin families, tier
  heuristics, surfaces and domain routing.
- Read [routing-checklist.md](references/routing-checklist.md) for the routing
  decision order, write gates and uncertainty handling.

## Limits

- Do not treat this skill as complete plugin documentation.
- Do not infer exact plugin parameter names, notetag syntax, plugin command
  payloads or Action Sequence command details from this router alone.
- Do not inspect obfuscated VisuStella plugin source as the primary source of
  behavior when package references or project docs can route the task.
- Do not create a new VisuStella agent or command from this skill.
- Do not validate runtime behavior without a human validation gate.
