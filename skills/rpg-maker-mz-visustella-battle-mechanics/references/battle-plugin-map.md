# VisuStella Battle Plugin Map

Use this reference to route VisuStella MZ battle work by plugin, tier,
dependency, and surface. This map is a compact routing aid, not complete plugin
documentation.

## Battle Domain Rule

VisuStella battle plugins can change targeting, damage, criticals, battle
layout, skill/state rules, passive states, turn timing, TP modes, AI decisions,
aggro priority, battle gauges, state visuals, and Action Sequence playback. Do
not assume vanilla RPG Maker MZ source explains a battle symptom when these
plugins are active.

## Plugin Families

| Plugin Or Family | Tier / Dependency Signal | Main Surfaces | Route To |
| --- | --- | --- | --- |
| Battle Core | Tier 1; depends on Core Engine | Action Sequences, battle layout, damage styles, criticals, custom target scopes, battle commands, HP gauges, base troop events, battle log, sideview battlers | action-sequences, notetags, plugin commands, parameters, battle checklist |
| Action Sequence Camera Core | Battle extension; camera controls depend on active extension | angle, skew, zoom, focus, reset, player camera options | action-sequences, parameters, diagnostics |
| Action Sequence Impact | Battle extension; impact commands require active extension | impact, inject, visual hit effects, time stop style presentation | action-sequences, parameters, diagnostics |
| Skills and States Core | Tier 1 battle/support family | skill costs, accessibility, passive states, aura/miasma, slip damage/healing, state reapply, buffs/debuffs, gauges | notetags, plugin commands, parameters, battle checklist |
| Auto Skill Trigger | Battle extension | automatic skill triggers, trigger conditions, state/trait interactions | notetags, parameters, diagnostics |
| Life State Effects | Battle extension | enemy-only and state-only life/death effects, trait-object life effects | notetags, parameters, diagnostics |
| Visual State Effects | Higher-tier visual battle extension | state overlays, breathing, hover, tone, opacity, response popups, buff/debuff visuals | notetags, parameters, events/presentation, diagnostics |
| Active Turn Battle | Tier 2; requires Battle Core and TPB mode | ATB mechanics, interrupts, field gauge, skill/item speeds, gauge colors, actor/enemy/system commands | parameters, notetags, plugin commands, diagnostics |
| TP System | Tier 2 battle resource system | TP modes, TP formulas, actor/enemy/system TP commands, TP display | parameters, notetags, plugin commands, diagnostics |
| Battle AI | Higher-tier; usually Battle Core dependent | AI styles, AI levels, skill conditions, targeting, TGR weight | notetags, parameters, diagnostics |
| Aggro Control System | Tier 2; optional Core/Battle integration | provoke, taunt, aggro values, priority hierarchy, aggro gauges, actor/enemy commands | notetags, plugin commands, parameters, diagnostics |
| Elements Status Menu Core | Battle/status menu support | element rulings, trait sets, actor/enemy status commands, status menu categories | notetags, plugin commands, parameters |
| Items and Equips Core | Cross-domain battle/QoL surface | item/equipment access, shop status, equipment type handling, actor item/equip commands | progression-economy, notetags, plugin commands, parameters |

## Surface Routing

| User Signal | Primary Route | Secondary Gate |
| --- | --- | --- |
| "Action Sequence", `<Custom Action Sequence>`, camera, impact, inject, projectile, target loop, no damage after animation | `rpg-maker-mz-visustella-action-sequences` | `rpg-maker-mz-data-json` before Common Event/skill/item writes; Playtest |
| damage formula, damage cap, damage trait, critical, life steal, target scope | `rpg-maker-mz-visustella-notetags` or `rpg-maker-mz-visustella-plugin-parameters` | `rpg-maker-mz-data-json` for note writes |
| passive states, aura, miasma, slip damage, state turns, state reapply | `rpg-maker-mz-visustella-notetags` plus this checklist | `rpg-maker-mz-data-json`; Playtest |
| ATB speed, interrupt, field gauge, gauge color, TP mode, TP formula | `rpg-maker-mz-visustella-plugin-parameters` or `rpg-maker-mz-visustella-notetags` | `rpg-maker-mz-plugin-workflow` for `js/plugins.js`; Playtest |
| Battle AI conditions, AI style, targeting, TGR weight | `rpg-maker-mz-visustella-notetags` and parameters | Playtest for AI behavior |
| aggro, provoke, taunt, threat priority, actor/enemy aggro commands | `rpg-maker-mz-visustella-notetags` or `rpg-maker-mz-visustella-plugin-commands` | `rpg-maker-mz-data-json`; Playtest |
| battle UI, command windows, HP gauges, status windows, state visuals | `rpg-maker-mz-visustella-plugin-parameters` or events/presentation | `rpg-maker-mz-plugin-workflow`; Playtest |

## Dependency Notes

- Core Engine is the usual Tier 0 foundation.
- Battle Core is the usual Tier 1 foundation for battle mechanics and Action
  Sequence work.
- Higher-tier battle plugins usually belong below the lower-tier plugins they
  depend on.
- If plugin order, active/inactive extension, missing command availability, or
  unexplained runtime symptom is part of the question, route to
  `rpg-maker-mz-visustella-compat-diagnostics`.

## Boundary

This reference routes battle-domain work only. It does not authorize any
consumer write and does not replace project inventory, data-json, plugin
workflow, or Playtest gates.
