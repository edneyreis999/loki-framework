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

## Control Switches Range Validation

`Control Switches` (`121`) stores parameters as
`[startId,endId,operation]`. In RPG Maker MZ, `command121` applies the
operation to every switch from `startId` through `endId`, inclusive.

Treat `startId !== endId` as an intentional range operation. For a single
switch, require `[id,id,operation]`. For several distinct narrative, quest, or
progression flags, prefer separate unit commands and assert each command shape
unless the task explicitly declares a contiguous range.

A validator for `code:121` must compare the expected command shape, not only the
final set of switch IDs that could be affected. Classify the expected shape as
`unit-switch`, `multiple-unit-switches`, or `explicit-range`; reject ranges when
the requirement names individual flags or a singular state.

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

## Choice Path Enumeration

For maps or Common Events with nested choices, do not infer complete routes from
apparent leaves, repeated labels or visible indentation alone. Enumerate paths
through the event command structure:

- `Show Choices` (`102`) opens the choice group.
- `When` (`402`) and `When Cancel` (`403`) define branch entries at the choice
  indent.
- `Choice End` (`404`) closes the group.

For route counts, record the parser rule used, the first and final transfer or
state mutation for each path, and any branch that reaches termination without
the expected command. Treat text duplication as a content signal only; it is not
proof that a block can be extracted or merged safely.

## Terminal Transfer And Exit Validation

`Transfer Player` (`201`) changes map/location, but a transfer command in the
event list is not by itself proof that the interpreter branch has no further
observable work. When a branch is intended to be terminal, correlate the
transfer with `Exit Event Processing` (`115`) or an equivalent terminal flow
confirmed in the target engine/source.

Report terminal-transfer validation separately from JSON parse and route count:

- `terminal_transfer_checked`: transfer commands were found and classified.
- `explicit_exit_checked`: expected exits or equivalent termination were
  confirmed.
- `runtime_pending`: Playtest or runtime evidence is still required for
  perceptible behavior after transfer.

Avoid wording that implies every transfer must always be followed immediately by
`115`; the reusable rule is to prove termination for branches that are claimed
to be terminal.

## Large Command-List Rewrite Split

For broad map or Common Event rewrites, split responsibilities before mutation:

1. Read-only extraction identifies current ranges from the latest file state.
2. A single serialized writer applies scoped changes to approved `target_files`.
3. Independent QA reproduces or audits route counts, branch structure, command
   targets and restricted diff.

Never apply stale range indices from an earlier snapshot without recomputing or
shifting them against the current file. A successful static equivalence check
proves structure only; message timing, child-interpreter feel, visual state,
audio, input and route perception remain runtime or Playtest gates.

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
| 102 | `command102` | Show Choices | Enumerate choice paths with matching `402`/`403`/`404`. |
| 111 | `command111` | Conditional Branch | Verify branch parameter shape before generation. |
| 115 | `command115` | Exit Event Processing | Use as explicit branch termination when required by the flow. |
| 117 | `command117` | Call Common Event | Verify child-interpreter behavior before calling looping or parallel logic. |
| 121 | `command121` | Control Switches | Verify inclusive range and ON/OFF parameter semantics in the target engine. |
| 122 | `command122` | Control Variables | Verify operation and operand encoding. |
| 201 | `command201` | Transfer Player | Verify destination and terminal-flow expectations separately. |
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
| 402 | branch entry | Choice branch | Validate pairing with `102` and `404`, plus indent. |
| 403 | cancel branch | Choice cancel | Validate cancel behavior and indent when present. |
| 404 | choice end | End of choices | Validate it closes the intended choice group. |
| 657 | continuation entry | Plugin-command continuation in MZ data | Preserve structure unless the plugin schema is known. |

## Common Failure Mode

Audio and plugin command codes can look plausible while being semantically inverted. A JSON parse pass only proves syntax. It does not prove the event command means what the task claims.

Branch command codes can also look correct while their child commands are
outside the branch because `indent` was left at the parent level. Treat branch
structure, asset existence and runtime validation as distinct checks.
