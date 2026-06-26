---
name: loki-agent-creator
description: Create or revise Loki agents, Claude Code subagents, or Codex custom agents. Use when the main unit is a specialist role with independent judgment, isolated context, restricted tools, read-only analysis, proposal-only output, or structured handoff back to an orchestrator; also use when deciding between agent, skill, and command.
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

1. Leia primeiro `manifest.yaml`, `docs/source-boundaries.md`,
   `docs/operational-inventory.md`, `docs/usage-guide.md`,
   `docs/loki-plan-execution-workflow.md`, `docs/loki-learning-workflow.md`,
   `docs/package-authoring-guardrails.md` e `docs/project-context-catalog.md`
   do pacote local.
2. Procure agentes existentes em `agents/` e no catalogo aprovado antes de criar um novo papel.
3. Confirme que agente e a abstracao correta:
   - Crie agente quando houver julgamento especialista, pesquisa ruidosa, revisao independente, restricao de ferramentas ou proposta isolada.
   - Use skill quando o valor for procedimento reutilizavel no contexto principal.
   - Use command quando o valor for orquestrar fluxo completo com estado, outputs e gates.
4. Se o agente fizer parte do pacote, rode preflight de autoria: destino correto, docs/manifest impactados, referencias externas classificadas e validacoes finais.
5. Defina uma responsabilidade estreita. O agente deve fazer uma coisa bem e retornar uma saida consolidada.
6. Defina o modo default do Loki como `proposal-only`, salvo approval humano explicito em fase futura.
7. Declare `inputs`, `outputs`, `allowed_writes`, `forbidden_writes`, `response_format`, `confidence`, `risks` e `required_gates`.
8. Nao embuta regras de projeto, engine ou framework em agentes core. Quando retrospectivas tecnicas revelarem padroes de uma tecnologia, gere ou atualize uma skill especializada e referencie-a em `<technology_required_skills>`.
9. Use placeholders genericos para fronteiras do consumidor: `<consumer_runtime_surfaces>`, `<sensitive_write_patterns>`, `<domain_ids>` e `<human_validation_gate>`.
10. Limite ferramentas ao minimo necessario. Agente de pesquisa deve ser read-only; agente implementador sensivel deve propor patch ao orquestrador.
11. Trate Claude Code e Codex como adaptadores diferentes:
   - Claude Code: subagents sao Markdown com frontmatter YAML. `name` e `description` sao obrigatorios; `tools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort` e `isolation` sao opcionais.
   - Codex: custom agents sao arquivos TOML instalados em nivel de usuario ou no projeto consumidor. `name`, `description` e `developer_instructions` sao obrigatorios; `sandbox_mode`, `model_reasoning_effort`, `mcp_servers`, `skills.config` e `nickname_candidates` sao opcionais.
12. Para Codex, lembre que subagents so sao spawned quando o usuario pede explicitamente; eles herdam sandbox/approval do turno pai, e fan-out aumenta custo e latencia.
13. Para Claude Code, escreva uma `description` precisa porque ela orienta delegacao. Ao editar agente direto em disco, planeje reiniciar a sessao quando necessario.
14. Inclua formato de resposta estruturado para o orquestrador detectar conflitos por arquivo, `<domain_ids>`, superficie e gate.
15. Atualize `manifest.yaml` apenas quando o novo agente for aceito no pacote local.

## References

- Read [agent-contract-template.md](references/agent-contract-template.md) when drafting a new agent contract, defining structured handoff output, auditing agent completeness, or citing the external Claude Code/Codex research basis.

## Quality Checklist

- O agente tem julgamento proprio que uma skill nao cobriria melhor.
- O papel e estreito e nao compete com agente existente.
- A `description` inclui gatilhos concretos e limites claros.
- Ferramentas e permissao sao minimas para a tarefa.
- O agente nao escreve diretamente em superficies sensiveis no MVP.
- A saida tem evidencia, risco, confianca e proximo passo.
- O agente declara quando deve parar e devolver ao orquestrador.
- Conflitos por arquivo, `<domain_ids>`, `<consumer_runtime_surfaces>`, gate ou destino ficam detectaveis.
- Se o agente for empacotado, a mudanca respeita `docs/package-authoring-guardrails.md`.
- O agente nao generaliza aprendizado local sem approval.
- A mudanca em agente consolidado tem `technical-review` ou `approval`.

## Inputs

- Demanda do usuario.
- Manifesto, inventario e docs canonicos do pacote local.
- Agentes, commands e skills existentes.
- Politica de orquestracao e gates do Loki.
- Pesquisa atual de Claude Code ou Codex quando a superficie da plataforma estiver em duvida.

## Outputs

- Novo agente ou revisao de agente em Markdown/TOML conforme destino.
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
