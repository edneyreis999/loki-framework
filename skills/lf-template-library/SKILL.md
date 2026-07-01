---
name: lf-template-library
description: Use installed Loki templates from Codex. Trigger when creating or reviewing Loki technical analyses, action plans, task files, command contracts, component contracts, or project documentation indexes that should follow the package templates.
when_to_use:
  - "Use when creating or reviewing Loki technical analyses, action plans, task files, command contracts, component contracts, or project documentation indexes."
  - "Use when an installed package template should be loaded before writing an artifact."
argument-hint: "[template kind, artifact destination]"
arguments:
  required: []
  optional:
    - template_kind
    - artifact_destination
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: long_context
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - template contract changes
  - durable package documentation changes
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/lf-template-library/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:tech-analysis
  - loki:generate-action-plan
  - loki:continuous-improvement
---

# lf-template-library

## Purpose

Expose Loki templates to Codex as skill references. Codex has no project-level
template directory equivalent to a runtime command surface, so this skill
exposes package templates through `references/templates/`. Installers may also
link the package `templates/` directory to `.agents/templates/` as a local
inspection mirror.

## Template Map

- Technical analysis:
  [technical-analysis-template.md](references/templates/technical-analysis-template.md)
- Action plan index:
  [tasks-template.md](references/templates/tasks-template.md)
- Action plan task:
  [task-template.md](references/templates/task-template.md)
- Command contract:
  [command-contract-template.md](references/templates/command-contract-template.md)
- Component contract:
  [component-contract-template.md](references/templates/component-contract-template.md)
- Project docs index:
  [project-doc-index-template.xml](references/templates/project-doc-index-template.xml)

## Procedure

1. Select the smallest template that matches the requested artifact.
2. Read the corresponding template from `references/templates/`.
3. Fill placeholders with evidence from the active task, approved plan, user
   decision, or available project context.
4. Preserve required headings, frontmatter fields, validators, gates, and resume
   information unless the user explicitly changes the contract.

## Limits

- Templates are scaffolds, not evidence. Do not fill fields with invented paths,
  approvals, validators, runtime facts, or user decisions.
- Use `templates/` for package content. The installed `.agents/templates/`
  path is only a local inspection mirror.
