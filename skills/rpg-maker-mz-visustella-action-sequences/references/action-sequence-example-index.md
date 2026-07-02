# VisuStella Action Sequence Example Index

This index summarizes the validated internal XML example set used to guide
pattern matching. It is self-contained and intentionally omits package-authoring
source paths.

## Audit Summary

- XML examples indexed: 42.
- Literal `Action Effect` matches across XML files: 46.
- Examples without a literal `Action Effect` match: 7.
- Treat examples without literal Action Effect as pattern references only; if a
  new sequence must apply damage, healing, buffs, debuffs, states, or item/skill
  effects, add `MECH: Action Effect` or justify an explicit equivalent.

## Example Groups

| Example IDs | Pattern Family | Use When |
| --- | --- | --- |
| 81-88 | jump, flip, dash-through, repeated dash attacks | melee movement, sideview approach, repeated hits |
| 89-92 | teleport and animation sneak attacks | disappear/reappear, no-animation hit variants, surprise attacks |
| 97-105 | tackle, flip bounce, penalty kick, dash flip | collision, bounce, knockback, approach/return patterns |
| 110-113 | float cast, dash cast, flip cast | caster movement, spell-style action with flash timing |
| 120-121 | flip shot and dive shot | ranged shot or dive movement with action effect timing |
| 130-133 | projectile and magic projectile variants | animation projectile travel and impact behavior |
| 140-148 | advanced slashes, input, nightmare, flare/increment/critical variants | conditional, random, input-driven, or advanced battle presentation |
| 52-53 | combo and wind-dance examples | multi-hit and multi-target loop inspiration |

## Full Example List

| ID | Example | Literal Action Effect Count |
| --- | --- | --- |
| 52 | combo-duplo | 2 |
| 53 | dana-dos-ventos | 4 |
| 81 | jump-attack | 1 |
| 82 | flip-attack | 1 |
| 83 | dash-through | 1 |
| 84 | dash-through-all | 1 |
| 85 | high-jump | 1 |
| 86 | jump-a-dash-a | 2 |
| 87 | flip-a-dash-a | 2 |
| 88 | dash-through-x-2 | 2 |
| 89 | teleport-attack | 1 |
| 90 | teleport-sneak-attack | 1 |
| 91 | teleport-attack-all | 1 |
| 92 | animation-sneak-attack | 1 |
| 97 | tackle | 1 |
| 98 | flip-bounce | 1 |
| 99 | flip-bounce-tackle | 2 |
| 100 | frontal-flip-bounce | 1 |
| 101 | penalty-kick | 1 |
| 102 | flip-sneak-attack | 1 |
| 103 | flip-bounce-all | 1 |
| 104 | dash-flip | 1 |
| 105 | dash-flip-all | 1 |
| 110 | float-cast | 2 |
| 111 | dash-cast | 2 |
| 112 | dash-cast-all | 2 |
| 113 | flip-cast | 1 |
| 120 | flip-shot | 1 |
| 121 | dive-shot | 1 |
| 130 | projectile | 1 |
| 131 | flip-projectile | 1 |
| 132 | mgc-flip-projectile | 0 |
| 133 | mgc-projectile | 1 |
| 140 | flip-attack-sequential | 1 |
| 141 | elemental-slash | 1 |
| 142 | crisis-attack | 0 |
| 143 | random-slash | 0 |
| 144 | input-attack | 0 |
| 145 | nightmare | 0 |
| 146 | flare-sword | 1 |
| 147 | increment-blade | 0 |
| 148 | critical-smash | 0 |

## Matching Rules

- Use example names to choose a motion pattern, not to copy blindly.
- Preserve the user's intended target scope: single, all, random, sequential, or
  repeated.
- If the target skill/item is damaging or healing, Action Effect review is
  mandatory even when the matched example has no literal Action Effect label.
- Any generated or modified sequence still requires `rpg-maker-mz-data-json`
  before data writes and Playtest before runtime validation.
