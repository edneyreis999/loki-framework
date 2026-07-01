# External Knowledge Extraction Contract

Use this reference when extracting knowledge from external artifacts before
auditing Loki impact.

## Objective

Extract useful knowledge from analyzed artifacts that may improve Loki. Useful
knowledge can come from explicit rules, recurring patterns, skill or command
structure, output formats, better ambiguity handling, validation criteria,
rejection criteria, design principles, positive examples worth adapting, or
negative examples Loki should avoid.

Extraction must never be forced. If an artifact brings no useful learning for
Loki, state that clearly and explain why.

## Non-Forcing Criteria

Present a suggestion only when all criteria are true:

- It solves a real problem or reduces practical ambiguity.
- It is compatible, adaptable, or consciously rejectable relative to Loki.
- It can produce a concrete change in a skill, command, rule, document, template,
  validator, or test.
- It has traceable origin in the analyzed artifact.
- It does not duplicate Loki unless the recommendation improves clarity,
  structure, or prompt economy.

When these criteria are not met, classify the point as `ja contemplado`,
`incompativel`, `irrelevante`, `especifico demais`, `sem evidencia suficiente`,
or `nao aplicavel ao Loki`.

## Input Sources

Consider external frameworks, commands, skills, instruction documents,
operational rules, examples, prompt artifacts, documentation, and observable
differences between the external material and provided Loki context.

Do not assume Loki knowledge beyond supplied context. If Loki context is
incomplete, distinguish observed facts, inferences, and points requiring later
validation.

## What To Look For

Search for learnings in these categories when they exist:

- Instruction clarity: direct wording, binary criteria, reduced ambiguity, and
  precise use of must, must not, prefer, avoid, and only if.
- Prompt economy: fewer words without precision loss, redundancy removal, and
  long instructions replaced by verifiable rules.
- Loki essence preservation: ideas to adapt, incompatible behavior to reject,
  and protection against excessive autonomy, excessive rigidity, or misaligned
  patterns.
- Knowledge transfer: turning a specific instruction into a general principle
  or adapting a general rule into a specialized skill.
- Taxonomy and organization: objective, triggers, preconditions, constraints,
  process, expected output, common failures, conclusion criteria, and when not
  to use.
- Potential Loki gaps, redundancies, output formats, rejection criteria,
  conflicts, recommendation granularity, positive and negative examples,
  traceability, uncertainty handling, prioritization, noise prevention,
  principle extraction, validation tests, delta thinking, and recurring
  patterns.

Do not treat recurrence as sufficient proof of quality.

## Extraction Process

1. Map analyzed artifacts and their type: skill, command, framework,
   documentation, example, rule, prompt, or other.
2. Extract relevant observations only when they could affect Loki.
3. Ignore details too specific to the source context unless they reveal a
   transferable principle.
4. Classify each candidate as `adotar`, `adaptar`, `rejeitar`,
   `ja contemplado`, `investigar`, or `sem aprendizado util`.
5. Evaluate compatibility, conflict risk, implementation cost, expected gain,
   and priority at a candidate level, without choosing a Loki destination yet.
6. Explain rejections clearly.

## Required Handoff Shape

Return:

```yaml
external_extraction:
  external_artifacts:
    - id: ""
      type: ""
      apparent_purpose: ""
      relevance_to_loki: ""
      context_limitations: []
  observations:
    - source_artifact: ""
      source_kind: "explicit_rule | recurring_pattern | artifact_structure | positive_example | negative_example | inference"
      observation: ""
      interpretation_for_loki: ""
      category: ""
      evidence_strength: "high | medium | low"
  candidate_learnings:
    - title: ""
      classification: "adotar | adaptar | rejeitar | ja contemplado | investigar | sem aprendizado util"
      category: ""
      origin: ""
      observation: ""
      interpretation: ""
      practical_problem: ""
      compatibility_notes: ""
      rejection_criteria_considered: []
      risk: ""
      priority: "obrigatoria | recomendada | experimental | baixa | rejeitada"
      cost: "baixo | medio | alto"
      expected_gain: "baixo | medio | alto"
      validation_idea: ""
  no_useful_learning:
    conclusion: false
    reason: ""
```
