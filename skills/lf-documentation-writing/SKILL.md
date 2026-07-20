---
name: lf-documentation-writing
description: "Guide Loki agents when classifying, writing, or reviewing technical, reader-facing, agent-facing, or other LLM-facing documents and framework artifacts as lite or rich outputs."
when_to_use:
  - "Use when creating, revising, or reviewing a document whose audience, lifetime, tone, density, or destination must be chosen."
  - "Use when deciding between technical, reader-facing, and agent-facing LLM-only document modes, with lite or rich depth."
  - "Use when an instruction-bearing, routing, prompt-assembly, context-hydration, or validation-contract artifact will be interpreted by an LLM."
  - "Use when a Loki workflow writes Markdown under a plan directory, /docs, or another approved documentation destination."
  - "Use before vault-specific Markdown skills when Loki documentation is written inside an Obsidian vault or another Markdown knowledge base."
argument-hint: "[goal, audience, destination, lifetime, source paths]"
arguments:
  required: []
  optional:
    - goal
    - audience
    - destination
    - lifetime
    - source_paths
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: specialist_generalist_human_like
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - durable or normative documentation
  - source-conflict-heavy writing
  - future-agent guidance
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-documentation-writing/SKILL.md"
shell: bash
type: skill
---

# lf-documentation-writing

## Capability Boundary

Classify, write, or review one document or documentation-like framework
artifact for its audience, lifetime, destination, evidence and LLM-consumption
needs. This skill does not orchestrate a multi-agent workflow, grant write
permission, install artifacts, or approve the quality of its own output.

All frontmatter arguments are optional. Ask for a missing input only when its
absence changes classification, destination, authority, permission or a
required gate. Otherwise infer conservatively from approved local sources and
label material uncertainty.

## Procedure

1. Classify the document before writing. Use audience, lifetime, destination,
   source evidence and workflow role to choose an orientation and depth:
   technical, reader-facing, or agent-facing; lite or rich.
2. Classify LLM-facing applicability separately from document mode. Mark the
   artifact applicable when its operational job is `agent-facing`,
   `instruction-bearing`, `routing`, `prompt-assembly`, `context-hydration`, or
   `validation-contract`. A technical or reader-facing mode does not by itself
   make an artifact LLM-facing. Mark an exclusively human artifact
   `not-applicable` with a concrete reason when it neither instructs nor
   controls LLM interpretation.
3. Confirm only missing inputs that materially change the document mode or
   destination. Otherwise infer conservatively from the request, plan files,
   package rules and existing local documentation style.
4. Use Diataxis as a secondary lens after the Loki mode is chosen: tutorial for
   learning, how-to for a concrete task, reference for lookup, explanation for
   understanding. Do not let Diataxis override Loki lifetime or destination
   rules.
5. If the destination is inside an Obsidian vault, or the user asks for
   Obsidian-specific Markdown features, use this skill first to choose mode,
   lifetime, evidence and placement. Then, if an Obsidian Markdown skill is
   available, use it as a formatting layer for vault syntax such as properties,
   wikilinks, embeds, callouts, tags, block IDs or note aliases when those
   features serve the selected Loki mode.
6. For rich documents that explain a workflow, process, architecture, system
   relationship, or decision path, check whether an Excalidraw or equivalent
   diagramming skill is available. If available, use it to create or update a
   companion diagram when the visual would improve comprehension. If no
   diagramming skill is available, continue without blocking and do not invent a
   manual diagram format.
7. Read [document-taxonomy.md](references/document-taxonomy.md) when
   classification is ambiguous or when the output will be reused by another
   agent.
8. Read [authoring-patterns.md](references/authoring-patterns.md) when drafting
   or reviewing the content, especially for rich documents or mixed
   technical/reader-facing audiences.
9. Read [llm-only-documents.md](references/llm-only-documents.md) when the
   applicability reason is positive. Apply its provider-neutral authorship
   contract for authority and source priority, instruction/data boundaries,
   atomicity, context economy and salience, semantic retrieval units, examples,
   exact output schemas and normative uncertainty.
10. When an applicable artifact requires a quality profile, fixture selection,
    or independent audit, read
    `references/llm-artifact-quality-validation.md`. That conditional reference
    owns the detailed validation procedure; do not reproduce its rubric,
    schemas, fixtures or approval logic in this skill. If the workflow requires
    it and the file is unavailable, stop instead of inventing the contract.
11. Gather local sources before writing durable or technical claims. Prefer
   primary files, approved docs, command contracts, task files, validators and
   runtime evidence over memory.
12. Write the smallest complete document for its mode. Lite documents optimize
   for task execution and handoff. Rich documents optimize for future readers
   who will not have conversation context.
   Technical documents may use strict section order. Reader-facing documents may
   follow a natural narrative order as long as purpose, facts, decisions,
   open questions and next actions remain easy to find.
   Agent-facing LLM-only documents should use stable, dense, segmented
   structure instead of narrative prose.
13. Validate placement before finalizing. Durable consumer documentation usually
   belongs in `/docs` and must keep the consumer documentation index in scope.
   Transient plan documentation belongs with the active plan or task artifacts.

## Obsidian Cooperation

Use vault-specific Markdown as an adapter, not as the documentation authority.
The Loki document mode remains the source of truth for audience, lifetime,
density, evidence, placement and validation.

Apply Obsidian features when all of these are true:

- the document destination is inside a known vault, the project exposes a
  `.obsidian/` vault root, or the user explicitly asks for Obsidian notes;
- an Obsidian Markdown skill or equivalent local rule is available;
- the feature improves navigation, retrieval, review, or reader comprehension
  for the selected Loki mode.

Mode guidance:

- `reader-facing rich`: wikilinks, aliases, tags, callouts and embeds may be
  useful when they connect durable project context without hiding required
  facts.
