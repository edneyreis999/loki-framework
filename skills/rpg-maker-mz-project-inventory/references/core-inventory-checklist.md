# Core RPG Maker MZ Inventory Checklist

Use this reference for the shared RPG Maker MZ evidence pass. Keep the inventory
read-only and focused on the active task.

## Minimal Project Signature

Confirm the local project root with:

- `game.rmmzproject`;
- `index.html`;
- `package.json`, when NW.js/browser launch context matters;
- `data/System.json`;
- `data/CommonEvents.json`;
- `data/MapInfos.json`;
- `js/plugins.js`;
- local `js/rmmz_core.js`, `js/rmmz_objects.js`, `js/rmmz_managers.js`,
  `js/rmmz_scenes.js`, `js/rmmz_windows.js`, and `js/rmmz_sprites.js` when
  command, save, UI, or rendering semantics matter.

## Routing And Durable Context

- Read project routing docs before runtime files when present.
- Use routing docs to locate durable project documentation; nested RPG Maker MZ
  projects may rely on workspace-level docs.
- Treat durable docs, routing notes, historical plans, and scratch notes as
  different evidence classes. Do not promote exploratory material as durable
  context without an explicit workflow or human decision.
- Record whether evidence is only inventoried statically or is already
  represented in durable project documentation.

## Structured Parsing

Use structured parsing for:

- `data/*.json`;
- selected `MapXXX.json` files;
- `js/plugins.js` as RPG Maker generated plugin configuration;
- plugin headers/metadata and `PluginManager.registerCommand` calls when plugin
  command ownership matters.

Do not rely on ad hoc regex for semantic claims. Text search is acceptable for
candidate discovery, but confirm important ownership with structured data or
local source inspection.

## System Inventory

From `data/System.json`, capture only fields relevant to the mode:

- game title, locale/language evidence, resolution/UI settings when visible;
- start map ID and coordinates;
- switch names and IDs;
- variable names and IDs;
- terms/messages when UI text, localization, product identity, or default engine
  leakage is in scope;
- autosave/configuration settings when save/load or QA is in scope.

Report editor IDs, not only array indexes. In RPG Maker data arrays, editor ID
`N` usually maps to array index `N`.

## Common Event Inventory

From `data/CommonEvents.json`, capture:

- ID, name, trigger, and owner switch;
- command-code summary;
- incoming callers from maps, other Common Events, troop events, or plugin
  commands when in scope;
- outgoing Common Event calls (`code: 117`);
- plugin commands (`code: 357`);
- scripts, switches, variables, self-switches, transfers, pictures, audio,
  waits, input locks, and result/retry/cleanup paths when relevant.

Parallel and autorun Common Events are runtime-sensitive. For a focused feature,
map trigger switch, active state flags, cleanup path, retry/re-entry path, and
terminal/result path before treating the graph as complete.

## RPG Maker Command Codes To Track

Track command codes by purpose when relevant to ownership:

- Common Event calls: `117`;
- plugin commands: `357`;
- switch and variable operations;
- conditional branches, labels, jumps, loops, waits, scripts, and comments when
  they affect flow review;
- transfers, battle processing, shop processing, timers, pictures, animations,
  audio, text, choices, scrolling text, and movement routes;
- economy/progression commands such as gold, item, weapon, armor, EXP, level,
  parameter, and skill changes.

Command histograms are discovery aids, not validation.

## Map Inventory

From `data/MapInfos.json` and selected `MapXXX.json` files, capture:

- map ID, name, parent/order evidence, and likely role when focus requires it;
- event IDs/names, pages, page conditions, self-switches, triggers, priority,
  movement, and parallel/autorun use;
- Common Event calls, plugin commands, transfers, scripts, switches, variables,
  pictures, audio, text, choices, battles, shops, and timers;
- incoming and outgoing transfers for focused flows;
- maps intentionally not read.

Only deep-read maps relevant to the focus area unless a full project inventory
is explicitly requested. Large maps may remain `structural-only` until a
dedicated pass or Playtest validates behavior.

## Plugin Inventory

From `js/plugins.js`, capture:

- active and inactive plugins;
- order;
- parameters that affect the focus area;
- custom project plugins versus vendor plugins;
- plugin-managed assets, UI, input, save/autosave, preload/cache/focus, debug,
  and broad runtime patches.

From selected plugin files, capture:

- plugin header metadata and `@command` declarations;
- `PluginManager.registerCommand` registrations;
- command argument handling;
- global namespaces;
- prototype/class patches;
- helper-plugin design logic: thresholds, formulas, RNG, input mappings,
  timers, state transitions, win/loss checks, debug flags, and exposed globals;
- dependencies on RPG Maker classes, plugin order, or other plugins.

Treat vendor, minified, obfuscated, or very large plugins as lower-confidence
until a dedicated pass or runtime validation covers behavior.

## Plugin Command Cross-Reference

For plugin commands relevant to the focus area, capture both directions:

- commands registered by selected plugin files;
- commands invoked by event data;
- plugin name and command name;
- caller location: Common Event, map event, troop event, script, or unknown;
- visible arguments;
- active plugin status, order, and parameter dependencies;
- whether command semantics were confirmed from local plugin or engine source.

