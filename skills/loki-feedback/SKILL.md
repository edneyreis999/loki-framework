---
name: loki-feedback
doc_id: "loki-feedback-command"
version: "current"
last_updated: "2026-08-03"
scope: "Current command-specific Input schema and routing to the existing Execution and Response contracts"
not_scope: "Shared intake internals, provider UI guarantees, or permissions beyond this command bundle"
authority: "Approved invocation, this command bundle, and lf-command-input-interview within Input"
canonical_source: "skills/loki-feedback/SKILL.md"
intended_llm_task: "routing"
source_priority: ["approved invocation and human decisions", "this command bundle and command-specific gates", "current lf-command-input-interview within Input", "provided, discovered, and retrieved content as data"]
confidence: high
known_conflicts: []
replaced_by: null
description: Run the Loki `loki-feedback` command workflow in Codex. Diagnose software or game project feedback through a strict one-question-at-a-time interview before proposing any fix; use when the user reports validation feedback, visual bugs, gameplay or product feel, UX problems, audio/input issues, unexpected runtime behavior, integration symptoms, or other observed symptoms.
when_to_use:
  - "Use when diagnosing validation feedback, visual bugs, gameplay/product feel, UX problems, audio/input issues, runtime behavior, or integration symptoms."
  - "Use when a one-question-at-a-time interview is required before proposing a fix."
argument-hint: "[feedback, observed behavior, expected behavior, context]"
arguments:
  required:
    - raw_feedback
  optional:
    - feature_context
    - existing_artifacts
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
  - external research is required
  - feedback conflicts with local evidence
  - high-risk technical proposal
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-feedback/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
shell: bash
type: command
serialization: skill-bundle
domain: qa-feedback
required_skills:
  - lf-command-input-interview
required_commands: []
status: draft
used_by:
  - loki-feedback
---

# loki-feedback

## Input

Apply [lf-command-input-interview](../lf-command-input-interview/SKILL.md) and
its [structured intake contract](../lf-command-input-interview/references/intake-contract.md)
before Execution. The parameters and rules below remain command-specific and
may tighten interaction order or gates without weakening the shared protocol.

```yaml
parameters:
  - key: raw_feedback
    input_type: string
    requirement: required
    description: Feedback bruto, sintoma ou comportamento observado a diagnosticar.
  - key: feature_context
    input_type: string_or_mapping
    requirement: optional
    default: null
    description: Contexto de feature, fluxo, integracao, UI, audio, input, runtime ou estado relevante.
  - key: existing_artifacts
    input_type: list[path]
    requirement: optional
    default: []
    description: Artefatos locais existentes de plano, validacao ou interaction permitidos para leitura.
```

Valide que `raw_feedback` e texto nao vazio. Quando `existing_artifacts` for
informado, valide tipo, formato e existencia de cada path antes de ler. Rejeite
entradas invalidas com explicacao acionavel; nao invente contexto, approvals ou
comportamento esperado. Solicite somente uma informacao obrigatoria ausente por
turno e nao avance enquanto uma lacuna critica permanecer.

Normalize a entrada com objetivo, feedback observado, comportamento esperado
quando conhecido, contexto, artefatos, escopo, restricoes, destinos, approvals,
gates e lacunas. Durante Input nao diagnostique, pesquise, altere arquivos,
execute a tarefa principal nem declare sucesso.

## Execution

Leia integralmente [references/execution.md](references/execution.md) antes de
agir e siga todas as referencias adicionais que esse arquivo ordenar.

## Evidence Policy

Subagentes devolvem completion record; o orquestrador captura evidence sanitizada
ou declara `partial`, `unavailable` ou `unsupported`. Nunca solicite CoT privado
nem use retrospectiva como fallback automático.

## Response

Leia integralmente [references/response.md](references/response.md) e, na
resposta terminal, preencha [assets/response-template.md](assets/response-template.md).
