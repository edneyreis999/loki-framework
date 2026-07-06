# Message Core Localization Workflow

Use this reference when implementing, reviewing, or migrating localization with
VisuStella MZ Message Core in an RPG Maker MZ consumer project.

## Preflight

1. Confirm the project is RPG Maker MZ.
2. Inventory active plugins from `js/plugins.js`; do not rely only on plugin
   files existing under `js/plugins/`.
3. Find every active plugin entry whose name is `VisuMZ_1_MessageCore`.
4. If no active Message Core entry exists, stop and report that this skill does
   not apply yet.
5. If more than one active Message Core entry exists, inspect all of them and
   keep their localization settings synchronized unless the user explicitly
   approves a different runtime architecture.

## Parsing `Localization:struct`

RPG Maker MZ plugin parameters commonly persist structs as JSON strings inside
the `parameters` object. Parse recursively enough to inspect nested structs and
lists instead of searching raw strings.

For each active `VisuMZ_1_MessageCore` entry, extract:

- `Enable`;
- `DefaultLocale`;
- configured language list;
- `LangFiletype:str`;
- `CsvFilename:str`;
- `TsvFilename:str`;
- Options language display fields when the task touches the Options menu.

Normalize booleans and strings for comparison, but preserve original casing and
values when writing back. Treat missing, disabled, unsupported, or disagreeing
fields as structural failures until resolved.

## Effective Runtime Table

Use `LangFiletype:str` as the source of truth for format selection.

| `LangFiletype:str` | Effective filename field | Required parser |
| --- | --- | --- |
| `csv` | `CsvFilename:str` | semicolon-delimited CSV |
| `tsv` | `TsvFilename:str` | tab-delimited TSV |

Do not decide format from `<language-table>.csv`,
`<language-table>.tsv`, or any filename suffix alone. A project can have stale
files, migration leftovers, backup tables, or mismatched parameter values.

Prefer one runtime table in `data/` when the consumer does not have an approved
build pipeline. Source tables for translators can exist only when the final
runtime table and source-of-truth ownership are explicit.

## Language Table Shape

The first column must be `Key`. Remaining columns should match the configured
Message Core languages that are expected to render at runtime.

Validate:

- every row has the same number of columns as the header;
- keys are non-empty;
- keys are unique after trimming and case-normalization, because Message Core
  key lookup is case-insensitive in supported documentation;
- the `DefaultLocale` column exists;
- every configured runtime language that should be selectable has a column;
- required player-facing keys have non-empty values for the locales in scope.

For CSV, use semicolon as the delimiter unless the installed Message Core
documentation or project evidence proves a different delimiter. For TSV, reject
literal tab characters inside cells unless the table parser can escape them
without changing column count.

## Converting Player-Facing Text

Use `\tl{key}` for localized player-facing text. Keep key names stable,
readable, and deterministic within the project's naming convention.

Good target surfaces commonly include:

- Show Text event command strings;
- choices and choice help text;
- player-facing system terms and menu labels;
- item, weapon, armor, skill, enemy, troop, class, actor, or state names and
  descriptions when they are displayed to the player;
- tutorial text, signs, books, notices, and quest text stored in maps or Common
  Events.

Avoid converting:

- internal identifiers, switches, variables, filenames, asset names, plugin
  command names, formulas, script bodies, note tags, or machine-facing fields
  unless the project explicitly treats them as player-facing;
- text in a window or plugin surface that does not process Message Core text
  codes, unless runtime evidence confirms support.

Preserve RPG Maker MZ structure. Edit JSON through structured parsing, keep
event command codes and parameter arrays valid, and avoid broad search/replace
across `data/*.json`.

## Coordinated Writes

When implementing localization in one change, keep these surfaces coordinated:

- all active Message Core `Localization:struct` entries;
- the effective runtime language table;
- every `\tl{key}` reference introduced in player-facing data;
- validators and Playtest handoff status.

If a migration changes CSV to TSV or TSV to CSV, update all active Message Core
entries, create the new effective table, remove or clearly demote stale runtime
tables, then run structural validation and browser smoke before Playtest.