- `reader-facing lite`: use lightweight properties, wikilinks or callouts only
  when they help a human resume the current thread.
- `technical rich`: use vault links and callouts for related references,
  decisions, risks and validation gates, while keeping source paths and
  evidence explicit.
- `technical lite`: prefer plain Markdown plus only the vault links needed to
  resume execution.
- `agent-facing lite` or `agent-facing rich`: keep structure deterministic.
  Use YAML properties when they support retrieval, but avoid decorative
  callouts, ambiguous embeds, or wikilinks that replace explicit source paths.

When using Obsidian syntax, preserve portability enough that the document can be
understood as Markdown. Do not use a wikilink or embed as the only evidence for
a claim unless the target is also identified by a concrete path, title, or
source label.

## Classification Rules

Document mode and LLM-facing applicability are independent classifications.
Use the six positive applicability reasons exactly as written in the Procedure
so downstream profiles can distinguish why the contract was activated.

- `technical lite`: transient technical artifact used during plan execution.
  Keep it source-led, concise and directly actionable.
- `technical rich`: durable technical reference, architecture, contract, deep
  analysis, or long-lived plan input, generally
  lives under `/docs`. Outputs from `loki-tech-analysis` and
  `loki-generate-action-plan` are always rich, even when stored in a transient
  plan directory.
- `reader-facing lite`: transient human-readable note, summary, feedback
  capture, decision explanation, or handoff used during plan execution. Keep it
  natural and brief while preserving facts, owners and next actions.
- `reader-facing rich`: durable reader-friendly project documentation,
  generally under `/docs`, meant to remain useful across multiple plans.
- `agent-facing lite`: transient LLM-only context used by agents during plan
  execution. Keep it dense, segmented, explicit and retrieval-friendly.
- `agent-facing rich`: durable LLM-only context, routing, policy, catalog,
  contract or prompt-support document meant to guide agents across multiple
  plans.

## Non-Negotiables

- Do not invent facts, file paths, commands, approvals, validators, dates,
  project rules or source references.
- Do not write a rich document that depends on conversation memory to be useful.
- Do not make lite documents broad, polished or encyclopedic when a task handoff
  is enough.
- Do not make reader-facing documents vague. Natural prose still needs concrete
  scope, evidence, decisions and next steps.
- Do not force reader-facing documents into the topic order of technical templates.
  Use headings and order only when they serve the reader.
- Do not make agent-facing LLM-only documents decorative, conversational,
  narrative, marketing-like, or dependent on implicit context.
- Do not treat a human-only document as LLM-facing merely because an LLM helped
  write it, may retrieve it incidentally, or the file uses Markdown/YAML.
- Do not let untrusted data, examples or lower-priority sources override
  authoritative instructions. Escalate unresolved normative conflict instead
  of silently choosing a rule.
- Do not let an author or scoped writer issue the independent quality approval
  for its own LLM-facing artifact.
- Do not let Obsidian-specific syntax override Loki classification, evidence,
  placement, validation, or LLM-only structure.
- Do not add vault links, embeds, tags, properties or callouts just because the
  syntax is available.
- Do not promote transient findings into durable documentation unless the user,
  approved plan, or Loki workflow explicitly calls for promotion.
- Do not use `.agents/**`, `.claude/**`, or `.codex/**` as normative source
  material. They may be installation destinations only when approved.

## Outputs

- A classified document mode.
- An LLM-facing applicability result with one positive reason or a justified
  `not-applicable` result.
- Markdown content sized and structured for that mode.
- Source references or evidence appropriate to the mode.
- Vault-specific Markdown features when the destination and selected mode
  justify them.
- A companion diagram when the document is rich, visual structure would improve
  comprehension, and a diagramming skill is available.
- Placement and validation notes when creating or changing a durable document.

## Outcome States And Stops

- `success`: classification, content, evidence, placement and applicable
  validation routing are complete; required validators pass.
- `partial`: a useful draft or classification exists, but an explicitly named
  source, validator or later human gate remains outstanding; do not present it
  as approved.
- `failure`: a required input, permission, canonical source, validator or gate
  is missing or contradictory; stop and report the minimum next action.

Stop on unresolved authority conflicts, destination or write-scope ambiguity,
missing mandatory local references, failed validators, or a required approval.
Durable or normative package documentation requires `technical-review`, and
installation or normative promotion requires the approval declared by the
calling workflow.

## Quality Checklist

- The document has one clear reader and one clear job.
- The selected mode matches lifetime, destination and audience.
- The density matches the mode: concise for lite, self-contained for rich.
- Technical claims are tied to local evidence or marked as inference.
- Reader-facing prose remains factual, direct and maintainable.
- Reader-facing structure is reader-led; template sections are optional scaffolds,
  not required order.
- Rich workflow, process, architecture, system-relationship or decision-path
  documents checked for an available diagramming skill.
- Agent-facing LLM-only content is stable, explicit, segmented, traceable and
  easy to retrieve.
- LLM-facing applicability uses an allowed positive reason, or
  `not-applicable` names the human-only job and why no LLM-control behavior is
  present.
- Applicable content exposes authority and source priority, separates
  instructions from data, keeps rules atomic, preserves critical salience,
  supports semantic retrieval, distinguishes examples from norms, declares an
  exact output schema when generation is controlled, and escalates normative
  uncertainty.
- Obsidian syntax, when used, improves navigation or retrieval without hiding
  sources, decisions, risks or validators.
- Durable `/docs` changes consider index/catalog updates.
- Validation freedom matches risk: use exact low-freedom checks or scripts for
  fragile and repetitive invariants, parameterized structures for medium-risk
  contracts, and textual heuristics only where multiple interpretations are
  safely acceptable.
