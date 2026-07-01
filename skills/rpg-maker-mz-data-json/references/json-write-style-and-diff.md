# JSON Write Style And Diff

Use this reference before automated edits to RPG Maker MZ `data/*.json`.

## Principle

Preserve the target file's structure and style. A valid JSON parse is necessary but not sufficient. A writer that reflows a whole file makes review unsafe and can hide unintended changes.

## Workflow

1. Parse the target JSON.
2. Detect local style before writing:
   - indentation width;
   - trailing newline;
   - ASCII escaping behavior;
   - line layout of large arrays or objects.
3. Apply the smallest structured change.
4. Serialize with the detected style.
5. Parse the written file again.
6. Review diff before proceeding.
7. Stop and repair the writer if unrelated lines reflow.

## Diff Gate

The diff should be explainable in terms of the requested IDs and fields. If thousands of lines change because of indentation or escaping, revert that write with a scoped restore and rewrite with the correct style.

## Project-Local Facts

Do not bake one project's indentation into this package skill. Store project-local writer facts in the consumer project docs. The reusable rule is to detect and preserve style.
