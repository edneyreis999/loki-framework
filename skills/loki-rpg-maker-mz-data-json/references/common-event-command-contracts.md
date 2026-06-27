# Common Event Command Contracts

Use this reference when a task reads, generates, rewrites, or audits RPG Maker MZ event command `code` and `parameters` values.

## Rule

Do not rely on memory, old task text, or an implementation audit that repeats the same assumptions as the patch. Confirm command semantics in the target engine source, usually `Game_Interpreter.prototype.commandNNN` in `rmmz_objects.js`, before treating a numeric code as correct.

## Minimum Workflow

1. Locate the command in the target engine source.
2. Record the command name, expected `parameters` shape, and side effect.
3. Compare the generated JSON against that independent source.
4. If the command affects runtime behavior, require a runtime or Playtest gate.
5. If an audit checks only that the JSON contains the same code the task wrote, reject the audit as tautological.

## Recurring Lookup Targets

These commands are common in RPG Maker MZ event work. Treat this as a lookup checklist, not a complete table.

| Code | Engine method | Typical purpose | Gate |
| --- | --- | --- | --- |
| 111 | `command111` | Conditional Branch | Verify branch parameter shape before generation. |
| 117 | `command117` | Call Common Event | Verify child-interpreter behavior before calling looping or parallel logic. |
| 121 | `command121` | Control Switches | Verify ON/OFF parameter semantics in the target engine. |
| 122 | `command122` | Control Variables | Verify operation and operand encoding. |
| 223 | `command223` | Tint Screen | Validate visible runtime effect. |
| 225 | `command225` | Shake Screen | Validate visible runtime effect. |
| 231 | `command231` | Show Picture | Validate picture name, origin, position, opacity and asset existence. |
| 232 | `command232` | Move Picture | Validate picture id and timing. |
| 235 | `command235` | Erase Picture | Validate cleanup does not erase active UI unexpectedly. |
| 241 | `command241` | Play BGM | Validate audio asset and runtime route. |
| 242 | `command242` | Fadeout BGM | Validate duration and handoff. |
| 246 | `command246` | Fadeout BGS | Do not confuse with ME playback. |
| 249 | `command249` | Play ME | Do not confuse with BGS fadeout. |
| 357 | `command357` | Plugin Command | Schema is plugin-specific; prefer editor-confirmed or engine-confirmed generation. |
| 657 | continuation entry | Plugin-command continuation in MZ data | Preserve structure unless the plugin schema is known. |

## Common Failure Mode

Audio and plugin command codes can look plausible while being semantically inverted. A JSON parse pass only proves syntax. It does not prove the event command means what the task claims.
