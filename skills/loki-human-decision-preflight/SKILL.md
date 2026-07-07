---
name: loki-human-decision-preflight
description: Run the Loki `loki:human-decision-preflight` command workflow in Codex. Use before action planning to classify open decisions as ask-now, delegate-to-plan, validate-later, or answer-from-local-sources.
when_to_use:
  - "Use when running loki:human-decision-preflight before loki:generate-action-plan."
  - "Use when an analysis, brief, feedback record, or retrospective has open human decisions that may block planning."
  - "Use when deciding whether to ask the user now, delegate a detail to the plan, validate later, or answer from local sources."
argument-hint: "[analysis path, brief, open questions, target decision record]"
arguments:
  required: []
  optional:
    - analysis_path
    - brief
    - open_questions
    - target_decision_record
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - many open human decisions
  - conflicting evidence
  - sensitive writes or irreversible product choices
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-human-decision-preflight/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:human-decision-preflight
---

# loki-human-decision-preflight

## Procedure

1. Read the installed command contract:
   [loki-human-decision-preflight.md](../../commands/loki-human-decision-preflight.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions and resume
   contract.
3. Load `lf-tech-analysis-authoring` to separate facts, inferences, open
   questions and gates.
4. Load `lf-action-plan-authoring` to decide whether a pending decision can be
   represented safely as a task, validator, human loop or stop condition.
5. Classify every pending decision as `must_ask_now`, `can_delegate_to_plan`,
   `can_validate_later` or `do_not_ask_llm_can_determine`.
6. Ask at most one active `must_ask_now` question per turn.
7. Treat this skill as the Codex entrypoint for the command name
   `loki:human-decision-preflight`.

## Limits

- Do not invent human decisions, approvals, validators, file targets or answers.
- Do not write runtime, durable docs, commands, skills, agents, templates,
  validators, `manifest.yaml` or `install-scopes.json` during ordinary command
  execution.
- Do not mark `ready_for_next_phase: true` while a `must_ask_now` decision is
  unresolved.
- Do not ask the user questions that local sources or structured validation can
  answer.
