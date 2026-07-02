# VisuStella Progression And Economy Checklist

Use this checklist before designing, reviewing, or debugging VisuStella MZ
progression and economy behavior.

## Preflight

- Confirm RPG Maker MZ project evidence and active VisuStella plugin list.
- Confirm plugin ownership: Skill Learn System, Skill Shop, Equip Passive
  System, More Currencies, Database Inherit, Items and Equips Core, Skills and
  States Core, or another route.
- Confirm the target surface: parameter, notetag, plugin command, database
  object, shop entry, event command list, or runtime behavior.
- Confirm whether the task is generic domain guidance or a consumer-specific
  balance/content decision. Consumer-specific tuning belongs in the consumer
  project, not the package.

## Cost And Requirement Checks

- Separate cost, requirement, visibility, and confirmation behavior.
- Confirm whether a condition is checked for display, enablement, purchase,
  learning, equip, or runtime use.
- For JavaScript formula/tag behavior, confirm available variables and object
  context before proposing code.
- Check item/weapon/armor/currency costs, variable costs, gold costs, AP/SP
  costs, and composite costs separately.

## Currency And Shop Checks

- For More Currencies, identify whether the task uses item, weapon, armor,
  variable, or gold currency.
- Confirm proxy records when the same purchase can appear with different
  currencies or prices.
- For Skill Shop or Items and Equips shop behavior, confirm how the shop is
  opened, which skills/items are listed, and whether visibility differs from
  purchase enablement.
- Use plugin commands for runtime shop flows and data-json for event payloads.

## AP, SP, Skill Learning, And Passives

- Confirm AP/SP gain source, actor/class scope, victory rewards, menu display,
  draw/display formulas, and plugin commands.
- Confirm learnable skills are defined on the intended actor/class/skill
  surface.
- For Equip Passive System, confirm passive state ID, capacity, equip slot,
  learned/unlearned state, hidden/masked behavior, and unlock conditions.
- When passives affect battle, route to
  `rpg-maker-mz-visustella-battle-mechanics` for combat implications.

## Database Inherit And Item/Equipment Checks

- Confirm inheritance source and target IDs; inheritance behavior can depend on
  database order.
- Distinguish inherited note fields, traits, effects, parameters, damage
  formulas, and enemy actions.
- For Items and Equips Core, confirm item/equip category, accessibility,
  equipment slots, type handling, shop status display, item/equip prices, and
  menu window parameters.

## Write Gate Mapping

| Target | Required Gate |
| --- | --- |
| `data/*.json`, database objects, notes, shops, event command lists, Common Events | `rpg-maker-mz-data-json` |
| Plugin Manager settings, plugin parameters, activation, load order, `js/plugins.js` | `rpg-maker-mz-plugin-workflow` |
| active plugin list, database IDs, event callers, shop ownership | `rpg-maker-mz-project-inventory` |
| AP/SP awards, shops, learning, passive unlocks, inherited behavior, save/load-sensitive state | Playtest or another approved human validation gate |

## Stop Conditions

- The task would require consumer-specific pricing or progression policy not
  provided by the user or durable project docs.
- The write target is unknown or lacks task authorization.
- Plugin order, active plugin list, inheritance source/target, or database ID
  ownership is unclear and affects behavior.
- Runtime or save/load behavior must be proven but no Playtest or human
  validation gate exists.
