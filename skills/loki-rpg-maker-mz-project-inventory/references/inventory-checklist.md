# RPG Maker MZ Project Inventory Checklist

Use this checklist to keep RPG Maker MZ inventory work concrete and bounded.

## Minimal Project Signature

- `game.rmmzproject`
- `index.html`
- `package.json`, when NW.js/browser launch context matters
- `data/System.json`
- `data/CommonEvents.json`
- `data/MapInfos.json`
- `js/plugins.js`
- `js/rmmz_core.js`
- `js/rmmz_objects.js`
- `js/rmmz_managers.js`

## System Inventory

From `data/System.json`, capture:

- game title;
- locale/language evidence when present;
- start map ID and coordinates;
- switch names and IDs for the requested range;
- variable names and IDs for the requested range;
- terms/messages only when UI text or localization is in scope.

Always report editor IDs, not only array indexes. In RPG Maker data arrays,
editor ID `N` usually maps to array index `N`.

## Common Event Inventory

From `data/CommonEvents.json`, capture:

- ID;
- name;
- trigger;
- switch ID for parallel/autorun events;
- command code histogram;
- calls to other Common Events (`code: 117`);
- script/plugin command usage;
- picture/audio/map transfer commands when relevant.

Do not rewrite command lists during inventory.

## Common Event Graph

For the focus area, build a read-only graph of event ownership:

- Common Event ID and name;
- incoming callers from map events, other Common Events or plugin commands;
- outgoing Common Event calls (`code: 117`);
- switches and variables read or written by the event;
- plugin commands, scripts, transfers, picture and audio commands that affect
  runtime behavior;
- unknown callers or uninspected maps that keep the graph partial.

If graph edges cross maps, plugins and Common Events, recommend
`loki:tech-analysis` before implementation.

## Map Inventory

From `data/MapInfos.json` and selected `MapXXX.json` files, capture:

- map ID and name;
- event names;
- event pages with conditions;
- Common Event calls;
- plugin commands;
- transfers;
- switches/variables touched by the focus area.

Only deep-read maps relevant to the focus area unless the task is explicitly a
full project inventory.

## Plugin Inventory

From `js/plugins.js`, capture:

- active plugins;
- inactive plugins;
- order;
- parameters that affect the focus area;
- custom project plugins versus vendor plugins.

From selected plugin files, capture:

- plugin commands registered;
- global namespaces exposed;
- methods patched;
- dependencies on RPG Maker classes or other plugins.

Use `loki-rpg-maker-mz-plugin-workflow` before any plugin edit.

## Plugin Command Inventory

For plugin commands relevant to the focus area, capture:

- plugin name and command name;
- command arguments when visible in event data;
- caller location: Common Event, map event, troop event or script;
- local plugin file that registers the command, when custom code exists;
- parameter dependencies from `js/plugins.js`.

Treat plugin command behavior as runtime-sensitive until Playtest or another
approved human validation gate confirms it.

## Asset And Save Surfaces

Capture counts or paths, not full binary reads:

- `img/pictures`, `img/characters`, `img/system`, `img/tilesets`;
- `audio/bgm`, `audio/bgs`, `audio/me`, `audio/se`;
- `effects`;
- `movies`;
- `fonts`;
- `save`.

If behavior depends on asset loading, mark Playtest/human validation as
required.

## Focus-Area Ownership Map

For a feature such as a race minigame, map:

- durable docs that define the feature;
- switches and variables;
- Common Events;
- maps and local events;
- plugins and plugin parameters;
- pictures/audio/effects;
- save/load state;
- validators and human gates.

If any of these are unknown, the inventory is `partial`, not `complete`.

## Feature Ownership Matrix

For each focus feature, produce a compact matrix with these columns:

- durable docs that define expected behavior;
- switches and variables;
- Common Events and graph status;
- map callers and local events;
- plugin commands, plugin parameters and custom plugin files;
- pictures, audio, effects, fonts or other assets;
- save/load surfaces and persisted variables;
- validators and required human gates;
- missing evidence and next command, usually `loki:tech-analysis` when the
  ownership boundary is still unclear.

## Doc-Runtime Drift

When durable docs and implementation disagree or cannot be reconciled statically,
record:

- doc source and expected behavior;
- runtime source and observed static evidence;
- mismatch, ambiguity or missing source;
- validation needed before treating either side as authoritative.

## Escalation To loki:tech-analysis

Recommend `loki:tech-analysis` when:

- ownership crosses maps, Common Events and plugins;
- implementation differs from durable docs;
- save/load or runtime behavior is material;
- an agent cannot complete a required handoff without deeper source inspection;
- the next step would require deciding design or implementation strategy.

Include a concrete focus, for example:

```text
loki:tech-analysis focus="Map race minigame ownership across System IDs, Common Events, map callers, Jhonny_RaceHelper and result-screen validation gates"
```

## Runtime Validation Boundary

Static inventory can identify structure and risk. It cannot validate:

- visuals;
- input;
- audio;
- event timing;
- plugin command behavior;
- Common Event execution;
- save/load compatibility;
- gameplay feel.

Those require human Playtest evidence.
