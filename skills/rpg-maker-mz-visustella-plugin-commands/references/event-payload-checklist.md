# VisuStella Event Payload Checklist

Use this checklist before proposing or reviewing a plugin command payload.

## Evidence Required

- Active plugin name that owns the command.
- Event surface: map event, event page, troop event, Common Event, or Action
  Sequence Common Event.
- Event ID/name, page index if relevant, troop ID/name if relevant, or Common
  Event ID/name.
- Current caller chain when a Common Event is triggered from another event or a
  skill/item effect.
- Required IDs/names for actors, enemies, skills, states, items, weapons,
  armors, variables, switches, pictures, maps, events, animations, or Common
  Events referenced by the command.

## Payload Review

1. Confirm the command belongs to an active plugin.
2. Confirm command arguments match the plugin command definition and expected
   target type.
3. Confirm IDs/names exist in the current project data.
4. Confirm command ordering relative to waits, branches, labels, loops, and
   cleanup.
5. Preserve event list structure. Do not use ad hoc string replacement for
   event command JSON.
6. For commands that affect battle, input, pictures, save/autosave, movement,
   messages, or UI, keep runtime validation pending until Playtest.

## Gate Mapping

- Review-only: project evidence can be read, but no writes are authorized.
- Event payload write: use `rpg-maker-mz-data-json`.
- Plugin command definition or registration write: use
  `rpg-maker-mz-plugin-workflow`.
- Action Sequence command list: use this checklist plus
  `rpg-maker-mz-visustella-action-sequences`.

## Stop Conditions

Stop and request more evidence when:

- the owning plugin is unknown;
- the command exists only in inactive plugin docs;
- event target IDs are missing;
- a command is being inserted into runtime-critical flow without Playtest gate;
- the task would edit plugin implementation or activation without
  `rpg-maker-mz-plugin-workflow`.
