---
name: loki-retrospectiva-tecnica
description: Run the Loki `loki:retrospectiva-tecnica` command workflow in Codex. Produce a concise technical retrospective after a Loki phase is completed or clearly paused, or after a real task difficulty is actually resolved, capturing artifacts, validations, human decisions, pending gates, reusable learnings, and residual risks for future LLM runs and continuous improvement.
when_to_use:
  - "Use after a Loki phase is completed or clearly paused."
  - "Use after a real task difficulty is resolved and reusable evidence should be captured."
  - "Use when recording artifacts, validations, human decisions, pending gates, learnings, and residual risks."
argument-hint: "[phase, tasks.md, builds, interactions]"
arguments:
  required: []
  optional:
    - phase
    - tasks_md
    - builds
    - interactions
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - reusable learning may become durable policy
  - evidence is incomplete or conflicting
  - retrospective recommends package artifact changes
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-retrospectiva-tecnica/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:retrospectiva-tecnica
  - loki:continuous-improvement
---

# loki-retrospectiva-tecnica

## When To Use

Use ao concluir ou pausar claramente uma fase, ou assim que uma dificuldade real for resolvida de fato, para registrar contexto tecnico reutilizavel por outra LLM.

## Procedure

1. Declare objetivo da fase.
2. Liste artefatos criados ou alterados.
3. Registre validacoes feitas e nao feitas.
4. Registre decisoes humanas e pendencias.
5. Extraia aprendizados reutilizaveis com fonte, separando o que foi validado do que permaneceu hipotese.
6. Registre qual evidencia mostra o que realmente resolveu o problema.
7. Marque riscos residuais.

## Inputs

- Task files.
- Builds.
- Interaction records.
- Validations.
- Resultado final da fase ou evidencia do problema resolvido.

## Outputs

- Retrospectiva Markdown em `retrospetivas/faseN/`.
- Candidatos para melhoria continua baseados apenas no que foi validado ou resolveu o problema de fato.

## Limits

- Retrospectiva nao e standard.
- Aprendizado nao vira regra sem approval.
- Nao deve incluir conversa bruta quando um resumo aprovado basta.
- Nao deve promover como aprendizado duradouro hipoteses, tentativas promissoras ou correcoes parciais nao validadas.

## Required Gates

- `technical-review` ou `approval` se a retrospectiva propuser mudanca duradoura.
