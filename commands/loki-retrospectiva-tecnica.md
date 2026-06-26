---
name: loki:retrospectiva-tecnica
type: command
status: draft
domain: continuous-improvement
required_skills:
  - loki-retrospectiva-tecnica
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - reusable learning may become durable policy
    - evidence is incomplete or conflicting
    - retrospective recommends package artifact changes
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: medium
    documentation_durable: high
    validator: low
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:retrospectiva-tecnica

## Purpose

Produzir retrospectiva tecnica objetiva como fonte auditavel de evidencia para outra LLM retomar contexto, entender decisoes e alimentar melhoria continua depois que uma fase, task ou dificuldade real tiver sido concluida ou resolvida de fato, sem transformar retrospectiva em regra duradoura por si so.

## Inputs

- Fase concluida ou pausada.
- Dificuldade relevante ja resolvida, quando o aprendizado depender do que efetivamente funcionou.
- Tasks, builds, interaction records e validacoes da fase.
- Riscos residuais e pendencias humanas.

## Outputs

- `retrospetivas/faseN/retrospectiva-faseN-<slug>.md`.
- Aprendizados reutilizaveis.
- Candidatos estruturados para `loki:continuous-improvement`, baseados apenas no que foi validado ou resolveu o problema de fato.

## Allowed Writes

- Retrospectiva do plano ativo.
- Pequenos resumos de status quando a task exigir.

## Forbidden Writes

- `AGENTS.md`
- `CLAUDE.md`
- Project-context duradouro do projeto consumidor.
- Promover standards, commands, skills, agents, templates, validators, docs consolidados ou `manifest.yaml` diretamente.
- Runtime, engine, framework ou superficies sensiveis do consumidor fora do escopo aprovado.
- `.claude/**` e `.agents/**`.

## Required Skills

- `loki-retrospectiva-tecnica`

## Handoffs

- `loki:continuous-improvement` quando a retrospectiva identificar aprendizado recorrente ou erro cuja correcao deva viver em superficie duradoura.
- `standards-curator` em modo `proposal-only` quando a classificacao do aprendizado estiver ambigua.

## Validators

- Cada aprendizado reutilizavel cita fonte concreta da fase.
- A retrospectiva separa fato observado, decisao humana, validacao, risco residual e hipotese.
- Quando houver erro ou atrito recorrente, capture tambem `expected behavior`, `actual behavior`, `context` e `suspected cause`.
- So promova como aprendizado reutilizavel o que foi validado ou resolveu o problema de fato; hipoteses, tentativas promissoras e correcoes parciais devem ficar explicitamente marcadas como nao validadas.
- Candidatos duradouros saem como proposta estruturada ou handoff, nunca como promocao aplicada.

## Human Gates

- `technical-review` se a retrospectiva recomendar mudanca duradoura em command, skill, agent, template, validator, doc ou `manifest.yaml`.
- `approval` para qualquer promocao posterior ou sincronizacao para `AGENTS.md`, `CLAUDE.md` ou contexto duradouro do consumidor.

## Packaging Checks

- Se a retrospectiva sugerir mudanca no pacote, registrar tipo de artefato afetado e encaminhar para `loki:continuous-improvement` com referencia a `docs/package-authoring-guardrails.md`.

## Learning Capture Format

Cada candidato de melhoria extraido da retrospectiva deve registrar, em texto ou YAML:

- `Mistake Description` ou aprendizado observado.
- `Expected Behavior`.
- `Actual Behavior`.
- `Context`.
- `Suspected Cause`.
- `Resolution Evidence`.
- Fonte da fase que sustenta a conclusao.

## Stop Conditions

- A fase nao tem resultado claro.
- A dificuldade ainda nao foi resolvida e a equipe ainda esta apenas testando hipoteses.
- Evidencias de validacao estao ausentes ou contraditorias.
- O texto mistura registro de evidencia com tentativa de promover regra diretamente.

## Resume Contract

A retrospectiva deve listar objetivo, artefatos criados, validacoes, decisoes humanas, aprendizados, riscos residuais, candidatos duradouros encaminhados e proximo passo.
