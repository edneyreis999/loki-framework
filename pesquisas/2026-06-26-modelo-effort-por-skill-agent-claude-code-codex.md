---
title: Modelo e effort por skill ou agent em Claude Code e Codex
date: 2026-06-26
status: pesquisa
topic: model-effort-routing
scope: claude-code-codex-adapters
sources:
  - https://docs.anthropic.com/en/docs/claude-code/skills
  - https://docs.anthropic.com/en/docs/claude-code/sub-agents
  - https://docs.anthropic.com/en/docs/claude-code/model-config
  - https://docs.anthropic.com/en/docs/claude-code/settings
  - https://developers.openai.com/codex/skills
  - https://developers.openai.com/codex/subagents
  - https://developers.openai.com/codex/config-basic
  - https://developers.openai.com/codex/config-advanced
local_sources:
  - .agents/skills/loki-agent-creator/SKILL.md
  - .agents/skills/loki-agent-creator/references/agent-contract-template.md
---

# Modelo e effort por skill ou agent em Claude Code e Codex

## Pergunta

E possivel configurar um workflow reutilizavel para trocar modelo e nivel de
raciocinio automaticamente, sem alternar manualmente com `/model` a cada task?

Subperguntas:

- Como isso funciona no Codex?
- Como fazer a mesma coisa no Claude Code?
- A skill `.agents/skills/loki-agent-creator` ja contempla esse conhecimento?
- Como esse conhecimento pode melhorar a skill?

## Resposta curta

No Codex, uma `SKILL.md` nao e a superficie documentada para trocar `model` ou
`model_reasoning_effort` do agente principal. Codex skills carregam instrucoes,
scripts e referencias por progressive disclosure; o controle de modelo fica em
`config.toml`, profiles, flags/overrides de CLI, `/model`, ou em custom agents
TOML quando um subagent e explicitamente spawned.

No Claude Code, a resposta e diferente: a propria `SKILL.md` pode declarar
`model` e `effort` no frontmatter. Esse override vale enquanto a skill esta
ativa no turno atual e nao e salvo como configuracao permanente; no prompt
seguinte, a sessao volta ao modelo normal. Claude Code tambem permite `model` e
`effort` em subagents Markdown.

## Achados sobre Codex

Codex skills sao o formato de autoria para workflows reutilizaveis. A skill e
um diretorio com `SKILL.md`, scripts, referencias e assets opcionais. O
`SKILL.md` documentado exige `name` e `description`; a metadata opcional em
`agents/openai.yaml` cobre apresentacao, politica de invocacao implicita e
dependencias de tools, nao selecao de modelo.

Para o agente principal do Codex, o modelo e o effort entram por configuracao:

- `$HOME/.codex/config.toml` para defaults de usuario;
- `.codex/config.toml` para override de projeto confiavel;
- profile em `$HOME/.codex/<profile>.config.toml`, selecionado com
  `codex --profile <profile>`;
- flags ou overrides de CLI, como `codex --model ...` e
  `codex --config model='"..."'`;
- `/model` durante a sessao;
- `model_reasoning_effort` em `config.toml` para effort.

Codex custom agents ficam em `.codex/agents/*.toml` ou
`$HOME/.codex/agents/*.toml`. Eles exigem `name`, `description` e
`developer_instructions`. O arquivo de custom agent pode incluir chaves de
configuracao como `model`, `model_reasoning_effort`, `sandbox_mode`,
`mcp_servers` e `skills.config`. Esses valores configuram o agente spawned, nao
mudam automaticamente o main thread.

Ponto operacional importante: Codex documenta que subagents so sao spawned
quando o usuario pede explicitamente. O fan-out tambem aumenta custo, latencia
e consumo de tokens porque cada subagent faz chamadas e tool work proprios.

### Exemplo Codex

```toml
# .codex/agents/docs-lite.toml
name = "docs_lite"
description = "Documentation-only worker for straightforward edits and summaries."
model = "gpt-5.4-mini"
model_reasoning_effort = "low"
sandbox_mode = "read-only"

developer_instructions = """
Handle documentation-only analysis or small docs edits.
Keep scope narrow, preserve terminology, and return concise evidence.
"""
```

Uso esperado:

```text
Use the docs_lite agent for this documentation task and summarize the result.
```

Para evitar `/model` no main thread sem subagent, o padrao mais limpo e um
profile:

```toml
# $HOME/.codex/docs.config.toml
model = "gpt-5.4-mini"
model_reasoning_effort = "low"
```

```bash
codex --profile docs
```

## Achados sobre Claude Code

Claude Code suporta a mesma ideia de forma mais direta em skills. A
documentacao de skills lista `model` e `effort` no frontmatter de `SKILL.md`:

