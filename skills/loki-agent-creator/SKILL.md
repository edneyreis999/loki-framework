---
name: loki-agent-creator
description: Create or revise Loki agents, Claude Code subagents, or Codex custom agents. Use when the main unit is a specialist role with independent judgment, isolated context, restricted tools, read-only analysis, proposal-only output, or structured handoff back to an orchestrator; also use when deciding between agent, skill, and command.
when_to_use:
  - "Use when creating or revising Loki agents, Claude Code subagents, or Codex custom agents."
  - "Use when the work needs specialist judgment, isolated context, restricted tools, or proposal-only output."
  - "Use when deciding whether a workflow belongs in an agent, skill, or command."
argument-hint: "[agent purpose, target adapter, allowed writes, gates]"
arguments:
  required: []
  optional:
    - agent_purpose
    - target_adapter
    - allowed_writes
    - gates
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - cross-adapter agent projection
  - durable package artifact changes
  - restricted tool or write boundary design
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-agent-creator/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:continuous-improvement
  - manual-framework-evolution
---

# loki-agent-creator

## When To Use

Use para criar ou revisar um agente Loki, subagent Claude Code, ou custom agent Codex quando a unidade principal for papel especialista com julgamento proprio, isolamento de contexto, ferramentas restritas ou saida `read-only`/`proposal-only`.

Use tambem quando houver duvida entre criar um agente, uma skill ou um comando.

## Procedure

1. Leia primeiro as regras embutidas nesta skill e
   `references/agent-contract-template.md`. Se estiver rodando dentro da fonte
   do pacote Loki e `manifest.yaml` ou `docs/*.md` estiverem disponiveis,
   use-os como contexto adicional. Quando a skill estiver instalada em um
   projeto consumidor sem docs do pacote, nao bloqueie a execucao; use os
   artefatos Loki visiveis e declare a limitacao.
2. Procure agentes existentes em `agents/` e no catalogo aprovado antes de criar um novo papel.
3. Confirme que agente e a abstracao correta:
   - Crie agente quando houver julgamento especialista, pesquisa ruidosa, revisao independente, restricao de ferramentas ou proposta isolada.
   - Use skill quando o valor for procedimento reutilizavel no contexto principal.
   - Use command quando o valor for orquestrar fluxo completo com estado, outputs e gates.
4. Se o agente fizer parte do pacote, rode preflight de autoria: destino correto, artefatos impactados, docs/manifest impactados quando disponiveis, referencias externas classificadas e validacoes finais.
5. Gere agentes multi-adapter por padrao. Nao ramifique o contrato pelo executor atual; some os metadados conhecidos de Claude Code, Codex e Loki, usando valores neutros validos quando um campo nao se aplicar.
6. Preencha o superset de metadados de agente:
   - Loki/common: `name`, `description`, `type`, `status`, `mode`, `purpose`, `when_to_trigger`, `inputs`, `outputs`, `allowed_writes`, `forbidden_writes`, `response_format`, `confidence`, `risks`, `required_gates`.
   - Claude Code subagent: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`.
   - Codex custom agent TOML: `name`, `description`, `developer_instructions`, `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `approval_policy`, `mcp_servers`, `skills.config`.
7. Quando formatos de runtime divergirem, mantenha um contrato Loki como fonte e gere as projecoes exigidas: Markdown/YAML para Claude Code e TOML em `codex/agents/` para Codex.
8. Defina uma responsabilidade estreita. O agente deve fazer uma coisa bem e retornar uma saida consolidada.
9. Defina o modo default do Loki como `proposal-only`, salvo approval humano explicito em fase futura.
10. Nao embuta regras de projeto, engine ou framework em agentes core. Quando retrospectivas tecnicas revelarem padroes de uma tecnologia, gere ou atualize uma skill especializada e referencie-a em `<technology_required_skills>`.
11. Use placeholders genericos para fronteiras do consumidor: `<consumer_runtime_surfaces>`, `<sensitive_write_patterns>`, `<domain_ids>` e `<human_validation_gate>`.
12. Limite ferramentas e permissoes ao minimo necessario. Em plugin Claude Code, nao dependa de `hooks`, `mcpServers` ou `permissionMode` para comportamento essencial, porque esses campos podem ser ignorados.
13. Para Codex, lembre que subagents so sao spawned quando o usuario pede explicitamente; eles herdam sandbox/approval do turno pai, e fan-out aumenta custo e latencia.
14. Inclua formato de resposta estruturado para o orquestrador detectar conflitos por arquivo, `<domain_ids>`, superficie e gate.
15. Atualize `manifest.yaml` apenas quando o novo agente for aceito no pacote local.

## References

- Read [agent-contract-template.md](references/agent-contract-template.md) when drafting a new agent contract, defining structured handoff output, auditing agent completeness, or citing the external Claude Code/Codex research basis.

## Quality Checklist

- O agente tem julgamento proprio que uma skill nao cobriria melhor.
- O papel e estreito e nao compete com agente existente.
- A `description` inclui gatilhos concretos e limites claros.
- O superset de metadados multi-adapter foi preenchido ou recebeu valor neutro valido.
- Ferramentas, modelo, effort, permissoes e gates sao minimos para a tarefa.
- O agente nao escreve diretamente em superficies sensiveis no MVP.
- A saida tem evidencia, risco, confianca e proximo passo.
- O agente declara quando deve parar e devolver ao orquestrador.
- Conflitos por arquivo, `<domain_ids>`, `<consumer_runtime_surfaces>`, gate ou destino ficam detectaveis.
- Se o agente for empacotado, a mudanca respeita as regras de autoria do pacote
  embutidas nesta skill e os guardrails do pacote quando estiverem disponiveis.
- O agente nao generaliza aprendizado local sem approval.
- A mudanca em agente consolidado tem `technical-review` ou `approval`.

## Inputs

- Demanda do usuario.
- Manifesto, inventario ou docs canonicos do pacote local, quando disponiveis.
- Agentes, commands e skills existentes.
- Politica de orquestracao e gates do Loki.
- Pesquisa atual de Claude Code ou Codex quando a superficie da plataforma estiver em duvida.

## Outputs

- Novo agente ou revisao de agente em Markdown/TOML conforme destino.
- Contrato fonte multi-adapter e projecoes de runtime quando o formato exigir.
- Contrato de papel, gatilhos, ferramentas, writes e gates.
- Registro no `manifest.yaml` quando aprovado.
- Lista de validacoes de pacote quando o destino for componente consolidado.
- Backlog quando a demanda nao justificar agente.

## Limits

- Nao criar agente para prompt reutilizavel simples; crie skill.
- Nao criar agente para fluxo invocavel completo; crie command.
- Nao permitir escrita sensivel direta no MVP.
- Nao criar fan-out recursivo sem necessidade explicita.
- Nao instalar automaticamente em `.claude/**`, `.codex/**` ou `.agents/**`.

## Required Gates

- `technical-review` para mudanca em agente, command, skill, template, validator ou doc consolidado.
- `approval` para permissao de escrita, nova politica duradoura, instalacao ou promocao normativa.
- `<human_validation_gate>` quando o agente propuser validar comportamento em `<consumer_runtime_surfaces>`.
