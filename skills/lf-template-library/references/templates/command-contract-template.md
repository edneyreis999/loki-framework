---
name: "loki-<stem>"
description: "<trigger complete and concrete>"
when_to_use: []
argument-hint: "<arguments>"
arguments:
  required: []
  optional: []
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: "<low|medium|high>"
model_class: "<provider-neutral class>"
adapter_projection:
  codex: "<advisory or enforced statement>"
  claude_code: "<projection statement>"
escalation_signals: []
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-<stem>/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: "<domain>"
required_skills: []
required_commands: []
status: draft
used_by: []
---

# loki-<stem>

## Input

Peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: <required-key>
    input_type: <type>
    requirement: required
    description: <description>
  - key: <optional-key>
    input_type: <type>
    requirement: optional
    default: <default>
    description: <description>
```

<Validate presence, types, formats, paths and combinations. Request missing
required data without invention. Normalize objective, parameters, scope,
constraints, destinations, approvals, gates and gaps. Prohibit the main task
and success declaration during Input.>

## Execution

Read `references/execution.md` completely before
acting and follow every additional reference it requires.

## Response

Read `references/response.md` completely and fill
`assets/response-template.md` for the terminal
response.

<!--
Required bundle tree:
skills/loki-<stem>/
├── SKILL.md
├── references/execution.md
├── references/response.md
└── assets/response-template.md

execution.md preserves purpose/start/end/result, orchestrator role, writes,
dependencies, handoffs and self-contained context, workflow/replanning, unique
write owner, validators/gates/approvals, packaging, stop and resume.
response.md declares primary consumer Both and the LLM/Humano/Both formats.
Do not add projection, command_name, package_projection or command_contract.
-->
## Contract requirements

This bundle must implement the canonical contract in
`skills/lf-command-creator/references/command-contract-template.md`. It must
declare observable purpose/start/end/output; keep Input limited to the exact
parameter request, YAML parameters, validation, missing-input request and
normalized handoff; add a session-state gate only when it is material,
trustworthily observable and compatible with the workflow; orchestrate, replan,
serialize owners/writes, validate gates and track handoffs in Execution; and
declare LLM/Humano/Both terminal formats in Response.

The execution contract must define `allowed_writes`, `forbidden_writes`, owner,
required skills/commands, validators, human gates, stop conditions and resume
state. Delegate to a scoped Write Agent where available. Direct orchestration
writes require an explicit no-writer exception and completion record with the
future-writer opportunity. Before delivery, record 24/24 explicit evidence
against the canonical checklist; any `não` blocks delivery.
