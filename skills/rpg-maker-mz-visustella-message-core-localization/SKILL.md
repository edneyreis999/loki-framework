---
name: rpg-maker-mz-visustella-message-core-localization
description: Use when implementing, reviewing, or validating RPG Maker MZ localization with VisuStella MZ Message Core Text Language Switching, Localization:struct, language CSV/TSV files, LangFiletype:str, \tl{key} references, Options language switching, browser smoke, or Playtest/LQA gates.
when_to_use:
  - "Use for VisuStella MZ Message Core Text Language Switching, Localization:struct, language CSV/TSV runtime tables, LangFiletype:str, CsvFilename:str, TsvFilename:str, DefaultLocale, configured languages, or \\tl{key} references."
  - "Use before changing Message Core localization parameters in js/plugins.js or converting RPG Maker MZ player-facing text to localization keys."
  - "Use when validating localization structure, browser loading of the effective language file, Options language switching, or human Playtest/LQA status."
argument-hint: "[project_root, language_table, target_surfaces, intended_change]"
arguments:
  required: []
  optional:
    - project_root
    - language_table
    - target_surfaces
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
  - localization parameters in js/plugins.js may be changed
  - player-facing RPG Maker MZ data, maps, events, choices, database names, or system terms may be changed
  - browser smoke or Playtest/LQA is required before closing runtime behavior
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-visustella-message-core-localization/SKILL.md"
  references:
    localization_workflow: "references/localization-workflow.md"
    validation_checklist: "references/validation-checklist.md"
shell: {}
type: skill
status: optional-extension
extension: "RPG Maker MZ VisuStella"
---

# rpg-maker-mz-visustella-message-core-localization

## Purpose

Guide RPG Maker MZ work that uses VisuStella MZ Message Core localization:
Text Language Switching, `Localization:struct`, runtime language CSV/TSV
tables, `\tl{key}` references, Options language switching, and validation
before human Playtest.

This skill is semantic guidance only. It does not authorize writes to consumer
RPG Maker MZ data, maps, events, plugin parameters, plugin files, assets, save
files, generated files, or runtime surfaces.

## Procedure

1. Confirm the work is RPG Maker MZ and that VisuStella MZ Message Core is
   installed, active, named, or likely relevant. Use
   `rpg-maker-mz-project-inventory` when project root, active plugins,
   `js/plugins.js`, target data files, or runtime surfaces are unknown.
2. Before any write:
   - use `rpg-maker-mz-plugin-workflow` for `js/plugins.js`, Plugin Manager
     parameters, plugin activation, load order, helper plugins, or plugin files;
   - use `rpg-maker-mz-data-json` for `data/*.json`, maps, events, Common
     Events, event command lists, choices, note fields, system terms, database
     objects, enemies, troops, items, skills, weapons, or armor.
3. Read `references/localization-workflow.md` before implementing or reviewing
   Message Core localization.
4. Parse `js/plugins.js` structurally and inspect every active
   `VisuMZ_1_MessageCore` entry. Treat multiple active entries as a single
   configuration set that must stay synchronized.
5. Parse `Localization:struct` for each active Message Core entry. Validate
   `Enable`, `DefaultLocale`, configured languages, `LangFiletype:str`, and the
   effective filename selected by `LangFiletype:str`.
6. Do not infer CSV or TSV from the filename alone. Use `LangFiletype:str` as
   the source of truth, then require the matching filename field and table
   parser.
7. Prefer one runtime language table unless the consumer has an explicit
   approved pipeline that builds the final table from other sources. Avoid
   leaving two plausible runtime sources without a clear source of truth.
8. Convert player-facing text to `\tl{key}` only through structured edits that
   preserve RPG Maker MZ JSON shape, event command parameters, message/choice
   structure, database IDs, and non-player-facing technical fields.
9. Read `references/validation-checklist.md` before declaring implementation
   complete, review-passed, or ready for Playtest.
10. Separate validation statuses:
    - structural validation for JSON, plugin parameters, table structure,
      unique keys, and `\tl{...}` coverage;
    - browser smoke for loading the effective language file and detecting boot
      or request errors;
    - human Playtest/LQA for Options language switching, runtime rendering, and
      readability.

## Inputs

- RPG Maker MZ project root or project inventory evidence.
- Message Core plugin evidence, `js/plugins.js`, localization parameters, or
  target language table.
- Target player-facing surfaces and intended operation: implementation,
  review, diagnosis, migration, validation, or Playtest handoff.

## Outputs

- Message Core localization configuration assessment.
- Runtime language table route and format decision based on `LangFiletype:str`.
- Required write gates for plugin parameters and RPG Maker MZ data JSON.
- Structural validation result, browser smoke result, and explicit human
  Playtest/LQA status.

## References

- Read [localization-workflow.md](references/localization-workflow.md) before
  implementing, reviewing, or migrating Message Core localization.
- Read [validation-checklist.md](references/validation-checklist.md) before
  marking localization structurally valid or ready for Playtest.

## Limits

- Do not create a parallel localization system when Message Core localization is
  the accepted mechanism.
- Do not make any locale, language pair, CSV, or TSV format mandatory for all
  projects.
- Do not assume `CsvFilename:str` or `TsvFilename:str` controls runtime by
  itself; check `LangFiletype:str`.
- Do not update consumer projects, `.codex/**`, `.agents/**`, or `.claude/**`
  from this package skill.
- Do not declare runtime localization, Options behavior, or readability
  validated without human Playtest/LQA evidence.
