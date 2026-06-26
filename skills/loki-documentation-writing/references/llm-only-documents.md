# Agent-Facing LLM-Only Documents

Use this reference when a document is meant primarily for AI agents, prompt
assembly, retrieval, routing, context hydration, deterministic reuse or
machine-readable policy.

Canonical label: `agent-facing document`.

Accepted alias: `LLM-only document`.

## Purpose

An agent-facing LLM-only document is not reader-friendly prose. It is dense,
segmented, explicit, traceable and easy to retrieve. A human may maintain it,
but the primary consumer is an LLM or agent.

## Practical Rules

1. Use stable structure, not free prose.
   Prefer Markdown headings, YAML frontmatter, XML-like tags, tables or records
   with predictable keys.
2. Separate instructions from data.
   Use blocks such as `<instructions>`, `<facts>`, `<examples>`, `<input>`,
   `<constraints>` and `<output_format>`. Mark untrusted or user-provided
   content as data, not commands.
3. Put metadata at the top.
   Required fields: `doc_id`, `version`, `status`, `last_updated`, `scope`,
   `not_scope`, `authority`, `canonical_source`, `intended_llm_task`.
4. Write atomic facts.
   Use one claim per bullet, line or record. Avoid ambiguous pronouns,
   metaphors, implicit references, "etc.", "as above" and unstated context.
5. Include expected output format and examples when the document controls
   generation.
   Add positive examples and negative examples when the distinction matters.
6. Front-load critical information.
   Put summary, source priority, conflict rules and critical constraints near
   the top. For long context blocks, put the specific task or question at the
   end with a clear anchor such as `Based on the information above`.
7. Chunk by semantic unit.
   Each section should make sense if retrieved alone: canonical title, short
   summary, scope, content, references and update trigger.
8. Remove human-only filler.
   No editorial intro, welcome text, marketing copy, decorative transitions,
   long history, redundant navigation or literary tone.
9. Mark conflicts, uncertainty and deprecation explicitly.
   Use fields such as `status`, `deprecated`, `replaced_by`, `confidence`,
   `known_conflicts`, `source_priority` and `last_verified`.

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
