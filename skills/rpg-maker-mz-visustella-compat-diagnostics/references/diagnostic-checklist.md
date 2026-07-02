# VisuStella Diagnostic Checklist

Use this checklist for VisuStella MZ symptoms, compatibility questions, and
cases where vanilla RPG Maker MZ source does not explain observed behavior.

## Minimum Flow

1. Confirm RPG Maker MZ project evidence.
2. Confirm VisuStella plugin evidence:
   - active plugin list;
   - exact plugin names;
   - `js/plugins.js` order;
   - parameters when relevant;
   - local docs or project notes when available.
3. Classify the symptom:
   - plugin inactive, missing, disabled, or misordered;
   - dependency/tier issue;
   - parameter mismatch;
   - notetag/comment tag on wrong target or wrong syntax;
   - plugin command payload or caller issue;
   - Action Sequence missing link, effect, target loop, extension, or cleanup;
   - battle mechanics issue;
   - progression/economy issue;
   - event/presentation issue;
   - performance/visual/save/options/debug issue;
   - runtime validation gap.
4. Route to the smallest specialized skill and preserve the data/plugin gate.
5. Separate static evidence from runtime-pending validation.

## Required Checks By Symptom

### Plugin Active, Tier, Order, Dependency

- Verify exact active plugin name and enabled flag.
- Check whether Core Engine or Battle Core is required.
- Confirm tier/order relationship before lower-tier dependencies and
  higher-tier extensions.
- If activation or load order must change, use `rpg-maker-mz-plugin-workflow`.

### Parameter Mismatch

- Confirm whether the setting lives in Plugin Manager parameters or an override
  notetag/command.
- Read `rpg-maker-mz-visustella-plugin-parameters`.
- Confirm actual consumer `js/plugins.js` values before claiming active
  behavior.
- Use `rpg-maker-mz-plugin-workflow` before changing `js/plugins.js`.

### Notetag Or Comment Tag Has No Effect

- Confirm the tag belongs to the active plugin.
- Confirm the target object supports the tag: actor, class, skill, item,
  weapon, armor, enemy, state, troop, map, event, page, Common Event, or note
  field.
- Confirm the object ID/name, note field/comment surface, inheritance or
  override behavior, and runtime condition.
- Use `rpg-maker-mz-visustella-notetags` and `rpg-maker-mz-data-json`.

### Plugin Command Does Nothing

- Confirm owning plugin and command availability.
- Confirm event surface: map event, troop event, Common Event, Action Sequence
  Common Event, or runtime caller.
- Confirm payload parameters, IDs, switch/variable dependencies, and caller
  chain.
- Use `rpg-maker-mz-visustella-plugin-commands` and `rpg-maker-mz-data-json`.

### Action Sequence Missing Effect Or Cleanup

- Confirm skill/item note linkage and Common Event linkage.
- Confirm setup and finish flow.
- If the sequence should apply the current action's damage/heal/effects,
  confirm `MECH: Action Effect` or explicit equivalent.
- Confirm target loop exit, extension plugin activation, camera/impact/inject
  reset, battler home reset, immortal flag cleanup, battle log flow, and
  Playtest gate.
- Use `rpg-maker-mz-visustella-action-sequences`.

### Visual, Event, Options, Save, Debug, Or Performance Symptom

- Route event/message/picture/bust/DragonBones/options/save/debug symptoms to
  `rpg-maker-mz-visustella-events-presentation`.
- Route state visual effects, camera, impact, inject, and battle UI symptoms to
  battle mechanics or action sequences first, then this diagnostic checklist.
- Confirm whether the issue can be statically inspected or requires runtime
  reproduction.

## Evidence Labels

- `static-evidence`: file/plugin/object evidence was inspected.
- `routing-hypothesis`: plugin family or symptom route is plausible but not
  proven.
- `structural-validation`: parse/diff/checklist validation passed.
- `runtime-pending`: behavior needs Playtest or another human validation gate.
- `runtime-validated`: only use after explicit human validation evidence.

## Stop Conditions

- No active VisuStella evidence exists and the symptom could be vanilla or
  project-specific.
- Several plugins could own the symptom and no plugin/surface evidence has been
  read.
- A proposed fix requires writes without task authorization and the required
  data/plugin gate.
- The requested answer would claim runtime behavior fixed without Playtest or
  equivalent human validation.
