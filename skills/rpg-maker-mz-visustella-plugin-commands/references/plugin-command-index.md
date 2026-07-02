# VisuStella Plugin Command Index

Use this index to route command work by plugin or family. It is a summary for
choosing context, not a complete command manual.

## Core Engine

| Plugin | Command Areas |
| --- | --- |
| Core Engine | animation, audio, debug/export, game-gold-map actions, picture control, screen shake, switch/variable changes, system actions, text popups |

## Battle

| Plugin | Command Areas |
| --- | --- |
| Active Turn Battle | actor ATB commands, enemy ATB commands, system ATB commands |
| Aggro Control System | actor aggro commands, enemy aggro commands |
| Elements Status Menu Core | actor commands, enemy commands, script-call helpers |
| Items and Equips Core | actor item/equip commands, purify commands, shop commands |
| Skills and States Core | skill cost commands, state turn commands |
| TP System | actor TP commands, enemy TP commands, system TP commands |
| Battle Core Action Sequences | ACSET, ANIM, MECH, MOVE, MOTION, TARGET, camera, impact, inject, projectile and related Common Event command groups; route to the Action Sequence skill |

## Gameplay And Movement

| Plugin | Command Areas |
| --- | --- |
| DragonBones Union | DragonBones runtime commands and setup helpers |
| Events and Movement Core | auto movement, call event, dash, event icon, event label, event location, event popup, event timer |

## Narrative And Presentation

| Plugin | Command Areas |
| --- | --- |
| Message Core | message commands, choice commands, picture commands, select commands |
| Visual Novel Picture Busts | basic bust commands, movement, fade, scale, tone/tint, animations |

## Quality Of Life

| Plugin | Command Areas |
| --- | --- |
| Items and Equips Core | actor, purify, and shop commands when the task is menu/shop QoL |
| Save Core | autosave commands, save commands |

## Skill Progression

| Plugin | Command Areas |
| --- | --- |
| Equip Passive System | actor, global, and system passive commands |
| Skill Learn System | AP commands, SP commands, system commands |
| Skill Shop | skill shop plugin commands |

## Routing Notes

- If the user names a command but not a plugin, first identify the active
  VisuStella plugin list and route by command area.
- If the command is part of a battle animation or Common Event linked from a
  skill/item Action Sequence, use `rpg-maker-mz-visustella-action-sequences`.
- If command availability is unclear, confirm plugin activation and load order
  before editing event data.
