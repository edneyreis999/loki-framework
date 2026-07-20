# Validation and Forward Testing

Use this reference when validating a skill folder or testing whether a complex skill works in practice.

## Basic Validation

Check every skill directory has:

- `SKILL.md`;
- YAML frontmatter;
- top-level `name`;
- top-level `description`;
- folder name matching the skill name unless there is a documented reason.

Validate package metadata points to existing files.

For this package, a lightweight validation can check:

```bash
find "$PACKAGE_ROOT"/skills -maxdepth 2 -name SKILL.md | sort
find "$PACKAGE_ROOT"/skills -maxdepth 1 -type f -name '*.md'
find "$PACKAGE_ROOT" -type f \
  ! -path '*/docs/package-authoring-guardrails.md' \
  ! -path '*/skills/lf-skill-creator/references/validation-and-forward-testing.md' \
  -print0 | xargs -0 rg -n "(Jhonny/|docs/05-Loki-Framework/001-blueprint-aprovado|/Users/|~/|source_plan|canonical_blueprint|operational_plan|historical_reference)"
```

The second command should return nothing. The `rg` command should also return nothing for packaged normative content.

Also verify:

- `manifest.yaml` paths exist;
- every packaged skill name matches its folder name;
- `description` carries the trigger context instead of relying only on `When To Use`;
- long conditional detail was moved to `references/` when appropriate.

## Script Validation

If the skill includes `scripts/`, run the scripts or a representative sample. Record what was tested and what was skipped.

## Forward Testing

Forward-test when the skill is complex, high-risk, or likely to be reused.

Use a clean prompt shape:

```text
Use $skill-name at /path/to/skill-name to solve <realistic task>.
```

Do not tell the evaluator the expected answer, suspected bug, or intended fix unless the task requires it.

Review:

- whether the skill triggered correctly;
- whether references were loaded only when needed;
- whether the output matched the skill contract;
- whether the agent needed hidden context to succeed.

If forward testing only succeeds with leaked context, tighten the skill or split references differently.

## Conditional LLM-Facing Quality Gate

Before delivery, classify the created or revised skill with
[lf-documentation-writing](../../lf-documentation-writing/SKILL.md). When the
classification is positively LLM-facing, require a complete
`llm_artifact_profile`, application of the
[canonical LLM artifact quality contract](../../lf-documentation-writing/references/llm-artifact-quality-validation.md),
and an independent `llm_consumption_quality` result in which every applicable
fixture passes. Do not copy the canonical rubric, schemas, or fixture
definitions into this creator contract.

Use these terminal semantics:

- positive LLM-facing classification without the complete profile, canonical
  contract, independent result, or with any non-passing applicable fixture:
  mark checklist item 15 `não` and block delivery;
- positive LLM-facing classification with the complete profile and independent
  result approved: item 15 may be `sim`, and completion remains subject to all
  other checklist items and existing gates;
- exclusively human-facing: record `not-applicable` with a concrete human-only
  reason and do not run irrelevant fixtures.

## Canonical 24/24 checklist

Before delivery, record `sim|não`, file and heading for every item. Any `não`
blocks delivery: (1) reusable specialized role; (2) one capability with scope
and non-scope; (3) no full workflow orchestration; (4) installable layout;
(5) YAML name/description; (6) folder/name/namespace; (7) trigger description;
(8) observable use/exclusions; (9) coherent multi-adapter metadata; (10)
objective purpose; (11) required/optional inputs and missing-input handling;
(12) imperative procedure; (13) outputs plus success/failure/partial states;
(14) limits/prohibitions/stops; (15) validators/evidence/gates, including the
conditional LLM-facing gate above when applicable; (16) degree of
freedom proportional to risk; (17) focused SKILL.md; (18) conditional detail in
references; (19) conditional reference routing; (20) deterministic scripts
tested; (21) assets only as output resources; (22) no contradiction/duplication;
(23) package self-containment; (24) structural validation and clean-context
forward test when complex/high-risk.

### Correction 16 — calibrate freedom

Choose explicit scripts or low-freedom steps for fragile, repetitive or
high-risk operations; use parameterized templates for medium-risk work and
heuristics only where judgment safely admits alternatives. This correction must
be present whenever item 16 is claimed as `sim`.
