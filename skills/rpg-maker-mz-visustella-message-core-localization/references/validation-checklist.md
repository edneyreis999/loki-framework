# Message Core Localization Validation Checklist

Use this checklist before marking VisuStella MZ Message Core localization as
structurally valid or ready for human Playtest.

## Structural Validation

Run these checks before browser smoke:

1. `json-parse`: every changed `data/*.json` file parses.
2. `plugins-parse`: `js/plugins.js` loads enough to inspect `$plugins` without
   executing the game runtime.
3. `message-core-active`: every active `VisuMZ_1_MessageCore` entry is found.
4. `localization-struct`: every active Message Core entry has parseable
   `Localization:struct`.
5. `message-core-sync`: all active Message Core entries agree on `Enable`,
   `DefaultLocale`, configured languages, `LangFiletype:str`, and effective
   filename.
6. `effective-file`: `LangFiletype:str` selects a supported format and the
   corresponding filename field points to an existing file in `data/`.
7. `table-structure`: the effective CSV/TSV header starts with `Key`, locale
   columns match the configured runtime languages in scope, and every row has
   the expected number of columns.
8. `unique-keys`: keys are non-empty and unique after trim plus
   case-normalization.
9. `tl-key-reference`: every `\tl{...}` reference in changed or target
   player-facing files resolves to a key in the effective table.
10. `single-runtime-language-file`: pass when only one runtime table is
    configured or when any extra table is explicitly non-runtime source data.

Structural validation can prove parseability, configuration consistency, table
shape, and lookup coverage. It does not prove readability or runtime behavior.

## Browser Smoke

After structural validation, run a lightweight browser smoke when feasible:

- serve the RPG Maker MZ project locally;
- open the game entrypoint in a browser automation tool;
- confirm the page reaches the title or first expected boot state;
- confirm the effective language file selected by `LangFiletype:str` returns
  HTTP 200;
- confirm stale alternate runtime files are not requested unexpectedly;
- record unrelated existing console or request errors separately from
  localization failures.

Browser smoke validates boot and file loading. It does not validate Options
workflow, language switching, text layout, line breaks, fonts, or LQA.

## Human Playtest/LQA Gate

Keep the human Playtest/LQA gate open until a human validates:

- Options shows the language command when the project expects one;
- the default language matches `DefaultLocale`;
- switching to each configured runtime language works without restart unless
  the project intentionally requires restart;
- messages, choices, menu terms, database names, enemy/troop names, item
  descriptions, and target quest or scene text render through the expected
  localized values;
- no unexpected literal `\tl{...}` appears in player-facing UI;
- line breaks, text speed, word wrap, fonts, glyph coverage, and window layout
  are readable for the languages in scope.

A positive qualitative comment is useful feedback, but do not convert it into
closed runtime validation unless it explicitly covers the Options flow, language
switching, and representative localized surfaces.

## Failure Handling

When a check fails:

- report the exact failing surface and whether it is structural, browser smoke,
  or human validation;
- do not hide mismatches by changing only filenames or only table files;
- fix `LangFiletype:str`, the matching filename field, and table format as a
  coordinated set;
- keep unrelated runtime errors in a residual-risk section instead of treating
  them as localization proof.
