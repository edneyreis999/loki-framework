# VisuStella Action Sequence Command Index

Use this reference to choose Battle Core Action Sequence command groups. These
commands are inserted as plugin commands inside Common Events, but Action
Sequence work needs this dedicated skill because setup, target flow, damage
application, and cleanup must be coherent.

## Required Flow

1. Skill or item has Action Sequence note setup, commonly
   `<Custom Action Sequence>`.
2. A Common Event contains Battle Core Action Sequence plugin commands.
3. The skill/item calls the Common Event through its effects or Action Sequence
   key setup.
4. The Common Event includes setup, visual/motion work, action effect where
   needed, and finish/cleanup.

## Command Groups

| Group | Use For | Notes |
| --- | --- | --- |
| `ACSET` | setup and finish action sets, all-target or each-target action sets | common start/end wrapper; usually includes display, immortal, home reset, log cleanup |
| `ANIM` | action animation, attack animation, specific animation, balloons, cast animation, portraits | use waits when timing matters |
| `BTLOG` | battle log lines and waits | pair with cleanup if sequence changes log flow |
| `CAMERA` | focus, offset, clamp, reset, wait for camera | camera extension must be active when command requires it |
| `ANGLE` | camera angle changes and reset | requires Action Sequence Camera Core |
| `SKEW` | camera skew changes and reset | requires Action Sequence Camera Core |
| `ZOOM` | camera or scene scale changes and reset | requires Action Sequence Camera Core where applicable |
| `CUTIN` | visual cut-in effects | check extension availability |
| `DB` | DragonBones actions | requires DragonBones-related setup and assets |
| `ELE` | element-related sequence behavior | verify battle plugin support and target context |
| `GRID` | battle grid actions | verify grid plugin availability |
| `HORROR` | horror visual effects | visual runtime validation required |
| `IMPACT` | shockwaves, trails, flash, time stop, impact effects | impact extension must be active for extension commands |
| `INJECT` | injected animations and waits | Action Sequence Impact style workflows often use this |
| `MECH` | damage/heal application, buffs/debuffs, states, HP/MP/TP, action emulation, immortal, labels, battle-system resources | `MECH: Action Effect` applies the current action's damage/heal/effects |
| `MOTION` | battler poses and motion-frame waits | sideview and battler support can matter |
| `MOVE` | move to target, home reset, jumps, floats, offsets, waits | sideview movement and target positions must be validated |
| `PROJECTILE` | projectile animation and effect emulation | can emulate Action Effect or item/skill/common-event effects at impact |
| `TARGET` | current/next/previous/random target index and label jumps | use for manual target loops |
| `VOICE` | battle voices | audio validation remains a Playtest/human gate |
| `WEAPON` | weapon display/control | verify actor/equipment context |
| `JS` | JavaScript hooks | high risk; validate context and avoid guessing APIs |

## Action Effect Rule

When a sequence is expected to apply the current skill/item effect, review for
one of these:

- `MECH: Action Effect`;
- an explicit emulated skill/item effect;
- projectile effect emulation configured to apply Action Effect;
- a deliberate statement that this sequence is visual-only and should not apply
  damage, healing, buffs, debuffs, states, or item/skill effects.

Animation, movement, camera, and sound alone do not apply the current action's
damage or effects.
