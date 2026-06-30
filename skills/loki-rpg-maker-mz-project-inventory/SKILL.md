---
name: loki-rpg-maker-mz-project-inventory
description: Guide read-only inventory of RPG Maker MZ projects before game-dev analysis, handoff, planning, or implementation by mapping local evidence across project signature, docs, System IDs, Common Events, maps, plugins, plugin commands, assets, save/load, domain surfaces, validation limits, and escalation to loki:tech-analysis. Use when agents need RPG Maker MZ evidence without changing their response format.
when_to_use:
  - "Use after a project is detected as RPG Maker MZ and a game-dev agent needs reliable local inventory evidence."
  - "Use before `loki:tech-analysis` when the question depends on RPG Maker MZ project structure, switches, variables, Common Events, maps, plugins, plugin commands, assets, save/load, UI, narrative, audio, balance, or runtime gates."
  - "Use when a game-dev agent needs to separate static evidence from Playtest-only validation before a handoff."
  - "Use when an RPG Maker MZ inventory is partial because implementation ownership, validation boundaries, or local evidence remain unmapped."
argument-hint: "[project_root, docs_index, focus_area, inventory_mode]"
arguments:
  required: []
  optional:
    - project_root
    - docs_index
    - focus_area
    - inventory_mode
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
  - Common Events, switches, variables, maps, plugins, plugin commands or save/load ownership are unknown
  - inventory findings require loki:tech-analysis before an agent can finish handoff
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-rpg-maker-mz-project-inventory/SKILL.md"
  references:
    checklist: "references/inventory-checklist.md"
    core_inventory: "references/core-inventory-checklist.md"
    game_dev_domains: "references/game-dev-domain-inventories.md"
shell: {}
type: skill
status: draft
---

# loki-rpg-maker-mz-project-inventory

## Purpose

Build a read-only evidence inventory of an RPG Maker MZ project so game-dev
agents can reason from local project facts instead of guessing runtime
ownership.

This skill is a guide for investigation. It does not impose its own report
format; preserve the response format of the active agent or command. Use the
inventory to state what was inspected, what was not inspected, which claims are
static only, and which next evidence requires Playtest, human review,
editor/runtime access, or `loki:tech-analysis`.

## Procedure

1. Resolve `project_root`.
   - Prefer a user-provided root when multiple RPG Maker MZ projects exist.
   - Otherwise use the directory containing `game.rmmzproject`, `index.html`,
     `data/`, and `js/`.
2. Read local routing guidance before implementation files:
   - root or project-local `AGENTS.md` / `CLAUDE.md`, when present;
   - durable docs index only when project guidance requires it;
   - never assume durable docs live under the RPG Maker MZ root.
3. Declare inventory mode before deep reading:
   - `minimal signature`: prove the RPG Maker MZ project shape;
   - `focused ownership`: map only surfaces tied to `focus_area`;
   - `full project inventory`: only when explicitly requested.
4. Confirm the RPG Maker MZ signature and primary surfaces:
   - `game.rmmzproject`, `data/System.json`, `data/CommonEvents.json`,
     `data/MapInfos.json`, `js/plugins.js`, and local `js/rmmz_*.js`;
   - database JSON, selected maps, plugin files, asset roots, save/local state,
     and local pipeline scripts when they affect understanding.
5. Parse structured surfaces with structured parsing, not regex, when the data
   matters: RPG Maker data JSON, `js/plugins.js`, plugin metadata, and event
   command lists.
6. Build only the ownership map needed for the mode:
   - switches, variables, Common Events, map/event callers, plugin commands,
     plugin parameters, helper-plugin logic, assets, save/load state, docs,
     validators, and human gates;
   - for `focus_area`, `complete` requires required ownership columns to be
     mapped or explicitly out of scope.
7. Use local engine source when command semantics matter.
   - Prefer relevant local `js/rmmz_*.js` interpreter, manager, scene, window,
     and storage methods over memory.
   - Use external or official RPG Maker documentation only when allowed and
     needed to resolve semantics not clear from local sources.
8. Classify evidence and confidence:
   - `parse-valid`, `editor-structural`, `engine-semantic`,
     `static-risk`, `runtime-pending`, `runtime-validated`;
   - list important sources not read because they were out of scope, too large,
     unavailable, unsafe, or required runtime/editor access.
9. Separate observations, interpretations, hypotheses, and recommendations.
   Inventory evidence can suggest a next action, but it is not a decision to
   promote standards, rewrite design, or implement fixes.
10. Preserve the active agent's response format. Add inventory findings only as
    the active task needs them; do not force a fixed Markdown section list.
11. When ownership crosses docs, maps, Common Events, plugins, assets, save/load
    or runtime behavior, and the active agent cannot finish safely, recommend
    `loki:tech-analysis` with a concrete focus, source list, unresolved
    boundary, and required validator or human gate.

## Gates And Limits

- Static inventory can map structure, ownership, references, risk, and likely
  behavior. It cannot validate visuals, input, audio, timing, Common Event
  execution, plugin behavior, gameplay feel, readability, sensitive-content
  handling, localization quality, or save/load compatibility.
- Require Playtest or another approved human validation gate before declaring
  runtime behavior, player comprehension, accessibility, mix, pacing, balance,
  route reachability, deployment, or save/load restoration valid.
- Use `loki-rpg-maker-mz-data-json` before editing `data/*.json`.
- Use `loki-rpg-maker-mz-plugin-workflow` before editing plugins or
  `plugins.js`.
- Do not write runtime, data, plugin, asset, save, generated, or installation
  target files while inventorying.
- Do not execute historical scripts, mutators, generators, cleanup scripts, or
  debug utilities during inventory; list and classify them only.
- Do not promote project-specific IDs, names, plugin names, map names,
  thresholds, story details, or feature behavior into package-wide rules.

## References

- Read `references/inventory-checklist.md` first to choose the smallest
  reference needed for the current mode and focus area.
- Read `references/core-inventory-checklist.md` for common RPG Maker MZ
  signature, structured parsing, System IDs, Common Events, maps, plugins,
  plugin commands, assets, save/load, pipeline scripts, drift, and escalation.
- Read `references/game-dev-domain-inventories.md` only when the focus area
  involves product/MVP, gameplay, level design, narrative, quest/content,
  dialogue, UX/UI, audio, technical art/assets, balance/economy,
  accessibility, or sensitive content.
