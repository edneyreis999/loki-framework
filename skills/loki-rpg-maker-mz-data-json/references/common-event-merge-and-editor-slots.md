# Common Event Merge And Editor Slots

Use this reference when creating, moving, renumbering, or merging Common Events in RPG Maker MZ data.

## JSON Valid Is Not Enough

The RPG Maker MZ editor may reject or ignore slots created only by script even when `CommonEvents.json` parses. Treat editor recognition and Playtest as separate gates from JSON syntax.

## Slot Workflow

1. Inventory current Common Event ids and names.
2. Choose target ids and preserve existing ids unless the task explicitly requires remapping.
3. When adding new CEs, prefer having the editor create empty slots first if the consumer project relies on editor-managed database structure.
4. Overwrite slot contents with structured JSON while preserving the real ids.
5. Remap every caller that uses `code:117` to the new ids.
6. Parse JSON, open/validate in editor when required, then Playtest affected routes.

## Remap Audit

Search all maps and Common Events for Common Event calls, not only the file being edited. A partial remap can leave maps calling the wrong behavior while the edited CE looks correct in isolation.

## Recovery

Use scoped restores or targeted rewrites for failed merges. Do not use broad cleanup commands as part of normal merge recovery in a workspace with untracked plans, assets, or local agent artifacts.
