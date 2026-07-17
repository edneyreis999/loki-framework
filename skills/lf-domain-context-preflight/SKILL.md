---
name: lf-domain-context-preflight
description: Select the smallest sufficient read-only durable domain context before a domain Write Agent proposes or performs an ordinary task write. Use when an installed domain specialist receives a self-contained task envelope and must inspect its own durable documentation without scanning the whole domain folder or changing consumer docs.
when_to_use:
  - "Use before a domain Write Agent starts its ordinary proposal or scoped-write preflight."
  - "Use when task topics or domain IDs can route a minimal read of the agent's durable domain folder."
  - "Use to classify missing, stale, inaccessible, or cross-domain durable context without editing documentation."
argument-hint: "[agent, task_id, task_context, domain_docs_root, optional current_sources]"
arguments:
  required:
    - agent
    - task_id
    - task_context
    - domain_docs_root
  optional:
    - current_sources
    - material_context_requirements
    - documentation_handoff_destination
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
  - material context has no current or durable substitute
  - relevant durable and current sources conflict
  - required context belongs to another domain
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-domain-context-preflight/SKILL.md"
  preflight_contract: "references/preflight-contract.md"
shell: bash
type: skill
---

# lf-domain-context-preflight

## Purpose

Perform one reusable capability: let the domain Write Agent select and report
the smallest sufficient durable context for its assigned task before its normal
proposal or write preflight. This capability is read-only and does not
orchestrate the task, other agents, global handoffs, or resume state.

## Inputs

Required:

- `agent`: stable identity of the domain Write Agent;
- `task_id`: stable identity of the assigned task;
- `task_context`: self-contained objective, unit of work, relevant surfaces,
  known facts, scope, targets, constraints, validators, and gates;
- `domain_docs_root`: the resolved durable documentation folder owned by the
  agent's domain.

Optional:

- `current_sources`: current project sources or observations available to the
  task, with paths or locators and freshness evidence;
- `material_context_requirements`: facts or decisions that must be known to
  execute safely;
- `documentation_handoff_destination`: the caller-provided documentation
  librarian/catalogador route for narrow cross-domain lookup or durable gaps.

If a required input is absent, ambiguous, unreadable, or not resolved to one
task/domain, stop before reading and return `blocked` with the minimum next
input. Never invent an identity, path, permission, fact, or materiality rule.

## Procedure

1. Read [preflight-contract.md](references/preflight-contract.md) completely
   before executing this preflight. It defines the output schema, deterministic
   decisions, freshness rules, stops, and conceptual fixtures.
2. Extract normalized `task_topics`, `task_domain_ids`, relevant surfaces, and
   material context requirements from `task_context`. Do not broaden the task.
3. Resolve and normalize `domain_docs_root`. If it exists, attempt its
   `README.md` first. Use README routes plus exact topic, domain-ID, and surface
   matches to choose candidate documents.
4. Read only the smallest candidate set needed to cover the normalized task.
   Never indiscriminately scan or preload the whole durable folder.
5. Compare relevant durable facts with available current sources. Current
   project evidence outranks stale durable documentation; preserve the durable
   conflict as an explicit gap instead of changing the document.
6. Apply the decision table in the reference and emit exactly one terminal
   result: `ready`, `ready-with-gaps`, or `blocked`.
7. Only after `ready` or `ready-with-gaps` may the caller begin its separate
   ordinary proposal or scoped-write preflight.

## Outputs

Return one `domain_context_preflight` record conforming to the reference. It
must identify inputs, README attempt, documents read, selection reasons,
relevant facts, freshness evidence, conflicts, gaps, cross-domain handoff,
result, result reason, and minimum next input when blocked.

- Success: `ready` — sufficient relevant context is available with no known
  material gap.
- Partial completion: `ready-with-gaps` — execution can proceed safely while
  explicit non-material, substituted, absent-folder, stale, or unavailable
  context gaps remain.
- Failure: `blocked` — a demonstrated material requirement lacks a trustworthy
  substitute, or a required input/permission/read is unresolved.

## Limits And Stops

- Remain read-only. Do not create, edit, move, delete, reconcile, or authorize
  writes to consumer documentation.
- Do not use this skill to produce research packets, publication batches,
  completion records, or session evidence.
- Do not read outside `domain_docs_root` directly. When another domain is
  material, return a narrow lookup handoff through the caller-provided
  documentation librarian/catalogador mechanism.
- Do not treat a missing folder as automatically blocking. Default it to
  `ready-with-gaps`; block only when materiality is demonstrated and no current
  substitute exists.
- Stop on path ambiguity, denied read permission, an unresolved material
  conflict, or any request to expand this capability into task orchestration or
  documentation writing.

## Validation

Validate that the returned record:

- parses as one schema-version `1` mapping;
- uses exactly one allowed terminal result;
- records a README attempt before any domain document read when the root exists;
- links every selected document to a task topic, domain ID, or relevant surface;
- records freshness and makes current source evidence prevail over stale docs;
- contains no documentation write or broad-folder-scan authorization;
- supplies `minimum_next_input` for every `blocked` result.

Packaged changes to this skill require `technical-review`.
