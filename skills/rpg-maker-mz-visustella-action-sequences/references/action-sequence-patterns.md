# VisuStella Action Sequence Patterns

Use this reference before generating, translating, or reviewing an Action
Sequence.

## Minimal Damaging Sequence

```text
Skill/Item note:
<Custom Action Sequence>

Common Event:
ACSET: Setup Action Set
ANIM: Action Animation
MECH: Action Effect
ACSET: Finish Action
```

Checks:

- `ACSET: Setup Action Set` prepares display, immortal, and optional battle
  step/cast behavior.
- `ANIM: Action Animation` shows the skill/item animation.
- `MECH: Action Effect` applies the current action's damage, healing, buffs,
  debuffs, states, and configured effects.
- `ACSET: Finish Action` resets home position, immortal flags, battle log, and
  waits as needed.

## Multi-Hit Pattern

```text
ACSET: Setup Action Set
ANIM: Action Animation
MECH: Action Effect
MOTION: Wait By Motion Frame
ANIM: Action Animation
MECH: Action Effect
ACSET: Finish Action
```

Use one Action Effect per intended hit unless using a command group that
explicitly applies multiple hits.

## Each-Target Loop Pattern

```text
ACSET: Setup Action Set
LABEL: LoopStart
TARGET: Next Target or TARGET: Random Target
MOVE/ANIM commands for the selected target
MECH: Action Effect
conditional branch or label jump to LoopStart while targets remain
ACSET: Finish Action
```

Checks:

- target scope on the skill/item supports all or random targets;
- target index command jumps to a valid label;
- loop has a clear exit;
- finish/reset still runs after the loop.

## Projectile Pattern

Use projectile commands when the visible hit travels from user to target.

Checks:

- start and goal locations are valid battlers or points;
- animation ID exists;
- wait flags match desired timing;
- projectile effect emulation applies Action Effect, item effect, skill effect,
  or Common Event effect when the projectile is meant to do more than visuals.

## Camera, Impact, And Inject Pattern

Use camera/impact/inject commands for presentation only after confirming the
required extension plugin is active.

Checks:

- camera focus/reset or zoom/reset pairs are balanced;
- impact effects do not replace Action Effect;
- injected animations have waits if later commands depend on them;
- finish/reset returns camera or battler state when needed.

## Cleanup Checklist

- Immortal flags are turned off.
- User and targets return home when expected.
- Opacity, angle, skew, zoom, overlays, portraits, and camera are reset when the
  sequence changed them.
- Battle log is cleared or advanced intentionally.
- Target loops exit.
- Runtime validation is marked pending until Playtest.

## Common Failure Modes

- Skill animates but deals no damage because `MECH: Action Effect` or an
  equivalent is missing.
- Common Event exists but is not linked from the skill/item effect or key.
- `<Custom Action Sequence>` disables automatic behavior, but the Common Event
  does not recreate required setup/action/finish behavior.
- Extension command is used while the required extension plugin is inactive.
- Multi-target flow uses a single-target scope, or a target loop never exits.
