---
doc_id: "lf-agent-execution-evidence-codex-adapter"
version: "2.0.0"
status: active
last_updated: "2026-07-23"
scope: "Current closed Codex evidence, exact-token, estimate, and liveness behavior"
not_scope: "Automatic App Server startup, private reasoning, or unverified provider capability"
authority: "lf-agent-execution-evidence current contracts and observed run-scoped exports"
canonical_source: "skills/lf-agent-execution-evidence/references/codex-adapter.md"
intended_llm_task: "context-hydration"
source_priority: ["approved run envelope", "neutral evidence contracts", "observed run-scoped export", "provider proposal"]
confidence: high
known_conflicts: []
replaced_by: null
---

# Codex adapter

The adapter accepts only an explicit structured export supplied to the collector.
App Server is experimental and opt-in; this package does not start it or depend
on it. Tested package behavior is therefore `partial`: thread/session locators
may be recorded, while transcript, tool I/O and usage remain unavailable unless
a run-scoped export proves them. Exact usage requires the export's verified
run-scoped counter; sanitized observable bytes may produce only the separate
low-confidence `utf8-byte-estimate-v1`. `reasoning_output_tokens` is a usage
counter, never private reasoning or chain-of-thought.

Forward-test states: successful terminal completion, terminal error and closed
session all produce a manifest; a closed session is `unavailable`, not empty or
complete.

Before a silence-based stop, query the adapter's observed thread/run status.
An observed running/progress state forbids the stop. If App Server or another
status source is not enabled, record `unsupported` or `unavailable` with a
reason; do not synthesize a heartbeat.
