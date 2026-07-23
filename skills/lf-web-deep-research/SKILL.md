---
name: lf-web-deep-research
description: Conduct reusable Loki web deep research with internet searches, source selection, credibility checks, citations, contradiction mapping, assumptions, gaps, and a structured handoff for `loki-deep-research`, technical analysis, planning, or human decisions.
when_to_use:
  - "Use when a Loki workflow needs deep research on the internet or web sources."
  - "Use when producing a sourced research report with methodology, citations, credibility assessment, contradictions, and gaps."
  - "Use when external current information is material and must be separated from local project facts."
argument-hint: "[research question, scope, depth, source constraints]"
arguments:
  required: []
  optional:
    - research_question
    - scope
    - depth
    - source_constraints
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
  - many sources or broad topic
  - conflicting evidence
  - current facts, regulation, pricing, security, medical, legal or financial claims
  - need for paid tools, login, scraping or personal-data collection
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-web-deep-research/SKILL.md"
shell: bash
type: skill
status: draft
used_by:
  - loki-deep-research
  - loki-tech-analysis
  - loki-human-decision-preflight
  - loki-implement-feature
---

# lf-web-deep-research

## Procedure

1. Confirm the research question, decision context, scope, out-of-scope items,
   depth, source constraints, output destination and risk level.
2. If local consumer state matters, inspect the smallest necessary local sources
   first. External sources explain the outside world; local files define the
   current project.
3. Build a research plan before searching:
   - 3-7 subquestions for ordinary deep research;
   - source classes to prefer, such as official docs, primary repositories,
     standards, papers, reports, product pages, public filings, reputable news
     or community discussions;
   - source classes to exclude or treat as low confidence;
   - freshness requirements and domains/geographies when relevant.
4. Build an `agent_research_plan` whenever depth is `deep` or `deeper`, and
   whenever ordinary research would force the main thread to read many long web
   pages. Split by subquestion, source class, entity, competitor, time period or
   contradiction probe. Each lane must be independent enough to run in parallel.
5. For broad or costly research, ask for approval or scope reduction before
   long-running, paid, login-based, scraping-heavy or multi-lane investigation.
6. Delegate research lanes to `source-researcher` agents when available. The
   main thread should pass only the lane envelope and receive only compact
   `source_research` handoffs; raw pages, long excerpts and noisy search results
   stay inside the agent context.
7. Search in waves:
   - broad discovery with several query variants;
   - targeted searches for primary sources and named entities;
   - deep reads of the most relevant sources;
   - verification searches for contradictions, criticism, recency and missing
     counterexamples.
8. Track methodology while working: queries, filters, domains, source URLs,
   source type, publication/update date when available, access date, why each
   important source was used or rejected.
9. Extract evidence into a source map. Keep each material claim linked to a
   source and classify it as fact, quoted claim, inference, assumption, gap or
   contradiction.
10. Assess source credibility by authority, proximity to primary evidence,
   recency, independence, transparency, conflict of interest and corroboration.
11. Preserve conflicts. When sources disagree, report the disagreement, likely
   cause, confidence level and what would resolve it.
12. Synthesize only what the evidence supports. Avoid implementation decisions
    unless the calling command asks for a recommendation; otherwise provide
    options, risks and next-step handoff.
13. Produce the output structure below and run the validators.

## Depth Modes

- `quick`: 3-5 sources, enough for orientation or low-risk decisions.
- `standard`: multiple query variants, primary sources where available,
  cross-checks and contradiction scan. Use agents when the source volume would
  bloat the main thread.
- `deep`: independent lanes by subquestion or source class, explicit source
  rejection notes, stronger conflict mapping and a fuller evidence table.
  Requires one `source-researcher` handoff per lane unless unavailable.
- `deeper`: use only with approval for costly, high-stakes or strategic work;
  split lanes, re-check recency, test counterclaims and produce a resume-ready
  handoff. Requires parallel `source-researcher` handoffs and compact
  consolidation.

## Agent Lane Envelope

For each lane, provide the agent only:

```yaml
agent_research_lane:
  lane_id: ""
  downstream_use: "deep-research"
  research_question: ""
  allowed_source_classes: []
  blocked_source_classes: []
  suggested_queries: []
  freshness_requirement: ""
  max_sources_to_return: 5
  max_evidence_words_per_source: 60
  required_output: "source_research"
```

Each agent returns compact `source_research`. The main thread keeps only:

- lane id and question;
- source URLs and source metadata;
- short evidence summaries;
- facts, inferences, assumptions, conflicts and gaps;
- confidence and recommended next step.

## Output Structure

```markdown
# Deep Research: <topic>

## Research Question

## Scope And Limits

## Methodology
- Queries:
- Filters/domains:
- Source classes:
- Date/access notes:
- Known limitations:

## Agent Research Plan
| Lane | Question | Agent | Scope | Status |
| --- | --- | --- | --- | --- |

## Executive Synthesis

## Key Findings

## Evidence Table
| Claim | Classification | Source | Date | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |

## Source Credibility

## Contradictions And Gaps

## Assumptions

## Risks And Implications

## Next-Step Handoff
```

## Validators

- The report states the research question, scope and limits.
- The methodology lists queries or search strategy, filters/domains and source
  classes.
- For `deep` and `deeper`, the report includes an agent research plan and
  compact `source_research` handoffs per lane, or explicitly stops.
- The main thread does not include raw long page content, noisy search dumps or
  large excerpts that should remain in agent context.
- Material claims cite sources or are labeled as inference, assumption, gap or
  contradiction.
- Source dates or access dates are present when recency matters.
- At least two independent sources support high-impact claims, or the report
  states why that standard could not be met.
- Primary sources are preferred when available.
- Contradictions are explicitly listed instead of collapsed into false
  certainty.
- Recommendations are proportional to evidence and name the next Loki command
  when implementation, planning, durable documentation or policy change is
  needed.
- No external source is allowed to override local consumer state.

## Limits

- Do not bypass paywalls, authentication, robots restrictions, rate limits,
  privacy boundaries or tool approvals.
- Do not collect personal data unless the calling workflow has explicit scope,
  legal basis and approval.
- Do not copy long source text into the report; summarize and cite.
- Do not treat search ranking, popularity, or a single vendor claim as proof.
- Do not apply code, runtime, package, documentation or installation changes
  from this skill.

## Source Patterns From References

This skill internalizes these reference patterns without depending on external
files at runtime:

- Search specialist: query variants, domain filters, full-page reads,
  credibility assessment and contradiction tracking.
- Multi-agent deep research: optional independent lanes for broad topics.
- Product/market research pipelines: clarify before research, record dates,
  flag assumptions and do not write planning artifacts until research is stable.
- Competitor research: choose depth, confirm expensive enrichment sets, use
  lanes and cite every claim.
- Academic research workflows: use specialized scholarly sources when the topic
  is literature-heavy.
- Corporate deep researcher agents: remain read-only, gather facts and gaps,
  cite sources, and avoid implementation decisions.