- `model`: modelo usado quando a skill esta ativa; aceita os mesmos valores de
  `/model` ou `inherit`.
- `effort`: nivel de effort usado quando a skill esta ativa; opcoes incluem
  `low`, `medium`, `high`, `xhigh` e `max`, conforme suporte do modelo.
- O override de `model` vale pelo resto do turno atual e nao e salvo nas
  settings. A sessao retoma o modelo normal no proximo prompt.
- Um modelo bloqueado por `availableModels` nao e usado; Claude Code mantem o
  modelo corrente ou herdado.

Claude Code tambem permite rodar uma skill em subagent com `context: fork` e
opcionalmente escolher `agent`. Nesse caso, a skill vira o prompt da tarefa e o
agent escolhido define ambiente, tools e permissoes.

### Exemplo Claude Code com skill leve

```yaml
---
name: docs-lite
description: Documentation-only workflow for straightforward edits, summaries, and README cleanup.
model: haiku
effort: low
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Review the requested documentation task.
Keep scope narrow, avoid code changes, and return the exact files that should
change plus a concise proposed patch or summary.
```

Esse formato resolve diretamente o caso "documentar com modelo menor" quando o
usuario invoca `/docs-lite`. Se `disable-model-invocation: true` for removido,
Claude tambem pode invocar a skill automaticamente quando a descricao bater com
o pedido.

### Exemplo Claude Code com subagent leve

```markdown
---
name: docs-lite
description: Documentation-only subagent. Use for simple docs review, README cleanup, and summaries where low cost matters more than deep reasoning.
tools: Read, Grep, Glob
model: haiku
effort: low
maxTurns: 6
---

You are a documentation-focused reviewer.
Return concise findings, affected files, confidence, and proposed next step.
Do not edit code.
```

Claude Code subagents sao Markdown com YAML frontmatter. `name` e
`description` sao obrigatorios. Campos opcionais documentados incluem `tools`,
`disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`,
`mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color` e
`initialPrompt`.

O campo `model` do subagent pode usar alias como `sonnet`, `opus`, `haiku`,
`fable`, um model ID completo ou `inherit`. A resolucao documentada para
subagents segue esta ordem:

1. `CLAUDE_CODE_SUBAGENT_MODEL`, se definido.
2. Parametro `model` da invocacao especifica.
3. `model` no frontmatter do subagent.
4. Modelo da conversa principal.

O `effort` do subagent ou skill sobrepoe o effort da sessao enquanto esse agent
ou skill esta ativo, respeitando limitacoes do modelo e politicas de allowlist.

## Diferenca essencial entre plataformas

| Superficie | Codex | Claude Code |
| --- | --- | --- |
| Skill muda modelo do main thread | Nao documentado como suporte | Sim, via `model` no frontmatter da skill |
| Skill muda effort do main thread | Nao documentado como suporte | Sim, via `effort` no frontmatter da skill |
| Agent/subagent com modelo proprio | Sim, custom agent TOML spawned explicitamente | Sim, subagent Markdown e Agent tool |
| Profile/config para default de sessao | Sim, `config.toml` e profiles | Sim, settings, flags, env vars e `/model` |
| Override dura quanto | Config/profile ate ser trocado; custom agent durante spawned agent | Skill: turno atual; subagent: execucao do subagent |
| Invocacao automatica de subagent | Codex: nao, exige pedido explicito | Claude pode delegar por descricao, e tambem aceita @-mention/explicit invocation |

## Analise da skill loki-agent-creator

A skill atual ja contempla parcialmente o conhecimento.

Pontos corretos ja presentes:

- Ela separa Claude Code e Codex como adaptadores diferentes.
- Ela registra que Claude Code subagents sao Markdown com frontmatter YAML.
- Ela registra que `name` e `description` sao obrigatorios em Claude Code
  subagents.
- Ela lista campos opcionais relevantes de Claude Code subagents, incluindo
  `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`,
  `memory`, `background`, `effort` e `isolation`.
- Ela registra que Codex custom agents sao TOML e exigem `name`,
  `description` e `developer_instructions`.
- Ela registra que Codex subagents so sao spawned quando o usuario pede
  explicitamente e que fan-out aumenta custo e latencia.
- Ela orienta criar skill, e nao agent, quando o valor for procedimento
  reutilizavel no contexto principal.

Lacunas encontradas:

- A skill nao explicita que Claude Code skills tambem podem declarar `model` e
  `effort` no frontmatter. Esse e o achado mais importante para a pergunta.
- A skill nao diferencia "Claude skill para trocar modelo no turno atual" de
  "Claude subagent para contexto isolado com modelo proprio".
- A linha de Codex custom agents deveria mencionar `model` como campo opcional,
  alem de `model_reasoning_effort`.
