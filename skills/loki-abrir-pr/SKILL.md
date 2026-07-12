---
name: loki-abrir-pr
description: Run the Loki `loki:abrir-pr` command workflow in Codex. Use when the user asks to open or prepare a Pull Request from the current branch using GitHub MCP when available or gh CLI as fallback.
when_to_use:
  - "Use when running loki:abrir-pr."
  - "Use when a user asks to create, open, draft, or prepare a GitHub Pull Request."
argument-hint: "[base branch, title, body, draft flag, references]"
arguments:
  required: []
  optional:
    - base_branch
    - title
    - body
    - draft
    - references
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: coding
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - uncommitted changes
  - unpublished branch
  - provider-specific PR behavior
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-abrir-pr/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:abrir-pr
---

# loki-abrir-pr

## Procedure

1. Read the installed command contract:
   [loki-abrir-pr.md](../../commands/loki-abrir-pr.md).
2. Load `lf-git-workflow`.
3. Prefer GitHub MCP for PR creation when the active adapter exposes a
   compatible tool; otherwise use authenticated `gh` as fallback.
4. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   validators, gates, stop conditions and resume contract.
5. Treat this skill as the Codex entrypoint for `loki:abrir-pr`.

## Limits

- Do not create a PR without approval of title, body, base and head.
- Do not merge, label, assign reviewers or alter milestones unless explicitly
  requested.
