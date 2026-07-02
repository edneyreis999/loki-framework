# VisuStella Plugin Notetag Index

Use this index to route notetag work by plugin family. It is intentionally
compact; verify exact syntax against the target plugin reference before writing
consumer data.

## Core Engine

| Plugin | Common Notetag Topics | Typical Targets |
| --- | --- | --- |
| Core Engine | max/initial level, class learn levels, animation tags, enemy tags, battle tags, basic parameter tags, QoL tags, tileset tags | actors, classes, class learn entries, enemies, animations, tilesets |

## Battle

| Plugin | Common Notetag Topics | Typical Targets |
| --- | --- | --- |
| Battle Core | Action Sequence tags, animation, battle command, battle layout, battleback, critical, damage, enemy setup, HP gauge, life steal, mechanics, targeting, troop tags | skills, items, actors, classes, enemies, states, troops |
| Auto Skill Trigger | trigger conditions, trigger examples, automatic skill use setup | skills, states, trait-bearing objects |
| Active Turn Battle | ATB field gauges, gauge manipulation, general ATB tags, JavaScript ATB tags | actors, classes, enemies, skills, states |
| Aggro Control System | aggro, provoke, taunt, JavaScript aggro, quick-reference tags | actors, classes, skills, enemies, states |
| Battle AI | skill conditions, targeting, TGR weight, AI configuration | enemies, skills, states |
| Elements Status Menu Core | actor biography, elements, JavaScript elements, trait sets | actors, classes, enemies, states, equipment |
| Items and Equips Core | equipment tags, item accessibility, shop menu, status window, JavaScript item/equip tags | items, weapons, armors, actors, classes |
| Life State Effects | enemy-only, state-only, trait-object effects | enemies, states, trait-bearing objects |
| Skills and States Core | aura/miasma, passive states, skill accessibility, skill costs, general skills/states, slip damage/healing | skills, states, actors, classes, equipment, enemies |
| TP System | actor TP mode, general TP tags, TP quick reference | actors, classes, enemies, skills, states |
| Visual State Effects | breathing, hover, state visuals, quick-reference state visuals | states, enemies, actors |

## Gameplay And Movement

| Plugin | Common Notetag Topics | Typical Targets |
| --- | --- | --- |
| DragonBones Union | battler DragonBones setup, map sprites | actors, enemies, events |
| More Currencies | cost tags, proxy currency tags | skills, items, shops, database objects |
| Events and Movement Core | activation regions, click triggers, movement sync, encounters, labels, icons, sprite transforms, hitboxes, copied events, saved event location | maps, events, event pages, event comments |

## Quality Of Life

| Plugin | Common Notetag Topics | Typical Targets |
| --- | --- | --- |
| Database Inherit | inherited properties, traits, effects, damage formulas, enemy actions, broad object inheritance | database objects that support inheritance |
| Items and Equips Core | item/equipment menu behavior and accessibility | items, weapons, armors |

## Skill Progression

| Plugin | Common Notetag Topics | Typical Targets |
| --- | --- | --- |
| Equip Passive System | setup, hiding, masking, unlock conditions, Skill Learn integration | skills, states, actors, classes, equipment |
| Skill Learn System | AP/SP, learnable skills, display conditions, requirement conditions, learn costs, animation tags | actors, classes, skills |
| Skill Shop | skill shop availability, costs, visibility, shop entries | skills and shop-related data |

## Action Sequence Tags

Route Battle Core Action Sequence tags to
`rpg-maker-mz-visustella-action-sequences` when the task involves:

- `<Custom Action Sequence>`;
- `<Auto Action Sequence>`;
- `<Bypass Auto Action Sequence>`;
- `<Common Event: name>`;
- `<Common Event Key: name>` or multiple common event keys;
- Common Events that contain Battle Core Action Sequence plugin commands.
