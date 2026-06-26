---
title: Workflow de Aprendizado do Loki
type: learning-workflow
status: draft
created: 2026-06-25
self_contained: true
---

# Workflow de Aprendizado do Loki

Este e o guia humano canonico para entender como o Loki aprende depois de uma
execucao, validacao, erro, feedback ou decisao. Ele explica quando um achado
vira apenas ajuste da task atual, quando vira retrospectiva e quando pode virar
regra duradoura.

![[loki-learning-workflow.excalidraw.md]]

## Ideia central

O Loki nao aprende por memoria magica da conversa. Ele aprende por evidencia: uma fonte concreta, um escopo claro, um destino certo, uma verificacao possivel e uma decisao registrada.

Tasks, builds, interactions e validacoes sao fontes transitorias. Elas ajudam a entender o que aconteceu, mas nao sao o lugar final de uma regra duradoura.

O fluxo normalmente comeca depois do
[Workflow de Execucao de Plano do Loki](loki-plan-execution-workflow.md), mas
tambem pode ser acionado por feedback humano, bug, playtest, validacao manual ou
descoberta tecnica fora de uma fase formal.

## Fluxo

1. Um sinal aparece: feedback humano, bug, dificuldade tecnica, decisao de produto, build, validacao ou repeticao de erro.
2. Se a fase ainda esta em execucao, use `loki:enrich-tasks` apenas para melhorar o plano atual. O aprendizado fica local: `tasks.md`, `task-N.M.md` ou `interaction/faseN/`.
3. Primeiro resolva o problema de fato. Nao transforme tentativa promissora em regra.
4. Quando a fase terminar, pausar claramente, ou a dificuldade real for resolvida, use `loki:retrospectiva-tecnica`.
5. A retrospectiva registra objetivo, artefatos, validacoes, decisoes humanas, evidencia do que resolveu, riscos e candidatos de melhoria.
6. So depois use `loki:continuous-improvement` para avaliar se algum candidato merece virar contexto duradouro. Quando houver um diretorio ou multiplas retrospectivas, use `retrospective-digester` em modo read-only para digerir cada arquivo antes da consolidacao.
7. O candidato e classificado por escopo: `universal`, `probable-universal`, `project-specific` ou `backlog`.
8. O destino e escolhido pela superficie que teria evitado a repeticao do problema.
9. Mudancas duradouras passam por gates: normalmente `technical-review`; e `approval` quando houver promocao normativa, instalacao, sincronizacao ou escrita sensivel.
10. A promocao termina com diff, validacao e registro do risco residual.

## Artefatos participantes

### Commands

| Command | Contribuicao no workflow |
| --- | --- |
| `loki:enrich-tasks` | Usa aprendizado transitorio para melhorar a fase atual, sem promover regra duradoura. |
| `loki:retrospectiva-tecnica` | Registra evidencia auditavel depois de fase concluida, pausa clara ou dificuldade resolvida de fato. |
| `loki:continuous-improvement` | Classifica candidatos, escolhe destino duradouro, exige gates e prepara ou aplica patch aprovado. |

### Skills

| Skill | Contribuicao no workflow |
| --- | --- |
| `loki-enrich-tasks` | Preserva o limite entre ajuste local da task e promocao normativa futura. |
| `loki-retrospectiva-tecnica` | Estrutura fonte, objetivo, decisao, validacao, risco residual e candidatos de melhoria. |
| `loki-command-creator` | Ajuda quando o aprendizado deve virar ou alterar um command com estado, gates e outputs. |
| `loki-agent-creator` | Ajuda quando o aprendizado pede um papel especialista com julgamento proprio. |
| `loki-skill-creator` | Ajuda quando o aprendizado deve virar procedimento reutilizavel com trigger e progressive disclosure. |

### Agents

| Agent | Contribuicao no workflow |
| --- | --- |
| `standards-curator` | Classifica escopo como `universal`, `probable-universal`, `project-specific` ou `backlog`. |
| `retrospective-digester` | Digerir uma retrospectiva ou lote pequeno em paralelo read-only, extraindo aprendizados, atritos, candidatos e evidencias para o orquestrador. |
| `source-researcher` | Confere evidencia, duplicidade, lacunas e conflitos multi-fonte antes de promocao duradoura. |
| `catalogador` | Promove aprendizado `project-specific` para `/docs` do consumidor e atualiza `docs/index.xml`. |
| `bibliotecario` | Localiza contexto duradouro existente antes de criar duplicidade. |
| `runtime-qa` | Fornece evidencia de validacao humana ou checklist quando o aprendizado depende de comportamento perceptivel. |

## Destinos corretos

Use esta regra simples:

| Aprendizado | Destino duradouro |
| --- | --- |
| Regra de negocio, lore, fluxo funcional ou termo do projeto consumidor | `docs/**/*.md` do consumidor + `docs/index.xml` |
| Regra project-wide para toda LLM do consumidor | `AGENTS.md` com roteamento minimo |
| Regra especifica de Claude Code, Codex ou adaptador | `CLAUDE.md` ou equivalente |
| Procedimento tecnico reutilizavel | `skills/` |
| Workflow invocavel com estado, outputs e gates | `commands/` |
| Papel especialista com julgamento proprio | `agents/` |
| Formato repetivel | `templates/` |
| Evidencia insuficiente ou caso isolado | backlog |

## O que nao fazer

- Nao promover aprendizado enquanto o problema ainda esta sendo testado.
- Nao usar retrospectiva como regra final. Ela e fonte auditavel.
- Nao guardar regra de negocio do consumidor no pacote Loki.
- Nao duplicar regra longa em `AGENTS.md` ou `CLAUDE.md`; esses arquivos devem rotear para a fonte certa.
- Nao alterar pacote, instalacao ou contexto duradouro sem gate exigido.

## Checklist rapido

Antes de promover qualquer aprendizado, confirme:

- Qual fonte prova o aprendizado?
- O que era esperado e o que aconteceu?
- O que realmente resolveu?
- O escopo e universal, provavel-universal, especifico do projeto ou backlog?
- Qual arquivo deveria ter prevenido a repeticao?
- Qual gate humano falta?
- Como validar que a nova regra funciona?

Se qualquer resposta estiver incerta, registre como candidato ou backlog, nao como regra aplicada.
