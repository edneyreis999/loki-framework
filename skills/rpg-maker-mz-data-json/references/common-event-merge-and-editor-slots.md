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

Before writing into a newly approved slot, parse the current
`CommonEvents.json` from disk and confirm the target ID already exists. If the
slot is missing, stop and ask for the RPG Maker editor state to be saved or for
an explicit editor-slot creation step. Do not infer that a user-approved slot is
available until it exists in the saved JSON.

When the slot exists, confirm it is empty or exactly in the expected pre-write
state before overwriting contents. If it already contains unexpected commands,
names, triggers or switches, stop for a merge decision instead of replacing it
silently.

## Remap Audit

Search all maps and Common Events for Common Event calls, not only the file being edited. A partial remap can leave maps calling the wrong behavior while the edited CE looks correct in isolation.

## Recovery

Use scoped restores or targeted rewrites for failed merges. Do not use broad cleanup commands as part of normal merge recovery in a workspace with untracked plans, assets, or local agent artifacts.
