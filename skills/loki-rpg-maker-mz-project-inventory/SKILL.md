---
name: loki-rpg-maker-mz-project-inventory
description: Inventory an RPG Maker MZ project before analysis or implementation by mapping project root, System IDs, Common Events, maps, plugins, plugin commands, assets, save/load surfaces, runtime gates, missing evidence, and required handoff to loki:tech-analysis when static inventory is incomplete. Use for RPG Maker MZ game projects, especially when game-dev agents need shared evidence before handoff or runtime/data/plugin planning.
when_to_use:
  - "Use after a project is detected as RPG Maker MZ and agents need a reliable project inventory."
  - "Use before `loki:tech-analysis` when the question depends on RPG Maker MZ project structure, switches, variables, Common Events, maps, plugins, assets, or save/load surfaces."
  - "Use during init or corrective fan-out only when a game-dev agent determines that an RPG Maker MZ project needs shared inventory evidence."
  - "Use when a game-dev agent cannot complete its inventory because implementation boundaries are unmapped."
argument-hint: "[project_root, docs_index, focus_area, output_target]"
arguments:
  required: []
  optional:
    - project_root
    - docs_index
    - focus_area
    - output_target
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - RPG Maker MZ runtime inventory is incomplete
  - Common Events, switches, variables, maps, plugins or save/load ownership are unknown
  - inventory findings require loki:tech-analysis before an agent can finish handoff
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-rpg-maker-mz-project-inventory/SKILL.md"
  references:
    checklist: "references/inventory-checklist.md"
shell: {}
type: skill
status: draft
---

# loki-rpg-maker-mz-project-inventory

## Purpose

Build a read-only inventory of an RPG Maker MZ project so Loki agents can reason
from concrete project evidence instead of guessing runtime ownership.

This skill does not edit runtime files. It exists to answer: what project
surfaces exist, what was inspected, what remains unmapped, and whether a
`loki:tech-analysis` run is required before a specialist agent can complete its
handoff.

## Procedure

1. Resolve `project_root`.
   - If the workspace has a nested RPG Maker MZ project, use the directory that
     contains `game.rmmzproject`, `index.html`, `data/` and `js/`.
   - Prefer the user-provided project root when multiple RPG Maker MZ projects
     exist.
2. Read project routing docs before inspecting implementation:
   - root `AGENTS.md` or `CLAUDE.md` when present;
   - project-local `AGENTS.md` or `CLAUDE.md` when present;
   - `docs/index.xml` when the project guidance requires durable docs first.
3. Confirm the RPG Maker MZ signature:
   - `game.rmmzproject`;
   - `data/System.json`;
   - `data/CommonEvents.json`;
   - `data/MapInfos.json`;
   - `js/rmmz_*.js`;
   - `js/plugins.js`.
4. Build a file-surface inventory:
   - database JSON files;
   - map JSON files;
   - plugin files;
   - asset roots: `img`, `audio`, `movies`, `effects`, `fonts`;
   - save/local state roots.
5. Parse, do not regex, the high-value JSON surfaces when needed:
   - `System.json` for switch names, variable names, start map, terms and game
     title;
   - `CommonEvents.json` for IDs, names, trigger types, switches and command
     code summaries;
   - `MapInfos.json` for map IDs and names.
6. Inspect `js/plugins.js` for active plugins, order and parameters. Treat plugin
   order and parameters as runtime-sensitive.
7. When a focus area is known, map ownership:
   - variables and switches referenced by docs or tasks;
   - Common Events involved;
   - map events that call those Common Events;
   - plugin files and plugin commands likely involved;
   - assets referenced by pictures, audio commands or plugin parameters.
8. Separate facts, inferences and hypotheses.
9. Mark inventory status:
   - `complete`: enough evidence exists for the requested inventory scope;
   - `partial`: important surfaces remain unmapped;
   - `blocked`: the next required evidence needs unavailable tooling, user
     input, Playtest, editor access or a forbidden write.
10. If the inventory is `partial` or `blocked` and a specialist agent needs it
    to finish a handoff, explicitly recommend `loki:tech-analysis` with a
    concrete focus and source list.
11. Do not claim runtime validation. Runtime, visuals, audio, input, Common
    Event execution and save/load require human Playtest evidence.

## Output Contract

Produce Markdown with these sections:

- `Status`: `complete`, `partial` or `blocked`.
- `Project Root`.
- `RPG Maker MZ Signature`.
- `Sources Attempted`.
- `Sources Read`.
- `Surface Inventory`.
- `System ID Map`: switches, variables and relevant system settings.
- `Common Event Map`.
- `Map Inventory`.
- `Plugin Inventory`.
- `Asset And Save Surfaces`.
- `Feature Ownership Matrix`.
- `Common Event Graph`.
- `Doc-Runtime Drift`.
- `Ownership Map For Focus Area`.
- `Evidence Map`.
- `Missing Evidence`.
- `Do Not Assume`.
- `Required Validators`.
- `Human Validation Gates`.
- `Need For loki:tech-analysis`.
- `Minimum Next Question`.
- `Context Budget Used`.

## Required Gates

- Use `loki-index-navigator` first when durable docs are required by project
  guidance.
- Use `loki-rpg-maker-mz-data-json` before editing `data/*.json`.
- Use `loki-rpg-maker-mz-plugin-workflow` before editing plugins or
  `plugins.js`.
- Use human validation before declaring runtime behavior valid.

## Limits

- Do not write runtime, data, plugin, asset, save or generated files.
- Do not mutate JSON while inventorying.
- Do not run historical build scripts as part of inventory.
- Do not infer RPG Maker command semantics from memory when local engine source
  is available.
- Do not treat JSON parse success as runtime validation.
- Do not let a game-dev agent mark its inventory complete when required
  implementation boundaries remain unmapped; escalate to `loki:tech-analysis`
  or return a structured `partial`/`blocked` handoff.

## References

- Read `references/inventory-checklist.md` when deciding which RPG Maker MZ
  surfaces to inspect or how to structure a corrective inventory pass.
