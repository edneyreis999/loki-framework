---
name: lf-git-workflow
description: Shared Loki procedure for safe Git branch, commit and pull request workflows, including status preflight, explicit staging, branch naming, GitHub MCP or gh fallback, human approvals, and validation.
when_to_use:
  - "Use when a Loki command creates a Git branch, creates a commit, pushes a branch, or opens a pull request."
  - "Use when deciding whether GitHub MCP, gh CLI, or local Git is required for a source-control workflow."
argument-hint: "[branch, commit, or pull request workflow inputs]"
arguments:
  required: []
  optional:
    - workflow
    - base_branch
    - branch_name
    - commit_scope
    - pr_title
    - pr_body
disable-model-invocation: false
user-invocable: false
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: coding
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - publishing to a remote
  - branch/base ambiguity
  - secrets or generated binaries in diff
  - provider-specific pull request behavior
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/lf-git-workflow/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:criar-branch
  - loki:commit
  - loki:abrir-pr
---

# lf-git-workflow

## Purpose

Provide common operational rules for Loki Git workflows so branch creation,
commits and pull requests stay explicit, reviewable and reversible.

## Design Basis

This procedure applies these portable Git workflow patterns:

- separate branch, commit and PR actions with their own gates;
- group related changes before staging or committing;
- derive branch names and commit messages from the actual objective or diff;
- preview remote-facing PR title/body before creation;
- keep provider-specific behavior behind explicit checks instead of assuming
  every review workflow is GitHub.

## Git Preflight

Always gather the smallest useful local state before writing:

```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short
git remote -v
```

Detect the default branch from remote metadata when possible. If local detection
is ambiguous, ask the user instead of guessing between `main`, `master` or a
custom base.

## Branch Naming

Preferred branch format:

```text
<author-or-team>/<type>/<short-description>
```

Fallback format when no author prefix is available:

```text
<type>/<short-description>
```

Allowed types: `feat`, `fix`, `ref`, `docs`, `test`, `chore`, `ci`, `build`,
`perf`, `style`, `meta`, `license`.

Description rules:

- lowercase kebab-case;
- 3 to 6 meaningful words when possible;
- ASCII letters, digits and hyphens only;
- describe the change, not just filenames.

Check both local and remote references before creating a branch.

## Commit Rules

- Do not commit on `main`, `master` or the detected default branch unless the
  user explicitly asked for that.
- Prefer explicit pathspecs over `git add .`.
- If changes are unrelated, propose separate commits.
- Stop on suspected secrets, credentials or unexpected generated binaries.
- Show the complete commit message before committing.

Commit header format:

```text
<type>(<scope>): <subject>
```

Scope is optional. Subject should be imperative, present tense, capitalized,
under 70 characters and without a trailing period. Add a body when the reason
is not obvious from the diff.

## Pull Request Rules

- A PR requires committed changes on a non-default branch.
- Confirm base branch and head branch before publishing.
- Push only after approval.
- Show the full PR title and body before creation.
- Do not merge, assign reviewers, add labels or change milestones unless the
  user explicitly asks.
- Prefer draft PRs when work is incomplete or validation is partial.

PR body should include concise sections for summary, motivation, key changes,
validation and references when relevant. If the repository has a PR template,
adapt to it or ask before ignoring it.

## GitHub MCP And CLI Fallback

Use local Git for local state and commits. Use GitHub MCP for remote GitHub
objects when available, especially branch and PR operations. Fall back to `gh`
when the MCP tool is unavailable but `gh` is installed and authenticated.

Minimum optional capabilities for full GitHub operation:

- GitHub MCP: repository lookup, branch search/create and pull request create.
- `gh` CLI fallback: `gh auth status`, `gh repo view`, `gh pr create`.
- Local Git: branch/status/diff/log/add/commit/push.

Do not assume GitHub for non-GitHub remotes. Stop and report unsupported
provider unless a provider-specific skill or command is added later.

## Validation Checklist

- Current branch, base branch and remote are known or explicitly confirmed.
- Any local writes are limited to the command's allowed writes.
- User approval exists before branch creation, staging, commit, push or PR
  creation.
- Diff and status were read before commit or PR.
- The final report includes command outputs that matter: branch name, commit
  SHA or PR URL.

## Limits

- This skill does not authorize destructive Git operations.
- This skill does not replace repository-specific contribution policy.
- This skill does not install or configure MCP servers.
