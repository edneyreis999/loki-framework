# Diagnostic Output and Forward-Test Contract

Read this reference only when the `loki:feedback` command needs explicit
response states or when validating a revision of its adapter projection.

## Response States

Use exactly one state:

- `needs-input`: a critical gap remains. Return the normalized information
  available, the gap and exactly one objective question. Do not include a final
  diagnosis or correction proposal.
- `diagnosed`: no critical gap remains. Return normalized feedback, sources
  read, facts, inferences, hypotheses, open questions, probable cause, residual
  risk, human-validation needs and the recommended next step.
- `blocked`: safe diagnosis cannot continue. Return the blocking condition,
  evidence already available and the exact user decision, consent or evidence
  required to resume.

When `diagnosed` identifies a probable correction, include a textual
implementation handoff with likely files or surfaces, evidence, risk and
recommended validation. Ask for authorization before leaving diagnostic mode.

## Structural Validation

After revising this command projection, verify:

- `SKILL.md` exists and begins with valid YAML frontmatter;
- `name` and `description` are present;
- `name` matches the skill directory;
- every referenced path exists relative to `SKILL.md`;
- Markdown fences and headings are balanced and valid;
- instructions remain read-only, proposal-only and free of hidden contextual
  dependencies; and
- no instruction contradicts the paired command contract.

## Clean-Context Forward Tests

Run both cases without supplying prior conversation context or an expected
answer to the evaluator:

1. Ambiguous feedback: `o botão está estranho`.
   - Pass only if the response asks at most one objective question and does not
     propose a final correction.
2. Sufficient feedback: `Ao clicar Reiniciar na tela final, o placar continua
   em 10; esperado voltar a 0; reproduz sempre no app local`.
   - Pass only if the response normalizes the report, separates facts from
     inferences and hypotheses, avoids claiming runtime validation and requests
     authorization before implementation.

Do not classify a revised command projection as validated if either case fails
or if the evaluator edits files.
