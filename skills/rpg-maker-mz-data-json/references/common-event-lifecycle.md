# Common Event Lifecycle

Use this reference when editing Common Events that are parallel, called through `command117`, guarded by switches, or involved in input/result-screen handoffs.

## Parallel Common Events

A parallel Common Event depends on its trigger switch and on the engine refreshing its interpreter. If the trigger becomes inactive, the engine can clear the interpreter. Turning off a lifecycle switch is therefore not just "blocking input"; it can kill the event that still needs to finish a wait loop or handoff.

## Input Locks Vs Lifecycle Switches

Use a dedicated input lock for gameplay input when the owner event must remain alive. Do not turn off the lifecycle switch solely to prevent player actions during a result screen, transition, or resolution animation.

Recommended checks:

- Which switch owns this Common Event?
- Which event is currently waiting?
- Does this flow need to survive a `Wait 1 frame`?
- Are keyboard, mouse, hover, timer, and gameplay handlers all respecting the input lock?
- Is there a separate confirmation input for the result screen?

## `command117` Calls

`command117` runs a Common Event as a child interpreter. It is appropriate for finite subroutines. It is risky for logic that expects to own an independent parallel loop, because the caller can wait forever or create a nested lifecycle dependency.

Before adding or keeping a `command117` call:

1. Confirm the target CE terminates.
2. Confirm the caller can safely wait for it.
3. Remove synchronous callers when converting a CE into long-lived parallel logic.
4. Validate runtime with the same trigger switches used in the project.

## Result-Screen Handoff

For end-of-flow screens, keep the event that owns the confirmation loop alive until the branch after input has run. Gameplay inputs should be locked, not allowed to reserve safe/risk CEs behind the result screen.

## Debug Signals

Useful evidence for lifecycle bugs:

- owner switch state before and after wait;
- current Common Event id and interpreter index;
- child interpreter presence;
- event reservation queue;
- input lock state;
- whether new input logs appear without a matching wait-loop log.
