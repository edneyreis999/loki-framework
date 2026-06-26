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
  ! -path '*/skills/loki-skill-creator/references/validation-and-forward-testing.md' \
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
