---
name: loki-feedback
description: Run the Loki `loki:feedback` command workflow in Codex. Diagnose software or game project feedback through a strict one-question-at-a-time interview before proposing any fix; use when the user reports validation feedback, visual bugs, gameplay or product feel, UX problems, audio/input issues, unexpected runtime behavior, integration symptoms, or other observed symptoms.
when_to_use:
  - "Use when diagnosing validation feedback, visual bugs, gameplay/product feel, UX problems, audio/input issues, runtime behavior, or integration symptoms."
  - "Use when a one-question-at-a-time interview is required before proposing a fix."
argument-hint: "[feedback, observed behavior, expected behavior, context]"
arguments:
  required: []
  optional:
    - feedback
    - observed_behavior
    - expected_behavior
    - context
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
  - external research is required
  - feedback conflicts with local evidence
  - high-risk technical proposal
context: standard
agent: main
hooks: []
paths:
  package_projection: "skills/loki-feedback/SKILL.md"
  command_contract: "commands/loki-feedback.md"
shell: {}
type: command
projection: installable-skill
command_name: loki:feedback
status: draft
used_by:
  - loki:feedback
---

# loki-feedback

## Procedure

1. Read the installed command contract:
   [loki-feedback.md](../../commands/loki-feedback.md).
2. Treat the paired command contract as the canonical operational source and
   follow its inputs, outputs, allowed writes, forbidden writes, gates,
   handoffs, stop conditions, and resume contract.
3. Read the
   [Diagnostic Output and Forward-Test Contract](references/diagnostic-output-and-forward-test.md)
   when explicit response states are needed or when validating this projection.
4. Keep ordinary feedback execution read-only and proposal-only. Normalize the
   report, separate facts from inferences and hypotheses, and ask at most one
   objective question while critical ambiguity remains.
5. Do not perform external research until the user has approved the exact
   proposed search phrase.
6. When the diagnosis identifies a probable correction, provide a textual
   implementation handoff and ask for authorization before leaving diagnostic
   mode.
7. Treat this projection as the Codex entrypoint for `loki:feedback`.

## Limits

- Do not apply the proposed correction from this command projection.
- Do not write durable artifacts except through the retrospective exception
  explicitly authorized by the paired command contract.
- Do not claim perceptible or runtime behavior as validated without explicit
  human confirmation.
- Do not continue to a final diagnosis while a critical question remains open.