- A skill nao explicita que Codex skills nao sao a superficie documentada para
  trocar modelo/effort.
- A skill nao registra que, em Claude Code, subagents vindos de plugin ignoram
  `hooks`, `mcpServers` e `permissionMode`; isso importa para packaging.
- A skill nao registra a semantica de duracao: Claude skill `model` vale para o
  turno atual; Codex profile/config vale como default de sessao; custom agents
  valem para a execucao spawned.
- A referencia `agent-contract-template.md` cita Claude skills e subagent
  execution, mas nao traz uma matriz de decisao sobre quando usar skill vs
  subagent vs profile para roteamento de modelo.

## Como esse conhecimento pode agregar na skill

Adicionar uma secao curta de "Model and effort routing" na
`loki-agent-creator` ajudaria a evitar overengineering. Hoje um autor Loki pode
criar um agent para uma tarefa que, em Claude Code, seria melhor resolvida por
uma skill com `model: haiku` e `effort: low`.

Recomendacao de regra:

- Use Claude Code skill com `model`/`effort` quando o workflow e procedural,
  reutilizavel e deve rodar no contexto principal ou no turno atual.
- Use Claude Code subagent com `model`/`effort` quando a tarefa precisa de
  contexto isolado, ferramentas restritas, memoria propria, ou retorno resumido
  ao orchestrator.
- Use Codex profile/config quando o objetivo e mudar o default de uma sessao ou
  projeto.
- Use Codex custom agent com `model`/`model_reasoning_effort` quando precisa de
  papel especialista spawned explicitamente.
- Nao prometa em Codex SKILL.md uma troca automatica de modelo/effort; trate
  isso como instrucao desejada, nao como garantia de runtime.

Texto candidato para incorporar na Procedure:

```markdown
Ao escolher entre skill e agent por custo/modelo:
- Claude Code skills podem declarar `model` e `effort` no frontmatter; use isso
  para workflows leves e procedurais que nao precisam de isolamento. O override
  vale para o turno atual da skill.
- Claude Code subagents tambem podem declarar `model` e `effort`; use quando
  houver isolamento de contexto, ferramentas restritas, memoria ou handoff
  consolidado.
- Codex skills nao sao a superficie documentada para trocar modelo ou
  `model_reasoning_effort`; use profile/config para defaults ou custom agent
  TOML spawned explicitamente.
- Em Codex custom agents, inclua `model` e `model_reasoning_effort` quando o
  papel justificar custo/capacidade diferente do parent.
```

Texto candidato para complementar a matriz Claude/Codex:

```markdown
- Claude Code skill: `SKILL.md` com `description`; opcionais uteis para custo
  incluem `model`, `effort`, `context: fork`, `agent`, `allowed-tools` e
  `disable-model-invocation`.
- Claude Code subagent: Markdown com frontmatter YAML; `name` e `description`
  obrigatorios; `model` e `effort` configuram a execucao do subagent.
- Codex skill: `SKILL.md` com `name` e `description`; use para workflow e
  progressive disclosure, nao para runtime model routing.
- Codex custom agent: TOML; `name`, `description` e `developer_instructions`
  obrigatorios; `model`, `model_reasoning_effort`, `sandbox_mode`,
  `mcp_servers`, `skills.config` e `nickname_candidates` opcionais.
```

Atualizar tambem `agent-contract-template.md` com uma pequena tabela de
"routing knobs" por adaptador ajudaria a manter o conhecimento fora do corpo
principal quando ficar longo.

## Implicacao para o Loki Framework

O framework deve tratar "modelo barato para tarefa simples" como decisao de
adaptador, nao como politica universal.

Para Claude Code, o pacote pode oferecer skills leves com frontmatter
`model`/`effort` para tarefas como documentacao, resumo, triagem e leitura.
Isso evita criar subagents desnecessarios.

Para Codex, o pacote deve preferir profiles documentados ou custom agents TOML
quando houver necessidade real de modelo/effort diferente. Skills Codex devem
continuar focadas em procedimento, entrada/saida, referencias e validacao.

## Proximos passos sugeridos

1. Atualizar `.agents/skills/loki-agent-creator/SKILL.md` com a regra de
   roteamento de modelo/effort por adaptador.
2. Corrigir a lista Codex custom agent para incluir `model`.
3. Adicionar a caveat de plugin subagents Claude Code para `hooks`,
   `mcpServers` e `permissionMode`.
4. Avaliar se `loki-skill-creator` tambem precisa conhecer Claude Code skill
   frontmatter `model`, `effort`, `context`, `agent`, `allowed-tools` e
   `disable-model-invocation`.
5. Se a mudanca virar normativa no pacote, aplicar `technical-review` conforme
   `docs/package-authoring-guardrails.md`.
