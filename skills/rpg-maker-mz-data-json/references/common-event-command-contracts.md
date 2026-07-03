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
6. When a command references an asset by name, verify the physical asset path for the target channel before claiming semantic validation.

## Branch And Indent Validation

RPG Maker MZ event commands use `indent` as runtime structure, not formatting.
`Game_Interpreter` sets the current `_indent` from each command, stores branch
state by that indent, and `skipBranch()` skips only following commands with a
greater indent than the branch command. Therefore, a command list can contain the
right branch `code` values while still running the guarded commands outside the
branch if their `indent` values are wrong.

When a list includes branching or scoped outcomes, report
`branch_indent_checked` separately from command-code validation. At minimum:

- For `Conditional Branch` (`111`), children controlled by the condition must
  be at a greater indent than the `111` command. `Else` (`411`) and the branch
  terminator (`412`) stay at the branch indent, while their children are nested
  below them.
- For choices, validate `When` (`402`), `When Cancel` (`403`) and choice end
  (`404`) structure, not just the presence of the choice command.
- For battle outcomes such as `If Win` (`601`), validate outcome block
  indentation before claiming the win/escape/lose flow is gated.
- Reject semantic audits that only locate `111`, `411`, `402`, `404` or `601`
  without checking the surrounding command order and indent ladder.

Visible behavior remains `runtime_pending` until a runtime or Playtest gate
confirms the intended flow.

## Audio Asset Validation

Audio play commands reference a logical audio object name; JSON parse and command
semantics do not prove the file exists. For generated or audited audio event
commands, report `audio_event_asset_exists_checked` separately from
`playback_validated`.

Check the command channel and asset folder together:

- `Play BGM` (`241`) uses `audio/bgm`.
- `Play BGS` (`245`) uses `audio/bgs`.
- `Play ME` (`249`) uses `audio/me`.
- `Play SE` (`250`) uses `audio/se`.

Confirm the named asset exists with an engine-supported extension in the target
folder, respecting case sensitivity for deployed platforms. Do not substitute a
plausible filename from memory. Playback, volume, pitch, pan, timing and mix
quality still require runtime or Playtest validation.

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
| 245 | `command245` | Play BGS | Validate audio asset and runtime route. |
| 246 | `command246` | Fadeout BGS | Do not confuse with ME playback. |
| 249 | `command249` | Play ME | Do not confuse with BGS fadeout. |
| 250 | `command250` | Play SE | Validate audio asset and runtime route. |
| 357 | `command357` | Plugin Command | Schema is plugin-specific; prefer editor-confirmed or engine-confirmed generation. |
| 657 | continuation entry | Plugin-command continuation in MZ data | Preserve structure unless the plugin schema is known. |

## Common Failure Mode

Audio and plugin command codes can look plausible while being semantically inverted. A JSON parse pass only proves syntax. It does not prove the event command means what the task claims.

Branch command codes can also look correct while their child commands are
outside the branch because `indent` was left at the parent level. Treat branch
structure, asset existence and runtime validation as distinct checks.
