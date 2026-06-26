# Loki Technical Analysis Contract

Use this contract when authoring or reviewing a Loki technical analysis.

## Inputs

Minimum safe inputs:

- brief, PRD, NSD, feedback, direct request or approved objective;
- explicit source paths or a documented reason to discover them;
- in-scope and out-of-scope surfaces;
- forbidden writes and sensitive consumer surfaces;
- known human decisions, assumptions and unresolved questions.

If the available input is not enough to produce a grounded analysis, stop and
ask for the missing source or decision.

## Evidence Model

Classify every important statement:

- **Fact:** confirmed by a local source, user decision or cited external source.
- **Inference:** reasoned conclusion from listed facts.
- **Hypothesis:** plausible explanation that still needs targeted verification.
- **Open question:** decision or source gap that needs human input.

Do not promote a hypothesis to a recommendation until a targeted read/search
confirms it. If confirmation is not possible, keep it as risk, question or stop
condition.

## Analysis Pass

1. Identify the consumer project root and read applicable routing instructions.
2. Build a source map from local primary sources before interpretive docs.
3. Confirm affected runtime surfaces, integration points, state contracts, IDs,
   schemas, generated artifacts or documentation surfaces.
4. Run targeted local checks for material hypotheses.
5. Apply the research gate only after local context is known.
6. Compare alternatives with explicit tradeoffs.
7. Define validators and human gates before recommending execution.
8. Produce a handoff that can feed `loki:generate-action-plan`.

Convergence means the recommendation, risks, validators, human gates and next
action are grounded in sources another agent can inspect.

## Research Gate

External research is conditional. Run it when one or more are true:

- the user explicitly asks for internet or current external context;
- the analysis depends on current library, framework, engine, API, plugin,
  security, licensing or compatibility information;
- local source explains the current state but not the upstream contract;
- a technology-specific skill requires current official documentation.

Placement:

1. First map local sources and affected surfaces.
2. Then form precise external questions.
3. Prefer official documentation, primary source repositories, release notes or
   a current documentation provider available in the environment.
4. Record the source URL or provider, what fact it supports, and any version or
   date constraint.

Do not use external research to override local consumer facts. If external docs
conflict with local runtime state, record the conflict and recommend a validator
or human decision.

## Required Output Fields

The analysis must include:

- title, status, creation date and source request;
- objective and expected downstream use;
- scope and out of scope;
- sources read, with kind and evidence extracted;
- facts, inferences, hypotheses and open questions;
- affected runtime surfaces and integration points;
- state, data, schema, ID or persistence contracts when relevant;
- research gate result: not needed, skipped with reason, or performed with
  cited sources and findings;
- decision matrix comparing viable approaches;
- recommendation and rationale;
- risks and mitigations;
- validators;
- human gates;
- affected docs;
- stop conditions;
- handoff to `loki:generate-action-plan`;
- resume state.

## Reference Rules

Use references that another agent can inspect:

- document path plus heading, section, line or anchor when available;
- source file path;
- command, API, schema, event, plugin, framework or integration name;
- approved user decision recorded in an interaction artifact;
- cited external URL, provider or package documentation identifier.

Never invent line numbers, file names, APIs, variables, IDs, versions or
approvals. If a reference matters but is not located, write `TODO: localizar`
and make the gap visible in risks or stop conditions.

## Validators

Before declaring the analysis ready, check:

- every recommendation has a source, inference chain or explicit assumption;
- unresolved hypotheses are labeled and not used as facts;
- affected surfaces and forbidden writes are declared;
- validators and human gates match the affected surfaces;
- research was either performed with cited sources or skipped with a reason;
- external sources do not replace local consumer evidence;
- the handoff is specific enough for `loki:generate-action-plan`;
- the artifact can be resumed without chat memory.

## Stop Conditions

Stop before recommending execution if:

- the source request is not verifiable;
- local primary sources required for safety are missing;
- a material decision belongs to the user;
- research reveals a blocker without a safe alternative;
- the requested next step would require unauthorized writes;
- validators or human gates cannot be defined for the affected surfaces.
