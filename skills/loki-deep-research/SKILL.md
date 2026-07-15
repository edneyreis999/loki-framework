---
name: loki-deep-research
description: Run the Loki `loki:deep-research` command workflow in Codex. Use when the user asks for deep research on the internet, web research with citations, multi-source investigation, source credibility analysis, contradiction mapping, or a sourced research report before analysis, planning, or decision-making.
when_to_use:
  - "Use when running loki:deep-research for internet/web deep research."
  - "Use when the output needs cited sources, query methodology, credibility checks, contradictions, assumptions, gaps, and next-step handoff."
argument-hint: "[research question, scope, depth, source constraints, destination]"
arguments:
  required: []
  optional:
    - research_question
    - scope
    - depth
    - source_constraints
    - destination
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - broad or ambiguous research scope
  - conflicting or weak external sources
  - high-stakes legal, medical, financial, security or compliance claims
  - expensive multi-lane or long-running web research
context: standard
agent: main
hooks: []
paths:
  package_projection: "skills/loki-deep-research/SKILL.md"
  command_contract: "commands/loki-deep-research.md"
shell: {}
type: command
projection: installable-skill
command_name: loki:deep-research
status: draft
used_by:
  - loki:deep-research
---

# loki-deep-research

## Procedure

1. Read the installed command contract:
   [loki-deep-research.md](../../commands/loki-deep-research.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load `lf-web-deep-research` before running web research or writing the
   research report.
4. Load `lf-index-navigator` first when durable consumer docs must constrain or
   contextualize the internet research.
5. Treat this command projection as the Codex entrypoint for the command name
   `loki:deep-research`.

## Limits

- Do not write runtime, code, generated data, sensitive consumer surfaces, or
  package artifacts during research.
- Do not turn sourced research into implementation, policy, or durable docs
  without the follow-up command and gate named in the command contract.
- Do not present unsupported claims as facts; mark them as inference,
  assumption, gap, or contradiction.
