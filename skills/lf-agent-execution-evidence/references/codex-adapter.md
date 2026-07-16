# Codex adapter

The adapter accepts only an explicit structured export supplied to the collector.
App Server is experimental and opt-in; this package does not start it or depend
on it. Tested package behavior is therefore `partial`: thread/session locators
may be recorded, while transcript, tool I/O and usage remain unavailable unless
a run-scoped export proves them. `reasoning_output_tokens` is a usage counter,
never private reasoning or chain-of-thought.

Forward-test states: successful terminal completion, terminal error and closed
session all produce a manifest; a closed session is `unavailable`, not empty or
complete.
