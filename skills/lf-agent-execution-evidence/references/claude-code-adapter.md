---
doc_id: "lf-agent-execution-evidence-claude-code-adapter"
version: "2.0.0"
status: active
last_updated: "2026-07-23"
scope: "Current closed Claude Code evidence, usage, and liveness behavior"
not_scope: "Unobserved hook capability, provider parity claims, private reasoning, or automatic capture"
authority: "lf-agent-execution-evidence current contracts and observed run-scoped exports"
canonical_source: "skills/lf-agent-execution-evidence/references/claude-code-adapter.md"
intended_llm_task: "context-hydration"
source_priority: ["approved run envelope", "neutral evidence contracts", "observed run-scoped export", "provider proposal"]
confidence: high
known_conflicts: []
replaced_by: null
---

# Claude Code adapter

Hooks, transcript files and usage are candidate sources only. Without an
observed, run-scoped export this adapter writes `unsupported` (no collector) or
`unavailable` (declared source inaccessible), with an explicit reason. It does
not claim parity with Codex and never revives automatic retrospective capture.

Use only an observed hook/runtime status as a liveness probe. Before a
silence-based stop, persist `running`, `progress`, `terminal`, `unsupported`, or
`unavailable` plus source/reason. Running/progress forbids the stop; absent
hooks do not imply silence or completion.
