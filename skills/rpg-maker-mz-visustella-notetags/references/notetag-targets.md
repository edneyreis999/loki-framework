# VisuStella Notetag Targets

Use this reference to choose the correct RPG Maker MZ data surface before
generating, reviewing, or locating VisuStella tags.

## Target Map

| Target | Typical File | Surface | Notes |
| --- | --- | --- | --- |
| Actors | `data/Actors.json` | actor `note` field | actor growth, level, battle presentation, TP, AP/SP, state visuals, equipment/passive routing |
| Classes | `data/Classes.json` | class `note` field and class learn data | learn level, skill learning, requirements, trait behavior |
| Skills | `data/Skills.json` | skill `note` field and skill effects | costs, targeting, Action Sequence tags, skill learning, accessibility, animations |
| Items | `data/Items.json` | item `note` field and effects | item access, shop behavior, Action Sequence tags, currency costs |
| Weapons | `data/Weapons.json` | weapon `note` field | equipment behavior, trait sets, passive/equip conditions |
| Armors | `data/Armors.json` | armor `note` field | equipment behavior, trait sets, passive/equip conditions |
| Enemies | `data/Enemies.json` | enemy `note` field and enemy actions | AI, targeting, aggro, TP, battle presentation, database inherit |
| States | `data/States.json` | state `note` field | passive states, visual state effects, life state effects, slip damage/healing, aura/miasma |
| Troops | `data/Troops.json` | troop notes/events where supported | troop tags, battle setup, event-driven commands |
| Maps | `data/MapInfos.json` and map JSON | map note field where supported | map-level movement, encounter, event template, presentation behavior |
| Events | map JSON pages/events | event note and comment tags | event activation, movement, labels, icons, sprites, hitboxes, pictures, copied events |
| Event Pages | map JSON event page command lists | comment tags on a page | page-specific event behavior; use only when plugin distinguishes comments from event notes |
| Common Events | `data/CommonEvents.json` | command lists, not note fields | use plugin-command or Action Sequence skill for command payloads |

## Write Gate

Any write to these surfaces requires `rpg-maker-mz-data-json` first:

- `data/*.json`;
- actor/class/skill/item/weapon/armor/enemy/state note fields;
- map, event, page, troop, or Common Event command lists;
- structured event comments used as comment tags.

## Comment Tag Distinction

Some VisuStella event systems accept the same text as:

- an event notetag that affects all pages of the event;
- a comment tag that affects only the event page containing that comment.

When the target is an event page, confirm whether the plugin accepts comment
tags and whether a note-only tag is required.

## Object Evidence Checklist

Before proposing a tag, identify:

1. object type;
2. object ID or name in the current project;
3. plugin that owns the tag;
4. active plugin evidence;
5. exact note/comment surface;
6. required runtime validation.
