---
title: Paralelismo em agentes Claude Code e Codex
date: 2026-06-26
status: pesquisa
sources:
  - https://code.claude.com/docs/en/sub-agents.md
  - https://code.claude.com/docs/en/agents.md
  - https://code.claude.com/docs/en/agent-teams.md
  - https://developers.openai.com/codex/subagents
  - https://developers.openai.com/codex/guides/agents-md.md
  - https://developers.openai.com/codex/skills
---

# Paralelismo em agentes Claude Code e Codex

## Pergunta

A instrucao de paralelismo deve ficar dentro do agente ou somente em quem chama o agente?

## Fontes consultadas

- Claude Code: [Subagents](https://code.claude.com/docs/en/sub-agents.md)
- Claude Code: [Agents](https://code.claude.com/docs/en/agents.md)
- Claude Code: [Agent teams](https://code.claude.com/docs/en/agent-teams.md)
- Codex: [Subagents](https://developers.openai.com/codex/subagents)
- Codex: [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md.md)
- Codex: [Skills](https://developers.openai.com/codex/skills)

## Achados

Claude Code trata subagents como assistentes especializados com contexto proprio. A delegacao acontece pela descricao do agente e pelo contexto do pedido. Isso torna importante que o agente declare claramente quando deve ser usado, quais entradas precisa, quais saidas deve devolver e se e seguro executar em paralelo.

As superficies de paralelismo do Claude Code tem custos diferentes. Subagents servem para side tasks em contexto separado e retornam um resumo ao fluxo principal. Agent teams sao experimentais e fazem mais sentido quando ha papeis independentes que precisam colaborar diretamente. Worktrees ajudam quando varias sessoes podem tocar arquivos diferentes e precisam evitar conflito de escrita.

Codex tambem documenta subagents como uma forma de executar trabalho paralelo e consolidar resultados no agente principal. A orquestracao fica no chamador: spawn, acompanhamento, espera e consolidacao. O agente customizado deve ter nome, descricao e instrucoes de desenvolvedor claras; a descricao e o contrato do agente ajudam o orquestrador a decidir quando delegar.

AGENTS.md no Codex e a superficie adequada para convencoes duraveis do workspace ou projeto. Skills sao mais adequadas para workflows reutilizaveis com carregamento progressivo e contrato de entrada/saida. Portanto, a politica geral de paralelismo deve viver no comando, skill ou documento de orquestracao que decide o fan-out.

## Decisao aplicada no Loki

A politica detalhada de paralelismo deve ficar em quem chama: comandos, skills e agentes-orquestradores. Esses chamadores sabem o objetivo, as dependencias, a ordem necessaria e se as tarefas podem rodar em paralelo sem colisao de contexto ou escrita.

Os agentes devem manter apenas um contrato curto de concorrencia:

- se sao seguros para execucao paralela;
- se sao read-only, write-capable ou dependem de estado externo;
- quais entradas precisam para nao reconsultar contexto desnecessariamente;
- qual formato de saida o chamador pode consolidar.

## Classificacao aplicada

Enfatizar forte:

- `execution-context-reader`: leitura independente de contexto e descoberta inicial, bom candidato para fan-out com outras leituras.
- `runtime-qa`: verificacao e QA podem rodar em paralelo com revisao documental ou analise de execucao quando nao houver escrita concorrente.
- `technical-implementer`: pode executar em paralelo somente quando o chamador particiona arquivos, tarefas e limites de escrita com clareza.

Enfatizar moderado:

- `bibliotecario`: util para consultas de indice e recuperacao documental em paralelo, mas normalmente como suporte ao chamador, nao como default agressivo.

Nao enfatizar como default:

- `standards-curator`: tende a consolidar padroes e decisoes; paralelismo pode fragmentar criterio.
- `catalogador`: catalogacao costuma depender de ordem, consistencia e consolidacao, entao o paralelismo deve ser excecao orientada pelo chamador.

## Implicacoes para autoria futura

Ao criar novos agentes Loki, evitar colocar politica ampla de fan-out dentro do corpo do agente. O agente deve explicar sua capacidade de concorrencia, mas a decisao de invocar muitos agentes em paralelo deve ficar no comando, skill ou agente-orquestrador.

Ao criar novos comandos ou skills Loki, declarar explicitamente quando vale paralelizar, quais agentes podem ser chamados juntos, quais dependencias exigem sequenciamento e como consolidar saidas divergentes.

## Alteracoes derivadas

- `docs/05-Loki-Framework/002-loki-framework-local/agents/execution-context-reader.md`
- `docs/05-Loki-Framework/002-loki-framework-local/agents/runtime-qa.md`
- `docs/05-Loki-Framework/002-loki-framework-local/agents/technical-implementer.md`
- `docs/05-Loki-Framework/002-loki-framework-local/agents/bibliotecario.md`
- `docs/05-Loki-Framework/002-loki-framework-local/commands/loki-run-plan.md`
- `docs/05-Loki-Framework/002-loki-framework-local/commands/loki-tech-analysis.md`
- `docs/05-Loki-Framework/002-loki-framework-local/commands/loki-feedback.md`
- `docs/05-Loki-Framework/002-loki-framework-local/commands/loki-continuous-improvement.md`
- `docs/05-Loki-Framework/002-loki-framework-local/skills/loki-run-plan-execution/SKILL.md`
