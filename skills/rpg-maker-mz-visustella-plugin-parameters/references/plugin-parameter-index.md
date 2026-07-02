# VisuStella Plugin Parameter Index

Use this index to narrow a parameter task by family and plugin. It is a routing
summary, not full plugin documentation.

## Core Engine

| Plugin | Parameter Areas |
| --- | --- |
| Core Engine | battle system defaults, color settings, gold settings, image loading, keyboard input, menu settings, parameter settings, QoL settings, quick functions, screen resolution, title screen, UI settings, window settings |

## Battle

| Plugin | Parameter Areas |
| --- | --- |
| Battle Core | Action Sequence defaults, actor/enemy battler settings, actor and party command windows, battle layout, battle log, battleback scaling, damage, damage combo window, HP gauge, in-battle status window, mechanics, multi-target windows |
| Action Sequence Camera Core | options-menu exposure for camera controls, camera angle/skew/zoom defaults, player-facing camera settings |
| Action Sequence Impact | general impact configuration and visual-impact defaults |
| Active Turn Battle | ATB gauge, field gauge, gauge colors, interrupt rules, ATB mechanics, options |
| Aggro Control System | aggro settings, provoke settings, taunt settings |
| Battle AI | general AI defaults, default conditions, TGR weight |
| Elements Status Menu Core | status menu categories, element rulings, trait set setup and trait-set types |
| Items and Equips Core | equip menu, item categories, item menu, new labels, shop menu, shop status window |
| Life State Effects | life/death state effect configuration |
| Skills and States Core | buff/debuff settings, gauge settings, passive state settings, skill cost types, skill settings, state settings |
| TP System | TP configuration, formulas, modes |
| Visual State Effects | buff/debuff visuals, general visual state settings, response popups, state visual config |

## Gameplay And Movement

| Plugin | Parameter Areas |
| --- | --- |
| DragonBones Union | battler settings, map sprite settings, general settings, experimental settings |
| More Currencies | general currency parameters and listing settings |
| Events and Movement Core | general event settings, labels/icons, movement, regions and terrain behavior |

## Narrative And Presentation

| Plugin | Parameter Areas |
| --- | --- |
| Message Core | auto color, custom font manager, general settings, text-code actions, replacements, language settings, macros, text speed option, word wrap |
| Visual Novel Picture Busts | picture bust defaults and general bust behavior |

## Quality Of Life

| Plugin | Parameter Areas |
| --- | --- |
| Database Inherit | inheritance plugin parameters and behavior defaults |
| Debugger | debugger plugin parameters and export/debug defaults |
| Items and Equips Core | item, equip, and shop menu parameters when used as QoL surface |
| Options Core | option categories, general options, master volume shortcut |
| Save Core | actor graphic settings, autosave settings, confirmation windows, general save settings, save style settings |

## Skill Progression

| Plugin | Parameter Areas |
| --- | --- |
| Equip Passive System | general settings, vocabulary settings, window settings |
| Skill Learn System | AP, SP, animation and sound, general config, windows |
| Skill Shop | general skill shop config, windows, vocabulary |

## Review Notes

- Parameter areas are defaults or plugin-wide behavior unless a notetag,
  comment tag, or plugin command overrides them.
- Parameter changes that appear harmless can affect save/load, input, battle
  timing, UI layout, or event flow. Keep runtime validation explicit.
- When a plugin appears in multiple families, route by the requested surface:
  parameter -> this skill; notetag -> notetags; event payload -> plugin
  commands; Action Sequence -> action sequences.
