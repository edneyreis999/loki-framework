# Document Taxonomy

Use this reference when classifying a document or resolving a mixed case.

Classify documents using two axes:

- orientation: `technical`, `reader-facing`, or `agent-facing`;
- depth: `lite` or `rich`.

`reader-facing` replaces the older `human-like` label. The older label may
appear in legacy plans, but new documents should use `reader-facing`.
`agent-facing` is the canonical label for LLM-only documents.

## Selection Flow

1. If the artifact is produced by `loki-tech-analysis`, classify it as
   `technical rich`.
2. If the artifact is produced by `loki-generate-action-plan`, classify it as
   `technical rich`.
3. If the document is meant primarily for AI agents, prompt assembly, retrieval,
   routing, context hydration, deterministic reuse, or machine-readable policy,
   classify it as `agent-facing lite` or `agent-facing rich`.
4. If the document is a durable technical reference, architecture note, source
   analysis, contract, validator guide, integration guide, migration record or
   implementation decision, classify it as `technical rich`.
5. If the document is durable, reader-friendly project context and generally
   lives under `/docs`, classify it as `reader-facing rich` unless its primary job
   is a technical contract or technical reference.
6. If the document is transient and supports current plan execution with file
   paths, implementation details, validators, diffs or technical decisions,
   classify it as `technical lite`.
7. If the document is transient and supports human understanding, feedback,
   communication, decision explanation or handoff during plan execution,
   classify it as `reader-facing lite`.

When two modes seem plausible, choose the richer mode if the next reader will
need to use the document without the conversation. Choose the technical mode if
incorrect technical detail would create implementation risk.
Choose the agent-facing mode if the primary reader is an LLM or AI agent rather
than a human.

## Technical Lite

Purpose: help an agent or engineer execute, validate or resume part of a plan.

Typical destinations:

- `task-N.M.md` work notes;
- `interaction/`;
- `builds/`;
- validation notes;
- local implementation briefs;
- temporary decision notes inside a plan.

Expected shape:

- objective;
- in-scope and out-of-scope surfaces;
- source paths read;
- facts, inferences and open questions when relevant;
- concrete next action;
- validators or human gate;
- stop condition if blocked.

Avoid broad background, tutorial tone, full architecture history, repeated
project context and polished narrative.

## Technical Rich

Purpose: preserve technical reasoning or contracts for future work.

Typical destinations:

- technical analysis artifacts;
- generated action plans;
- architecture or integration references;
- durable decision records;
- validator or package policy docs;
- long-lived technical docs under `/docs`.

Expected shape:

- scope and status;
- audience and intended use;
- source map or evidence list;
- constraints and assumptions;
- decision or recommendation;
- alternatives considered when material;
- risks and open questions;
- validators and human gates;
- maintenance notes or update triggers.

`loki-tech-analysis` and `loki-generate-action-plan` outputs are technical rich
by exception because downstream workflows depend on them as self-contained
handoff artifacts, even when they are stored with transient plan files.

## Reader-Facing Lite

Purpose: communicate transient context in natural language without turning it
into durable project truth.

Typical destinations:

- feedback summaries;
- user-facing task updates;
- interview or clarification notes;
- handoff notes;
- short retrospection inputs;
- plan execution summaries.

Expected shape:

- what happened or what was decided;
- why it matters now;
- what remains open;
- who or what should act next;
- links or paths only when they are useful to resume.

These elements do not require a fixed heading order. They may appear as short
prose, bullets, a message-style note, or a few lightweight sections.

Avoid excessive headings, machine-only field lists, durable policy language and
unverified broad claims.

## Reader-Facing Rich

Purpose: explain durable project context for future humans and agents.

Typical destinations:

- `/docs/**/*.md`;
- project guides;
- product, domain, lore or workflow docs;
- onboarding and operating context;
- durable explanations of rules or terminology.

Expected shape:

- clear title and short purpose;
- reader and scope;
- durable context written without conversation dependency;
- examples or scenarios when useful;
- relationships to adjacent docs;
- maintenance expectations;
- index/catalog update when the project uses one.

Use a natural, direct voice. The document may still contain technical facts, but
its primary value is reader understanding rather than execution control. The
structure should follow the reader's path through the topic; use formal sections
only where they make the document easier to maintain or navigate.

## Agent-Facing Lite

Purpose: provide transient LLM-only context for agents executing a current plan
or task.

Typical destinations:

- temporary context packs;
- task-local retrieval notes;
- agent handoff blocks;
- structured prompt inputs;
- plan execution facts that should be easy to recover by search.

Expected shape:

- metadata at the top;
- stable headings or XML-like tags;
- explicit instructions separated from data;
- atomic facts;
- source paths and evidence labels;
- output format when the document drives generation;
- conflicts, uncertainty and deprecation marked explicitly.

Avoid narrative transitions, editorial introductions, marketing copy, hidden
assumptions, ambiguous pronouns and decorative repetition.

## Agent-Facing Rich

Purpose: preserve durable context, rules, routing, catalogs, contracts or
prompt-support material for future AI agents.

Typical destinations:

- durable agent context documents;
- package or project catalogs;
- routing and retrieval indexes;
- policy or constraint packs;
- prompt-support documents;
- LLM-readable project references under `/docs` when the project declares that
  purpose.

Expected shape:

- `doc_id`, `version`, `status`, `last_updated`, `scope`, `not_scope`,
  `authority`, `canonical_source`, and `intended_llm_task` at the top;
- source priority and conflict rules;
- chunkable sections that make sense independently;
- dense facts with one claim per bullet or record;
- examples and output schemas when generation behavior matters;
- deprecation and replacement metadata when rules change.

Read [llm-only-documents.md](llm-only-documents.md) for the detailed contract.
