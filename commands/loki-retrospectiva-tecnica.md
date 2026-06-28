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

Produzir retrospectiva tecnica objetiva como fonte auditavel de evidencia para outra LLM retomar contexto, entender decisoes, capturar atritos observaveis de execucao e alimentar melhoria continua depois que uma fase, task ou dificuldade real tiver sido concluida ou resolvida de fato, sem transformar retrospectiva em regra duradoura por si so.

## Inputs

- Fase concluida ou pausada.
- Dificuldade relevante ja resolvida, quando o aprendizado depender do que efetivamente funcionou.
- Tasks, builds, interaction records e validacoes da fase.
- Rastro operacional relevante: ferramentas, comandos, scripts, buscas, leituras, tentativas falhas, tentativas uteis, inferencias e correcoes de rota.
- Riscos residuais e pendencias humanas.

## Outputs

- `retrospetivas/faseN/retrospectiva-faseN-<slug>.md`.
- Aprendizados reutilizaveis.
- Atritos de execucao estruturados para reduzir custo de tokens, ferramentas, buscas e interacoes futuras.
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
- `.claude/**`, `.agents/**` e `.codex/**`.

## Required Skills

- `loki-retrospectiva-tecnica`

## Handoffs

- `loki:continuous-improvement` quando a retrospectiva identificar aprendizado recorrente ou erro cuja correcao deva viver em superficie duradoura.
- `standards-curator` em modo `proposal-only` quando a classificacao do aprendizado estiver ambigua.

## Validators

- Cada aprendizado reutilizavel cita fonte concreta da fase.
- A retrospectiva separa fato observado, inferencia, decisao humana, validacao, risco residual, hipotese, atrito operacional e desperdicio.
- Quando houver erro, acerto relevante ou atrito recorrente, capture tambem `expected behavior`, `actual behavior`, `context`, `suspected cause` e `reuse guidance`.
- Scripts Python, shell commands, validadores e ferramentas usados para chegar ao resultado devem registrar objetivo, entrada, resultado observado, se contribuiu, se surpreendeu a LLM e como reutilizar ou evitar.
- Inferencias corretas e incorretas devem registrar evidencia inicial, lacuna, resultado, correcao de rota e lookup minimo recomendado.
- Mismatches de ambiente devem registrar expectativa da LLM, estado real, como foi detectado, impacto e preflight que teria evitado o atrito.
- Desperdicios materiais devem registrar causa provavel, impacto qualitativo e acao concreta para reduzir tokens, ferramentas, buscas ou interacoes futuras.
- So promova como aprendizado reutilizavel o que foi validado ou resolveu o problema de fato; hipoteses, tentativas promissoras e correcoes parciais devem ficar explicitamente marcadas como nao validadas.
- Candidatos duradouros saem como proposta estruturada ou handoff, nunca como promocao aplicada.

## Human Gates

- `technical-review` se a retrospectiva recomendar mudanca duradoura em command, skill, agent, template, validator, doc ou `manifest.yaml`.
- `approval` para qualquer promocao posterior ou sincronizacao para `AGENTS.md`, `CLAUDE.md` ou contexto duradouro do consumidor.

## Packaging Checks

- Se a retrospectiva sugerir mudanca no pacote, registrar tipo de artefato afetado e encaminhar para `loki:continuous-improvement` com referencia a `docs/package-authoring-guardrails.md`.

## Execution Friction Capture

A retrospectiva deve capturar atritos materiais de execucao sem recontar toda a conversa e sem expor raciocinio interno detalhado. Registre apenas fatos observaveis, decisoes, justificativas resumidas, evidencias, erros, desperdicios e instrucoes reutilizaveis.

Capture, quando aplicavel:

- `inference-good`: inferencia que acelerou a execucao; registrar evidencia usada e como repetir.
- `inference-bad`: inferencia incorreta ou prematura; registrar por que parecia plausivel, como falhou e qual verificacao teria evitado.
- `file-discovery`: dificuldade para achar arquivo, simbolo, contrato, mirror, symlink, fonte de verdade ou generated artifact.
- `script-command`: Python, shell, validator, build, test, linter, formatter, parser ou snippet usado; registrar comando, objetivo, resultado, surpresa, artefatos gerados e reuso.
- `unexpected-output`: script, teste ou ferramenta que retornou resultado diferente do esperado.
- `environment-mismatch`: versao, dependencia, PATH, shell, cwd, sandbox, permissao, rede, porta, cache, symlink, mirror instalado, variavel de ambiente, runtime state ou package manager diferente do esperado.
- `tool-friction`: ferramenta indisponivel, lenta, truncada, ruidosa, sem permissao, com output ambiguo ou que exigiu fallback.
- `validation-friction`: validator ausente, tardio, inconclusivo, quebrado, caro, flakey ou dependente de validacao humana.
- `user-correction`: correcao, redirecionamento, decisao, escopo novo ou esclarecimento que mudou a execucao.
- `handoff-friction`: agente, skill, command, template ou doc carregado tarde, errado, duplicado, defasado ou com contrato incompleto.
- `state-friction`: worktree suja, mudanca concorrente do usuario, arquivo gerado, diff inesperado, conflito de fonte ou estado persistido nao previsto.
- `search-waste`: busca ampla, leitura integral, leitura repetida, pesquisa externa evitavel ou fonte consultada tarde demais.
- `communication-waste`: pergunta que ja tinha resposta no contexto, resposta longa demais, plano maior que a tarefa ou status que nao ajudou.
- `minimum-next-path`: sequencia menor que uma proxima LLM deveria seguir para chegar ao mesmo resultado com menos tentativas.

Quando nada relevante existir para uma categoria, omita a categoria ou registre `not applicable`. Nao invente atritos para preencher checklist.

## Learning Capture Format

Cada candidato de melhoria extraido da retrospectiva deve registrar, em texto ou YAML:

- `Mistake Description` ou aprendizado observado.
- `Expected Behavior`.
- `Actual Behavior`.
- `Context`.
- `Suspected Cause`.
- `Resolution Evidence`.
- `Execution Friction Category`.
- `Minimum Next Path`.
- `Reuse Guidance`.
- `Avoid Next Time`.
- `Estimated Waste Impact`: `low`, `medium` ou `high`, sem inventar numero de tokens.
- Fonte da fase que sustenta a conclusao.

## Stop Conditions

- A fase nao tem resultado claro.
- A dificuldade ainda nao foi resolvida e a equipe ainda esta apenas testando hipoteses.
- Evidencias de validacao estao ausentes ou contraditorias.
- O texto mistura registro de evidencia com tentativa de promover regra diretamente.

## Resume Contract

A retrospectiva deve listar objetivo, resultado, artefatos criados, validacoes, decisoes humanas, rastro operacional relevante, scripts/comandos executados, inferencias uteis e incorretas, atritos de ambiente, resultados inesperados, desperdicios, caminho minimo recomendado, aprendizados, riscos residuais, candidatos duradouros encaminhados e proximo passo.
