# VisuStella Progression And Economy Plugin Map

Use this reference to route VisuStella MZ progression and economy work by
plugin, dependency, and surface. This map is a compact routing aid, not a full
manual.

## Domain Rule

Progression/economy behavior often crosses plugin parameters, notetags,
database objects, plugin commands, shops, events, and save/load state. Keep
semantic routing separate from write gates: use this skill for domain
reasoning, `rpg-maker-mz-data-json` for data writes, and
`rpg-maker-mz-plugin-workflow` for plugin configuration writes.

## Plugin Families

| Plugin Or Family | Main Surfaces | Route To |
| --- | --- | --- |
| Skill Learn System | AP, SP, learnable skills, show conditions, require conditions, learn costs, learn animations/sounds, menu visibility, AP/SP plugin commands | notetags, plugin commands, parameters, data-json |
| Skill Shop | skill shop entries, gold costs, class/level/skill/switch requirements, shop opening commands, vocabulary/window settings | notetags, plugin commands, parameters, data-json |
| Equip Passive System | state-based passives, equip/unequip capacity, hidden/masked passives, unlock conditions, Skill Learn integration, actor/global/system commands | notetags, plugin commands, parameters, data-json |
| More Currencies | item/weapon/armor/variable/gold currencies, proxy items, buy/sell costs, currency listing, shop pricing | notetags, parameters, data-json |
| Database Inherit | inherited properties, traits, effects, damage formulas, enemy actions, note inheritance, inheritance order | notetags, parameters, data-json, diagnostics |
| Items and Equips Core | item/equipment categories, accessibility, equip slots, copy/type limits, artifacts, cursed equipment, shop status windows, advanced shop behavior | notetags, plugin commands, parameters, data-json |
| Elements Status Menu Core | trait sets, element rulings, status menu categories, actor/enemy status commands | battle-mechanics, notetags, plugin commands, parameters |
| Skills and States Core | skill costs, skill accessibility, passive states, gauge replacements, state rules | battle-mechanics, notetags, plugin commands, parameters |

## Surface Routing

| User Signal | Primary Route | Required Gate When Writing |
| --- | --- | --- |
| AP, SP, learnable skills, learn costs, learn requirements, show/hide learn menu | `rpg-maker-mz-visustella-notetags` or `rpg-maker-mz-visustella-plugin-commands` | `rpg-maker-mz-data-json` |
| skill shop entries, shop visibility, gold/default costs, shop windows | notetags, plugin commands, parameters | data-json or plugin-workflow depending on target |
| equip passive setup, hidden/masked passives, unlock conditions | notetags | data-json |
| More Currencies costs or proxy currency setup | notetags and parameters | data-json or plugin-workflow |
| Database Inherit behavior, inherited traits/effects/formulas/actions | notetags and diagnostics | data-json; Playtest for behavior |
| item/equip menu layout, categories, status windows, shop display | parameters | plugin-workflow for `js/plugins.js` |
| event command to grant AP/SP, open shop, change passive state | plugin commands | data-json for event JSON |

## Dependency And Order Notes

- Skill progression plugins commonly depend on lower-tier core or battle
  support plugins. Confirm active plugin order when a command, parameter, or
  notetag appears unavailable.
- Database Inherit can affect many database records at load time. Confirm
  inheritance source, target, ID order, and override behavior before proposing
  data changes.
- More Currencies may use proxy records to represent different prices for a
  similar purchase. Confirm proxy ownership before editing item/shop data.
- Equip Passive System uses states as the mechanical base for passives; use
  battle-mechanics when the passive affects battle behavior.

## Boundary

This reference routes progression/economy work only. It does not define
consumer-specific prices, rewards, balance curves, or shop content.
