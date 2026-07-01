# Authoring Patterns

Use this reference when drafting or reviewing document content.

## Intake

Before writing, identify:

- document goal;
- primary reader;
- expected lifetime;
- destination path;
- source paths or evidence;
- in-scope and out-of-scope topics;
- required validators, approvals or index updates.

Ask only when the answer changes mode, placement, or validation. Otherwise make
a conservative assumption and state it in the document when useful.

## Diataxis Lens

After selecting the Loki mode, use Diataxis to tune structure:

- tutorial: teach by walking through a successful path;
- how-to: solve one concrete problem;
- reference: make facts easy to look up;
- explanation: build understanding and context.

Most Loki plan artifacts are how-to, reference, or explanation. Avoid tutorial
structure unless the reader is intentionally learning a process from scratch.

## Structure Guidance

Treat technical patterns as stronger section templates when precision,
validation, or downstream execution depends on predictable fields.

Treat reader-facing patterns as optional scaffolds. Reader-facing documents can
reorder topics, collapse sections into prose, or use a narrative flow when that
better serves the reader. They still need concrete purpose, verified facts,
decisions, open questions and next steps when those concepts are relevant.

Treat agent-facing LLM-only patterns as strict structure. Prefer predictable
headings, YAML frontmatter, XML-like tags, atomic facts and stable field names.
Do not optimize agent-facing documents for human polish.

## Technical Lite Pattern

Use terse sections and concrete evidence.

```markdown
# <Task Or Topic>

## Objective
<One or two sentences.>

## Sources
- `<path>`: <why it matters>

## Current State
- Fact: <verified detail>
- Inference: <labeled inference>

## Next Action
<Concrete action or blocked question.>

## Validation
<Command, check, human gate, or not-run reason.>
```

## Technical Rich Pattern

Make the artifact self-contained enough for future planning or implementation.

```markdown
---
title: <Title>
type: <analysis|plan|reference|decision|guide>
status: <draft|approved|superseded>
---

# <Title>

## Purpose
<Why this exists and who should use it.>

## Scope
<Included and excluded surfaces.>

## Sources
- `<path>`: <evidence role>

## Findings
<Facts first, then labeled inferences.>

## Decision Or Recommendation
<Chosen direction and rationale.>

## Risks And Open Questions
<What remains uncertain or gated.>

## Validation
<Automated checks, human gates, or not-run reasons.>

## Maintenance
<When this should be updated or retired.>
```

## Reader-Facing Lite Pattern

Use prose that a person can scan quickly. This is a possible shape, not a
required order.

```markdown
# <Short Title>

<Brief context paragraph.>

## What Matters Now
- <Concrete point>
- <Concrete point>

## Next Step
<Action, owner, or question.>
```

## Reader-Facing Rich Pattern

Write for a future reader who has no chat history. This is a possible shape, not
a required order.

```markdown
---
title: <Title>
type: <guide|context|reference|workflow|explanation>
status: <draft|active|superseded>
---

# <Title>

## Purpose
<Reader, goal and why the document exists.>

## Context
<Durable background, not task chatter.>

## Main Content
<Organized around reader goals.>

## Related Documents
- `<path or doc title>`: <relationship>

## Maintenance
<Owner, trigger, or update rule when known.>
```

## Review Pass

For every mode, check:

- does the title tell the reader what this is;
- does the first section establish purpose and scope;
- are facts separated from assumptions when risk matters;
- are paths, commands and validators accurate;
- is the document too dense for a reader-facing mode or too vague for a technical
  mode;
- does a reader-facing document use structure because it helps the reader, not
  because a template listed sections in that order;
- does an agent-facing LLM-only document avoid free prose and expose stable
  retrieval anchors, metadata, source priority and conflict status;
- is a rich document independent of conversation memory;
- is a lite document short enough to remain operational.
