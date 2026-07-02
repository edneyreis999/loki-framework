# VisuStella Notetag Validation Checklist

Use this checklist before writing or reviewing a VisuStella tag.

## Structural Checks

- Confirm the owning plugin and active plugin evidence.
- Confirm the target object type supports the tag.
- Confirm the exact object ID/name in the current project.
- Confirm whether the tag belongs in a note field or an event-page comment.
- Preserve existing note text; do not reflow unrelated tags.
- Keep opening and closing tags paired for block syntax.
- For comma-separated values, IDs, names, or formulas, confirm the current
  project data uses those IDs/names.

## Gate Checks

- Any note-field or comment write requires `rpg-maker-mz-data-json`.
- If the tag references plugin parameters, plugin activation, or load order,
  also use `rpg-maker-mz-plugin-workflow`.
- If the tag triggers plugin commands or Common Events, also use
  `rpg-maker-mz-visustella-plugin-commands` or the Action Sequence skill.
- Runtime effects remain pending until Playtest or another approved human
  validation gate.

## Domain Checks

| Tag Intent | Extra Checks |
| --- | --- |
| Cost, requirement, AP/SP, currency, shop | verify resource IDs, plugin ownership, and progression/economy route when available |
| Battle targeting, damage, criticals, life steal, TP, aggro, AI | verify battle plugin ownership and Playtest gate |
| Passive states, aura, miasma, visual states | verify state IDs and whether the tag belongs on state, skill, actor, class, equipment, or enemy |
| Event movement, copied events, labels, icons, hitboxes | verify map/event/page target and comment-vs-note scope |
| Action Sequence | verify skill/item note field, Common Event linkage, `MECH: Action Effect` when damage/heal/effects must apply, and Playtest gate |

## Stop Conditions

Stop and request more project evidence when:

- VisuStella is not confirmed active but the requested behavior depends on it;
- the same tag could belong to multiple plugins and no plugin/family is known;
- the object ID/name is missing;
- the write target is unknown;
- runtime proof is required but no human validation gate exists.
