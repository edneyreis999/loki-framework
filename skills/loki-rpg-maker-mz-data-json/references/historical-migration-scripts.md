# Historical Migration Scripts

Use this reference when a task reviews, adapts, or considers executing a script that mutates RPG Maker MZ `data/*.json` and was created for a previous plan, phase, migration, fix, or build step.

## Rule

Treat historical mutating scripts as evidence, not as reusable tools, until proven otherwise. A script can be idempotent for the snapshot where it was created and still be unsafe against the current runtime data.

Read-only audits are safer candidates for reuse. Mutators require a fresh preflight.

## Preflight Before Running A Mutator

1. Classify the script:
   - read-only audit;
   - validator;
   - mutator;
   - generator;
   - cleanup/debug helper.
2. Inspect version history for the script and its co-committed runtime files.
3. Identify whether later commits superseded the script's assumptions.
4. Parse the current target JSON and dump the affected IDs, commands, branches, parameters and indents.
5. Confirm command semantics against the target engine when numeric event codes are involved.
6. Confirm writer style and expected diff shape before saving.
7. Do not run the script if its preconditions describe an old snapshot that no longer matches the current files.

## Patch Strategy

Prefer a surgical structured patch when current data contains editor-created plugin commands, manual TextPicture commands, debug probes, telemetry, or hand edits that a generator could overwrite.

Idempotence must converge on the desired state. Checking only that a command exists is not enough; also verify attributes such as position, parameters, branch indent, target IDs, plugin command arguments and cleanup scope.

## Validation Labels

Report validation with explicit scope:

- `structural_validation`: parse, asserts, semantic dumps or diff checks passed.
- `runtime_pending`: runtime behavior is affected but Playtest has not confirmed it.
- `playtest_validated`: a human Playtest or equivalent runtime gate confirmed the affected route.

Never use structural validation alone to claim runtime behavior for input, audio, pictures, transfers, Common Events, child interpreters, waits, result screens or parallel lifecycle.

## Cleanup And Debug Probes

Temporary probes need an inventory before they are added:

- unique textual marker, if any;
- Common Events or maps touched;
- diagnostic audio or visual signals;
- expected cleanup command;
- post-cleanup audit.

Do not assume that removing a log marker removes every diagnostic effect. Audio probes and picture probes may not contain the same textual marker.
