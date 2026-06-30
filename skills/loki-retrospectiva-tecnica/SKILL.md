---
name: loki-retrospectiva-tecnica
description: Run the Loki `loki:retrospectiva-tecnica` command workflow in Codex. Produce a concise technical retrospective after a Loki phase is completed or clearly paused, or after a real task difficulty is actually resolved, capturing artifacts, validations, human decisions, execution frictions, useful and bad inferences, scripts, environment mismatches, pending gates, reusable learnings, and residual risks for future LLM runs and continuous improvement.
when_to_use:
  - "Use after a Loki phase is completed or clearly paused."
  - "Use after a real task difficulty is resolved and reusable evidence should be captured."
  - "Use when recording artifacts, validations, human decisions, execution frictions, pending gates, learnings, and residual risks."
  - "Use when a task consumed more tokens, tools, searches, scripts, or user corrections than it should have."
argument-hint: "[phase, tasks.md, builds, interactions, execution trace]"
arguments:
  required: []
  optional:
    - phase
    - tasks_md
    - builds
    - interactions
    - execution_trace
    - scripts_or_commands
    - target_retrospective
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
  - execution had repeated failed searches, bad inferences, unexpected script output, or environment mismatch
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

Use ao concluir ou pausar claramente uma fase, ou assim que uma dificuldade real for resolvida de fato, para registrar contexto tecnico reutilizavel por outra LLM. Use tambem quando a execucao terminou, mas custou mais tokens, ferramentas, buscas, scripts, validacoes ou interacoes do que deveria.

## Procedure

1. Declare objetivo, resultado entregue, criterio de conclusao, restricoes relevantes e `target_retrospective` quando o workflow chamador tiver fornecido um destino exato.
2. Liste artefatos criados, alterados, consultados ou descartados.
3. Registre validacoes feitas, nao feitas, bloqueadas, inconclusivas ou dependentes de gate humano.
4. Registre decisoes humanas, correcoes do usuario, mudancas de escopo e pendencias.
5. Reconstitua somente o rastro operacional material: ferramentas, comandos, scripts, buscas, leituras, tentativas falhas, tentativas uteis e sinais que corrigiram a rota.
6. Classifique atritos pela taxonomia abaixo, incluindo inferencias bem feitas e mal feitas.
7. Para cada script, comando ou validator relevante, registre objetivo, entrada, resultado observado, resultado esperado, surpresa, artefato gerado, utilidade real e reuso recomendado.
8. Para cada mismatch de ambiente, registre expectativa da LLM, estado real, como foi detectado, impacto e preflight que teria evitado o atrito.
9. Identifique desperdicios de contexto, ferramentas, buscas, scripts ou interacoes, com impacto qualitativo e acao concreta para evitar repeticao.
10. Escreva o caminho minimo recomendado para uma proxima LLM resolver tarefa equivalente com menos tentativas.
11. Extraia aprendizados reutilizaveis com fonte, separando validado, hipotese, falha operacional da LLM e preferencia humana.
12. Gere candidatos para `loki:continuous-improvement` apenas quando houver fonte, escopo, destino, verificacao e gate claro.
13. Marque riscos residuais e proximo passo.

## Execution Friction Taxonomy

Capture qualquer atrito material que explique custo extra, erro, correcao de rota
ou atalho util para a proxima execucao. Omita categorias sem ocorrencia
material. Nao invente atritos para preencher checklist.

- `inference-good`: inferencia correta que acelerou a execucao. Registre a
  evidencia usada, por que era confiavel e como repetir o lookup.
- `inference-bad`: inferencia incorreta, prematura ou confiante demais.
  Registre por que parecia plausivel, como falhou, qual evidencia corrigiu a
  rota e qual verificacao deveria vir primeiro.
- `file-discovery`: dificuldade para achar arquivo, simbolo, contrato, fonte de
  verdade, symlink, mirror instalado, generated artifact ou caminho canonico.
- `script-command`: Python, shell, validator, build, test, linter, formatter,
  parser ou snippet executado. Registre comando, cwd, objetivo, entrada,
  resultado, artefato produzido, custo e reuso.
- `unexpected-output`: script, teste, parser, validator ou ferramenta retornou
  resultado diferente do esperado, vazio, truncado, ruidoso ou contraditorio.
