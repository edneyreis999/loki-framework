---
name: loki-criar-branch
description: Run the Loki `loki:criar-branch` command workflow in Codex. Use when the user asks to create, start, switch to, or propose a Git branch for new work.
when_to_use:
  - "Use when running loki:criar-branch."
  - "Use when a user asks for a new Git branch with safe base detection and naming."
argument-hint: "[work description, branch type, base branch]"
arguments:
  required: []
  optional:
    - work_description
    - branch_type
    - base_branch
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
  - detached HEAD
  - ambiguous default branch or remote
  - uncommitted changes while changing base branch
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-criar-branch/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:criar-branch
---

# loki-criar-branch

## Procedure

1. Read the installed command contract:
   [loki-criar-branch.md](../../commands/loki-criar-branch.md).
2. Load `lf-git-workflow`.
3. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   validators, gates, stop conditions and resume contract.
4. Treat this skill as the Codex entrypoint for `loki:criar-branch`.

## Limits

- Do not commit, push or open a PR.
- Do not run destructive Git operations.
