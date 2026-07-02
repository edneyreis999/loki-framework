---
name: rpg-maker-mz-visustella-compat-diagnostics
description: Use when diagnosing VisuStella MZ plugin order, tiers, dependencies, compatibility, troubleshooting, performance, runtime symptoms, plugin conflicts, missing effects, notetags with no effect, action sequence cleanup, camera or visual glitches, save/options/debug issues, or cases where RPG Maker MZ engine source does not explain observed behavior.
when_to_use:
  - "Use for VisuStella MZ plugin order, tiers, dependencies, compatibility, troubleshooting, performance, runtime symptoms, plugin conflicts, missing effects, notetags with no effect, Action Sequence cleanup, camera or visual glitches, save/options/debug issues, or unexplained behavior."
  - "Use when vanilla RPG Maker MZ source does not explain a symptom and active VisuStella plugins may override behavior."
  - "Use with loki:feedback for user-observed symptoms; this skill supplies VisuStella technical checks and does not replace the feedback interview."
argument-hint: "[project_root, symptom, plugin_name, affected_surface]"
arguments:
  required: []
  optional:
    - project_root
    - symptom
    - plugin_name
    - affected_surface
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
  - symptom could come from plugin order, dependency, inactive plugin, parameter, notetag, command payload, or runtime validation gap
  - runtime behavior, performance, save/options/debug, visuals, or Action Sequence playback is affected
  - broad troubleshooting may need loki:feedback, project inventory, or technical analysis
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-compat-diagnostics/SKILL.md"
  references:
    diagnostic_checklist: "references/diagnostic-checklist.md"
    compatibility_risk_map: "references/compatibility-risk-map.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-compat-diagnostics

## Purpose

Guide RPG Maker MZ troubleshooting when VisuStella MZ plugin order,
dependencies, compatibility, parameters, notetags, plugin commands, Action
Sequences, performance, visuals, save/options/debug surfaces, or runtime
symptoms may explain observed behavior.

This skill supplies VisuStella technical checks. It does not replace
`loki:feedback` for user-reported symptoms and does not authorize writes to
consumer data, plugin files, Plugin Manager configuration, assets, save state,
generated files, or runtime surfaces.

## Procedure

1. If the user reports observed feedback or an unclear symptom, use
   `loki:feedback` interview behavior when appropriate. Use this skill for the
   VisuStella-specific technical checklist after the symptom is concrete enough
   to inspect.
2. Confirm RPG Maker MZ and active VisuStella evidence. Use
   `rpg-maker-mz-project-inventory` when plugin list, `js/plugins.js`, order,
   database IDs, event callers, Common Events, assets, or save surfaces are
   unknown.
3. Identify the strongest symptom category: inactive/misordered plugin,
   dependency issue, parameter mismatch, notetag on wrong object, plugin command
   payload issue, Action Sequence missing effect/cleanup, battle mechanics,
   progression/economy, event/presentation, performance, save/options/debug, or
   runtime validation gap.
4. Read `references/diagnostic-checklist.md` to run the minimum
   troubleshooting flow.
5. Read `references/compatibility-risk-map.md` when plugin family, tier, order,
   dependency, cross-domain conflict, or performance risk matters.
6. Route to the smallest domain or MVP skill:
   - `rpg-maker-mz-visustella-plugin-index` for broad plugin ownership, tier,
     dependency, load order, or unclear route;
   - `rpg-maker-mz-visustella-plugin-parameters` for parameter/default issues;
   - `rpg-maker-mz-visustella-notetags` for note/comment syntax, target, or
     no-effect tag issues;
   - `rpg-maker-mz-visustella-plugin-commands` for event/Common Event command
     payloads or PluginManager command surfaces;
   - `rpg-maker-mz-visustella-action-sequences` for missing damage, cleanup,
     target loops, camera, impact, inject, projectile, or sequence playback;
   - `rpg-maker-mz-visustella-battle-mechanics` for Battle AI, ATB, TP, aggro,
     states, passives, damage, targets, gauges, or battle UI;
   - `rpg-maker-mz-visustella-progression-economy` for AP/SP, shops,
     currencies, inheritance, passives, costs, requirements, or economy;
   - `rpg-maker-mz-visustella-events-presentation` for events, messages,
     pictures, busts, DragonBones, options, save, debugger, UI, or visual flow.
7. Use `rpg-maker-mz-data-json` before any data/event JSON write and
   `rpg-maker-mz-plugin-workflow` before any plugin file, Plugin Manager,
   activation, load order, or `js/plugins.js` write.
8. Require Playtest or another approved human validation gate before declaring
   runtime behavior, visuals, timing, input, audio, save/load, battle behavior,
   event flow, Action Sequence playback, performance, or user-facing symptoms
   validated.

## Inputs

- RPG Maker MZ project evidence or project root.
- Symptom, plugin name, target surface, runtime observation, or suspected
  conflict.
- Intended operation: diagnosis, lookup, planning, proposed fix, or validation.

## Outputs

- Diagnostic category and evidence status.
- Minimum next skill route and required write gate.
- Checklist result for plugin active/order/dependency, parameter, notetag,
  command payload, Action Sequence cleanup, domain-specific risk, and Playtest.
- Remaining unknowns and runtime validation status.

## References

- Read [diagnostic-checklist.md](references/diagnostic-checklist.md) for the
  minimum troubleshooting flow.
- Read [compatibility-risk-map.md](references/compatibility-risk-map.md) for
  family-level compatibility and performance risks.

## Limits

- Do not replace `loki:feedback` when the symptom still requires a user
  interview.
- Do not infer plugin behavior only from vanilla RPG Maker MZ source when active
  VisuStella plugins may override it.
- Do not inspect obfuscated plugin source as the primary source when package
  references, project docs, or local project inventory can route the issue.
- Do not edit consumer data, plugin config, assets, saves, or runtime surfaces
  from this skill alone.
- Do not declare symptoms fixed without Playtest or another approved human
  validation gate when runtime behavior is involved.
