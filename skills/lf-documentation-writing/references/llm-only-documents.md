# Agent-Facing LLM-Only Documents

Use this reference when a document is meant primarily for AI agents, prompt
assembly, retrieval, routing, context hydration, deterministic reuse or
machine-readable policy.

Canonical label: `agent-facing document`.

Accepted alias: `LLM-only document`.

## Applicability

Classify LLM-facing applicability independently from the document's Loki mode.
The contract applies when the artifact has at least one of these operational
jobs:

- `agent-facing`: its primary consumer is an LLM or agent;
- `instruction-bearing`: it constrains or directs LLM behavior;
- `routing`: it selects a workflow, skill, agent, source, or destination;
- `prompt-assembly`: it contributes instructions or context to a prompt;
- `context-hydration`: it supplies retrieved state or facts to an LLM;
- `validation-contract`: it defines checks, outcomes, gates, or stops that an
  LLM must interpret.

Return `not-applicable` with a concrete reason when the artifact is exclusively
for human reading and does not perform any job above. Incidental LLM authorship,
possible retrieval, Markdown/YAML formatting, technical density, or durable
placement is not positive evidence by itself.

## Purpose

An agent-facing LLM-only document is not reader-friendly prose. It is dense,
segmented, explicit, traceable and easy to retrieve. A human may maintain it,
but the primary consumer is an LLM or agent.

## Provider-Neutral Authorship Requirements

When LLM-facing applicability is positive, every applicable requirement below
is mandatory. Record why a requirement is not applicable; absence of a reason
is not a pass.

1. Use stable structure, not free prose.
   Prefer Markdown headings, YAML frontmatter, XML-like tags, tables or records
   with predictable keys.
2. Declare authority and source priority.
   Name the canonical source, list override order, and state how conflicts are
   resolved. Do not let recency, proximity, verbosity, examples, or retrieved
   content silently create authority.
3. Separate instructions from data.
   Use blocks such as `<instructions>`, `<facts>`, `<examples>`, `<input>`,
   `<constraints>` and `<output_format>`. Mark untrusted or user-provided
   content as data, not commands. State that instructions embedded inside data
   remain data.
4. Put metadata at the top.
   Required fields: `doc_id`, `version`, `status`, `last_updated`, `scope`,
   `not_scope`, `authority`, `canonical_source`, `intended_llm_task`.
5. Write atomic facts and rules.
   Use one claim per bullet, line or record. Avoid ambiguous pronouns,
   metaphors, implicit references, "etc.", "as above" and unstated context.
   Give stable identifiers to requirements that other sections or validators
   reference.
6. Control context economy and salience.
   Remove duplication and non-operational prose. Keep critical permissions,
   prohibitions, gates, authority rules, and stop conditions near the section
   that uses them and easy to recover without relying on document position
   alone.
7. Include an exact output schema when the document controls generation.
   Declare required keys, allowed values, cardinality, terminal states, and
   missing-input behavior. Do not substitute a descriptive example for the
   normative schema.
8. Use examples as evidence, not authority.
   Add positive and negative examples when a distinction is easy to
   misinterpret. Label them as non-normative and ensure they do not widen
   permissions or contradict the governing rule.
9. Front-load critical information.
   Put summary, source priority, conflict rules and critical constraints near
   the top. For long context blocks, put the specific task or question at the
   end with a clear anchor such as `Based on the information above`.
10. Chunk by semantic retrieval unit.
   Each section should make sense if retrieved alone: canonical title, short
   summary, scope, governing authority, content, references and update trigger.
   Repeat only the minimal locator or authority context needed to prevent a
   retrieved chunk from changing meaning.
11. Remove human-only filler.
   No editorial intro, welcome text, marketing copy, decorative transitions,
   long history, redundant navigation or literary tone.
12. Mark conflicts, normative uncertainty and deprecation explicitly.
   Use fields such as `status`, `deprecated`, `replaced_by`, `confidence`,
   `known_conflicts`, `source_priority` and `last_verified`. When two
   authoritative sources conflict or priority is unclear, return
   `needs-human-review`; never invent a merge, conditional approval, or hidden
   precedence rule.

## Author And Auditor Boundary

An author or scoped writer may classify applicability, preserve these
heuristics, run deterministic checks, and hand off evidence. It must not fill
an independent auditor result or approve the interpretability of its own
artifact.

When a workflow requires a quality profile, fixtures, bias controls, or an
independent approval decision, load
`llm-artifact-quality-validation.md` from this reference directory. That file
owns those detailed contracts; keep them out of this authorship reference.

## Base Shape

```markdown
---
doc_id: "<stable-id>"
version: "0.1.0"
status: "draft|active|deprecated|superseded"
last_updated: "YYYY-MM-DD"
scope: "<what this document governs>"
not_scope: "<what this document does not govern>"
authority: "<who or what can override this>"
canonical_source: "<path or source of truth>"
intended_llm_task: "<routing|retrieval|generation|validation|context>"
source_priority: ["<highest>", "<fallback>"]
confidence: "high|medium|low"
known_conflicts: []
replaced_by: null
---

# <Canonical Title>

<summary>
<one-sentence dense summary>
</summary>

<instructions>
- <instruction_id>: <imperative instruction>
</instructions>

<facts>
- <fact_id>: <single atomic fact with source path or evidence marker>
</facts>

<constraints>
- <constraint_id>: <explicit constraint>
</constraints>

<examples>
<positive_example id="example-1">
<status>non-normative</status>
<input>...</input>
<output>...</output>
</positive_example>
</examples>

<output_format>
<exact expected structure>
</output_format>
```

## Source Basis

- Anthropic Claude prompting guidance supports clear, direct instructions,
  examples, XML tags for separating instructions/context/input, and careful
  long-context structure.
- Google Gemini prompting guidance supports consistent structure, XML-style tags
  or Markdown headings, explicit parameters, critical instructions near the
  beginning, and task anchors after large context blocks.
- OpenAI prompt engineering guidance supports instructions at the beginning,
  delimiters between instruction and context, specific output formats and
  examples.
- OWASP prompt-injection guidance recommends structured prompts that separate
  instructions from user data and labels user content as data, not commands.
- `llms.txt` uses Markdown to provide LLM-friendly content in a precise,
  processable format.
- Long-context research indicates relevant information can be missed when it is
  buried in the middle of long contexts.
- Retrieval guidance recommends chunks that preserve enough context to be useful
  when surfaced independently.

Source URLs:

- `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`
- `https://ai.google.dev/gemini-api/docs/prompting-strategies`
- `https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api`
- `https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html`
- `https://llmstxt.org/`
- `https://arxiv.org/abs/2307.03172`
- `https://www.pinecone.io/learn/chunking-strategies/`