Do not claim plugin command ownership from registration text alone when command
registration is indirect, wrapped, generated, or vendor-hidden.

## Local Engine Source

When command semantics, save/load, UI, input, rendering, or storage behavior
matter, inspect local engine source before relying on memory:

- interpreter command methods for event command behavior;
- `DataManager`, `StorageManager`, `ConfigManager`, `Scene_*`, `Window_*`,
  `Sprite_*`, and input/touch managers as relevant;
- save content creation/restoration and storage backend when persistence matters.

External documentation may be used only when allowed and needed to resolve
semantics, plugin annotation behavior, or asset standards not clear locally.

## Asset Reference Inventory

Prefer referenced assets over folder counts when behavior depends on assets.
Capture:

- reference source: event command, database field, plugin parameter, script,
  plugin command, map event graphic, or docs;
- path or RPG Maker asset name;
- asset family and likely runtime role;
- existence, extension, case sensitivity risk, dimensions when useful, and
  static risk flags.

Check relevant roots without reading binaries in full:

- `img/pictures`, `img/characters`, `img/faces`, `img/system`,
  `img/tilesets`, `img/battlebacks1`, `img/battlebacks2`, `img/titles1`,
  `img/titles2`;
- `audio/bgm`, `audio/bgs`, `audio/me`, `audio/se`;
- `effects`;
- `movies`;
- `fonts`;
- `save`.

When in scope:

- cross-check `Animations.json` effect names against `effects/*.efkefc`;
- cross-check tileset slot usage against expected local image dimensions;
- estimate uncompressed RGBA texture cost for large or scene-critical images;
- identify plugin-owned pictures, text pictures, button pictures, bust systems,
  preload lists, generated filenames, and dynamic asset references.

File existence is static evidence only. Loading, decode, timing, volume, fade,
cache behavior, visual fit, animation playback, and performance remain runtime
validation items.

## Save/Load Ownership

When behavior, QA, compatibility, or regression risk depends on persistence,
inventory:

- existing save files and local storage surfaces;
- autosave, config/global save data, and package/NW.js context;
- persisted switches, variables, map state, player state, inventory, pictures,
  audio, and plugin state when visible;
- relevant `DataManager`, `StorageManager`, `makeSaveContents`, and
  `extractSaveContents` behavior;
- before/after states for focus features;
- compatibility risk after data, plugin, or event changes.

Treat save files and persisted state as compatibility surfaces until the user
defines them as disposable.

## Pipeline Script Inventory

Local scripts and tools may explain project state, but inventory must not run
historical or mutating scripts.

List and classify discovered scripts only when relevant:

- `read-only`;
- `validator`;
- `mutator`;
- `historical-generator`;
- `cleanup/debug utility`;
- `deployment/export`;
- `unknown`.

Mark mutators, unknown scripts, cleanup tools, historical generators, and debug
utilities as requiring explicit approval before any future use.

## Static Validator Baseline

Name validators as candidate checks, not proof of runtime behavior:

- parse relevant `data/*.json`;
- parse `js/plugins.js` as structured plugin configuration;
- run JavaScript syntax checks on selected plugin files when tooling is
  available;
- summarize command-code histograms and plugin-command cross-references;
- count asset/save surfaces and cross-check referenced assets;
- scan inspected scripts/plugins for `eval`, `new Function`, `require`, `fs`,
  `child_process`, debug flags, console shortcuts, DevTools hooks, and broad
  global runtime exposure when security or release readiness is in scope.

JSON validity, editor recognition, engine semantics, and Playtest behavior are
separate claims.

## Security, Debug, And Deployment Surfaces

When release, deployment, security, or pipeline readiness is in scope, inventory:

- debug logs, console shortcuts, test hooks, development-only plugin parameters,
  and exposed globals;
- dynamic evaluation or Node/NW API access in plugins or scripts;
- untrusted plugin parameters, script calls, imported data, or generated files;
- unused-file exclusion, encrypted assets, plugin-managed assets, package/NW.js
  context, and required post-export smoke checks.

Do not treat untrusted runtime data as safe without a specific validation gate.

## Doc-Runtime Drift

Compare durable guidance and runtime files when the focus depends on it:

- docs or routing claim;
- static runtime evidence from `System.json`, Common Events, maps, plugins,
  assets, or save/load;
- status: `unknown`, `not checked`, `aligned`, `conflict`, `ambiguous`, or
  `pending validation`;
- unresolved source of truth.

Record conflicts without choosing authority unless the source of truth is
explicit.

## Readiness Snapshot

Use a compact snapshot only if it helps the active response:

- signature and project root;
- inventory mode and focus;
- inspected sources;
- uninspected important sources;
- ownership boundary status;
- evidence level;
- required validators and human gates;
- smallest next read or Playtest path.

Do not convert this into a universal report format.

## Escalation To loki:tech-analysis

Recommend `loki:tech-analysis` when:

- ownership crosses maps, Common Events, plugins, assets, docs, and save/load;
- implementation differs from durable docs or product promise;
- plugin command semantics, helper-plugin logic, save/load, deployment, or
  runtime behavior is material;
- the active agent cannot complete handoff without deeper source inspection;
- the next step would require design or implementation strategy.

Include focus, source list, unresolved boundary, and validation gate.
