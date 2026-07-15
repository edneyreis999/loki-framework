---
name: loki-commit
description: Run the Loki `loki:commit` command workflow in Codex. Use when the user asks to commit local changes with explicit staging, conventional message, branch safety, and validation.
when_to_use:
  - "Use when running loki:commit."
  - "Use when a user asks to commit, save changes in Git, or prepare a commit message for local changes."
argument-hint: "[files or scope, message, type, issue references]"
arguments:
  required: []
  optional:
    - files
    - message
    - commit_type
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
  - mixed unrelated changes
  - suspected secrets or binaries
  - default branch commit request
context: standard
agent: main
hooks: []
paths:
  package_projection: "skills/loki-commit/SKILL.md"
  command_contract: "commands/loki-commit.md"
shell: {}
type: command
projection: installable-skill
command_name: loki:commit
status: draft
used_by:
  - loki:commit
---

# loki-commit

## Procedure

1. Read the installed command contract:
   [loki-commit.md](../../commands/loki-commit.md).
2. Load `lf-git-workflow`.
3. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   validators, gates, stop conditions and resume contract.
4. Treat this command projection as the Codex entrypoint for `loki:commit`.

## Limits

- Do not push, open a PR, merge or alter remotes.
- Do not commit on the default branch without explicit user request.
