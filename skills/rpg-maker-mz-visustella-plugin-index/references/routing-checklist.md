# VisuStella Routing Checklist

Use this checklist after the router skill loads. The goal is to choose the
smallest useful next context and preserve Loki write gates.

## Decision Order

1. Is the project confirmed as RPG Maker MZ?
   - If not, first use local project evidence or
     `rpg-maker-mz-project-inventory`.
2. Is VisuStella mentioned, detected in plugin names, or likely relevant to the
   requested behavior?
   - If not, use vanilla RPG Maker MZ skills and project evidence.
3. Is there an exact plugin name or family?
   - Read `plugin-map.md` and route by family.
4. Is the target surface known?
   - Parameters -> `rpg-maker-mz-visustella-plugin-parameters`.
   - Notetags/comment tags -> `rpg-maker-mz-visustella-notetags`.
   - Plugin commands -> `rpg-maker-mz-visustella-plugin-commands`.
   - Action Sequences -> `rpg-maker-mz-visustella-action-sequences`.
   - Battle mechanics -> `rpg-maker-mz-visustella-battle-mechanics`.
   - Progression/economy -> `rpg-maker-mz-visustella-progression-economy`.
   - Events/presentation -> `rpg-maker-mz-visustella-events-presentation`.
   - Compatibility/symptom diagnosis ->
     `rpg-maker-mz-visustella-compat-diagnostics`.
5. If both plugin and surface are known, prefer the surface skill and use the
   plugin map only to narrow which reference should be read inside that skill.
6. If only a symptom is known, classify the symptom:
   - no-effect tag -> notetags plus diagnostics;
   - plugin command does nothing -> plugin commands plus diagnostics;
   - parameter changed but behavior unchanged -> parameters plus diagnostics;
   - Action Sequence plays but no damage/heal -> action sequences plus data
     gate and Playtest;
   - visual/camera/picture/save issue -> events/presentation or diagnostics.
7. Choose at most two next skills unless the task explicitly requires a full
   technical analysis.

## Write Gate Mapping

| Target Change | Required Gate |
| --- | --- |
| `data/*.json`, note fields, database objects, maps, Common Events, event command lists, troop events | `rpg-maker-mz-data-json` |
| plugin files, helper plugins, PluginManager metadata, plugin parameters, `js/plugins.js`, plugin activation or load order | `rpg-maker-mz-plugin-workflow` |
| installed plugin discovery, active plugin order, project structure, local ownership, event callers | `rpg-maker-mz-project-inventory` |
| visuals, input, timing, audio, save/load, gameplay behavior, Action Sequence playback | Playtest or another approved human validation gate |

## Good Router Outputs

- "Use `rpg-maker-mz-visustella-notetags` for tag syntax and
  `rpg-maker-mz-data-json` before editing the target database object."
- "Use `rpg-maker-mz-visustella-plugin-parameters` for the setting semantics
  and `rpg-maker-mz-plugin-workflow` before changing `js/plugins.js`."
- "This is an Action Sequence task. Use
  `rpg-maker-mz-visustella-action-sequences`; damage/heal behavior still needs
  a Playtest gate."
- "The package does not yet include the specialized future route; use this
  router to identify the intended route and preserve the existing data/plugin
  gate."

## Stop Or Ask For More Evidence

Stop instead of guessing when:

- the request names a behavior but no project evidence shows VisuStella is
  installed;
- several plugins could own the behavior and no family/surface is known;
- a proposed write target is unknown;
- the task needs runtime proof but no human validation gate exists;
- the only available evidence is obfuscated plugin source and no docs or
  project inventory have been checked.