- `environment-mismatch`: versao, dependencia, PATH, shell, cwd, sandbox,
  permissao, rede, porta, cache, symlink, mirror, variavel de ambiente,
  package manager, runtime state ou estado persistido diferente do esperado.
- `tool-friction`: ferramenta indisponivel, lenta, com limite, sem permissao,
  com output insuficiente, exigindo fallback ou chamada redundante.
- `validation-friction`: validator ausente, tardio, flakey, caro, quebrado,
  inconclusivo ou dependente de validacao humana nao disponivel.
- `source-friction`: fonte local, doc, task, retro, build, interaction,
  manifest, template, comando ou skill estava ambigua, defasada, duplicada,
  fragmentada ou foi consultada tarde demais.
- `handoff-friction`: agente, skill, command, template ou doc carregado tarde,
  errado, duplicado, defasado ou com contrato incompleto.
- `state-friction`: worktree suja, mudanca concorrente do usuario, diff
  inesperado, arquivo gerado, cache, lockfile, build artifact ou estado
  persistido alterou a execucao.
- `dependency-friction`: pacote, API, plugin, engine, framework, schema,
  database, migration, data file ou generated type nao correspondia ao que a
  LLM esperava.
- `format-friction`: JSON/YAML/frontmatter/Markdown/schema/encoding/case
  sensitivity/line endings/locale/timezone causou tentativa extra ou erro.
- `external-research-friction`: pesquisa externa necessaria, evitavel,
  recusada, feita tarde ou feita ampla demais; registrar query minima futura.
- `user-correction`: correcao, redirecionamento, decisao, escopo novo ou
  esclarecimento humano que mudou a execucao.
- `communication-waste`: pergunta cuja resposta ja estava no contexto, resposta
  longa demais, plano maior que a tarefa, status pouco util ou explicacao nao
  solicitada.
- `search-waste`: busca ampla, leitura integral, leitura repetida, leitura de
  arquivo irrelevante ou falta de `rg`/lookup localizado primeiro.
- `scope-waste`: trabalho feito fora da task ativa, refactor cosmetico,
  artefato intermediario inutilizado ou investigacao maior que o risco exigia.
- `safety-gate-friction`: approval, technical-review, human-validation,
  research-consent ou human loop ausente, ambiguo ou descoberto tarde.
- `minimum-next-path`: sequencia menor que uma proxima LLM deveria seguir para
  chegar ao mesmo resultado com menos tentativas.

## Friction Record Format

Para cada atrito material, registre:

- `Category`.
- `What Happened`.
- `Expected Behavior`.
- `Actual Behavior`.
- `Context`.
- `Evidence`.
- `Cause`: confirmada, provavel ou desconhecida.
- `Resolution Or Outcome`.
- `Was Useful`: sim, nao ou parcialmente.
- `Waste Impact`: `low`, `medium` ou `high`, sem inventar numero de tokens.
- `Reuse Guidance`.
- `Avoid Next Time`.
- `Minimum Next Step`.

## Inputs

- Task files.
- Builds.
- Interaction records.
- Validations.
- Execution trace material: tool calls, comandos, scripts, buscas, leituras, erros, outputs inesperados, correcoes de rota e intervencoes humanas.
- Resultado final da fase ou evidencia do problema resolvido.

## Outputs

- Retrospectiva Markdown em `retrospetivas/faseN/`, ou no `target_retrospective` exato quando o workflow chamador tiver fornecido um destino por agente.
- Mapa de atritos de execucao com impacto e caminho minimo recomendado.
- Candidatos para melhoria continua baseados apenas no que foi validado ou resolveu o problema de fato.

## Limits

- Retrospectiva nao e standard.
- Aprendizado nao vira regra sem approval.
- Nao deve incluir conversa bruta, cadeia de pensamento ou narrativa cronologica extensa quando um resumo aprovado basta.
- Nao trate sucesso final como prova de eficiencia.
- Nao invente erros, causas, metricas, outputs ou atritos.
- Nao oculte inferencias corretas que seriam atalhos uteis para uma proxima execucao.
- Nao deve promover como aprendizado duradouro hipoteses, tentativas promissoras ou correcoes parciais nao validadas.

## Required Gates

- `technical-review` ou `approval` se a retrospectiva propuser mudanca duradoura.
