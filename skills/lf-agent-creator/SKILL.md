---
name: lf-agent-creator
description: Create or revise Loki agents, Claude Code subagents, or Codex custom agents. Use when the main unit is a specialist role with independent judgment, isolated context, restricted tools, read-only analysis, proposal-only output, scoped-writer output, or structured handoff back to an orchestrator; also use when deciding between agent, skill, and command.
when_to_use:
  - "Use when creating or revising Loki agents, Claude Code subagents, or Codex custom agents."
  - "Use when the work needs specialist judgment, isolated context, restricted tools, proposal-only output, or scoped-writer output."
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
hooks: {}
paths:
  package_skill: "skills/lf-agent-creator/SKILL.md"
shell: bash
type: skill
status: draft
used_by:
  - loki-continuous-improvement
  - manual-framework-evolution
---

# lf-agent-creator

## When To Use

Use para criar ou revisar um agente Loki, subagent Claude Code, ou custom agent
Codex quando a unidade principal for papel especialista com julgamento proprio,
isolamento de contexto, ferramentas restritas ou saida
`read-only`/`proposal-only`/`scoped-writer`.

Use tambem quando houver duvida entre criar um agente, uma skill ou um comando.

## Procedure

1. Leia primeiro `manifest.yaml`, `docs/source-boundaries.md`,
   `docs/operational-inventory.md`, `docs/usage-guide.md`,
   `docs/loki-plan-execution-workflow.md`, `docs/loki-learning-workflow.md`,
   `docs/package-authoring-guardrails.md` e `docs/project-context-catalog.md`
   do pacote local.
2. Procure agentes existentes em `agents/` e no catalogo aprovado antes de criar um novo papel.
3. Confirme que agente e a abstracao correta:
   - Use a heuristica curta: agent = quem julga, skill = como executar, command = o que orquestrar.
   - Crie agente quando houver julgamento especialista, pesquisa ruidosa, revisao independente, restricao de ferramentas ou proposta isolada.
   - Use skill quando o valor for procedimento reutilizavel no contexto principal.
   - Use command quando o valor for orquestrar fluxo completo com estado, outputs e gates.
   - Se o corpo do agente estiver virando receita repetivel, checklist operacional longo, passos de ferramenta ou comando executavel, mova esse procedimento para uma skill e deixe o agente com papel, julgamento, limites e handoff.
4. Se o agente fizer parte do pacote, rode preflight de autoria: destino correto, docs/manifest impactados, referencias externas classificadas e validacoes finais.
5. Gere agentes multi-adapter por padrao. Nao ramifique o contrato pelo executor atual; some os metadados conhecidos de Claude Code, Codex e Loki, usando valores neutros validos quando um campo nao se aplicar.
6. Preencha o superset de metadados de agente:
   - Loki/common: `name`, `description`, `type`, `status`, `mode`, `purpose`, `when_to_trigger`, `inputs`, `outputs`, `allowed_writes`, `forbidden_writes`, `response_format`, `confidence`, `risks`, `required_gates`.
   - Claude Code subagent: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`.
   - Codex custom agent TOML: `name`, `description`, `developer_instructions`, `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `approval_policy`, `mcp_servers`, `skills.config`.
7. Quando formatos de runtime divergirem, mantenha um contrato Loki como fonte e gere as projecoes exigidas: Markdown/YAML para Claude Code e TOML em `codex/agents/` para Codex.
8. Defina uma responsabilidade estreita, capacidades incluídas/excluídas e
   modos compatíveis. `read-only`, `proposal-only` e `scoped-writer` são modos
   operacionais, não categorias mutuamente exclusivas: o envelope aprovado
   escolhe o modo ativo e nunca concede escrita global.
9. Defina o modo default do Loki como `proposal-only`, salvo approval humano
   explicito ou politica de pacote que autorize um `scoped-writer` com
   `target_files`, dominios de escrita, validators, gates e proibicoes
   sensiveis.
10. Modele participacao de agente de dominio no `loki-init` somente como
   `init_inventory_domain_investigator`, em `read-only` ou `proposal-only`.
   O investigador emite research packets estruturados, completion record e
   continuation cursor ao orquestrador; ele nunca escreve consumer docs, chama
   o `catalogador` diretamente ou recebe fallback documental. A autoria de
   consumer docs pertence exclusivamente ao `catalogador`.
11. Quando um workflow Loki autorizar escrita por agente, declare somente os
   modos escopados aplicaveis ao trabalho ordinario, como
   `task_scoped_writer`, e exija caminhos exatos no envelope do workflow
   chamador. Escrita `task_scoped_writer` pode cobrir codigo, configuracao, conteudo,
   dialogo, dados, assets ou runtime somente quando a task aprovada declarar
   `target_files`, owner, skill tecnica aplicavel, validators e gates. Fora
   desse envelope, o agente retorna proposta, checklist ou achado.
12. Para um Write Agent de dominio em trabalho ordinario fora de consumer docs,
   aplique `lf-domain-context-preflight` pessoal antes da escrita quando a
   formula de metadata indicar: `installed_in_consumer: true`, `category:
   Write Agent`, `task_write_mode` contendo `task_scoped_writer`,
   `durable_context_root` declarado e papel de agente de dominio. O
   `active_mode` da invocacao pode ser `scoped-writer`; ele nao substitui a
   chave do modo de task. O agente usa leitura minima suficiente,
   trata fonte local atual como prevalente sobre snapshot duradouro e devolve
   gaps ao destino documental fornecido pelo caller; ele nao corrige docs por
   conta propria. `ready-with-gaps` permite seguir quando a lacuna nao for
   material; `blocked` impede a escrita.
13. Classifique writes por root resolvido, nao apenas pelo texto do path.
   `consumer-docs` sob o consumer project root e exclusivo do `catalogador`;
   `package-documentation` sob o package root pertence somente ao writer
   interno aprovado. Um agent de dominio nunca converte uma classe na outra.
14. Nao embuta regras de projeto, engine ou framework em agentes core. Quando retrospectivas tecnicas revelarem padroes de uma tecnologia, gere ou atualize uma skill especializada e referencie-a em `<technology_required_skills>`.
15. Use placeholders genericos para fronteiras do consumidor: `<consumer_runtime_surfaces>`, `<sensitive_write_patterns>`, `<domain_ids>` e `<human_validation_gate>`.
16. Limite ferramentas e permissoes ao minimo necessario. Em plugin Claude Code, nao dependa de `hooks`, `mcpServers` ou `permissionMode` para comportamento essencial, porque esses campos podem ser ignorados.
17. Para Codex, lembre que subagents so sao spawned quando o usuario pede explicitamente; eles herdam sandbox/approval do turno pai, e fan-out aumenta custo e latencia.
18. Inclua formato de resposta estruturado para o orquestrador detectar conflitos por arquivo, `<domain_ids>`, superficie e gate.
19. Exija de cada agente um completion record compacto com identidade e
   parentage fornecidos pelo orquestrador, resultado, arquivos, validators,
   gates, riscos e proximo destino. Proiba coleta de IDs/tokens por inferencia e
   qualquer cadeia de raciocinio privada. O orquestrador, e nao o agente,
   captura evidence sanitizada ou registra `partial`, `unavailable` ou
   `unsupported`; retrospectiva so ocorre por acao humana ou command explicito.
20. Antes de concluir, exija entradas, destinos de handoff de sucesso/falha,
   validação antes do handoff, condições de parada e completion record honesto.
   Um scoped-writer recebe targets, owner, domínios, validators, gates e roteiro
   humano quando a validação não for determinística; remove temporários salvo
   evidência autorizada em `planos/`.
21. Antes de concluir, rode validação estrutural: frontmatter mínimo, modos,
   `allowed_writes`, `forbidden_writes`, `required_gates`, `response_format` e
   TOML Codex pareado quando existir projeção. Aplique a checklist 24/24 da
   referência e corrija todo `não` antes da entrega.
22. Atualize `manifest.yaml` apenas quando o novo agente for aceito no pacote local.

## References

- Read [agent-contract-template.md](references/agent-contract-template.md) when drafting a new agent contract, defining structured handoff output, auditing agent completeness, or citing the external Claude Code/Codex research basis.

## Quality Checklist

- O agente tem julgamento proprio que uma skill nao cobriria melhor.
- A decisao agent/skill/command passou pela regra: quem julga, como executar, o que orquestrar.
- Procedimentos repetiveis, comandos, receitas de ferramenta e checklists longos foram movidos para skill ou command, nao embutidos no agente.
- O papel e estreito e nao compete com agente existente.
- A `description` inclui gatilhos concretos e limites claros.
- O superset de metadados multi-adapter foi preenchido ou recebeu valor neutro valido.
- O agente declara `mode`, `allowed_writes`, `forbidden_writes`, `required_gates` e `response_format`.
- Ferramentas, modelo, effort, permissoes e gates sao minimos para a tarefa.
- O agente nao escreve diretamente em superficies sensiveis sem task aprovada,
  owner, skill tecnica aplicavel, validators e gates.
- Quando `mode: scoped-writer`, o contrato declara `sandbox_mode`,
  `scoped_write_modes`, `task_write_mode`/destino equivalente, ferramentas
  minimas, dominios de escrita e Allowed Writes com caminhos exatos recebidos
  pelo envelope.
- Um agente de dominio participa do init somente como
  `init_inventory_domain_investigator`, sem consumer-doc writes, e devolve
  research packets/continuation ao orquestrador; `catalogador` e o unico autor
  de consumer docs e nao existe fallback.
- Um Write Agent de dominio faz seu proprio `lf-domain-context-preflight` antes
  de task writes quando a formula de metadata se aplica; respeita precedencia
  da fonte atual e roteia gaps sem autoeditar documentacao.
- `consumer-docs` e `package-documentation` sao distinguidos pelo root
  resolvido e somente o writer interno aprovado mantem docs do pacote.
- O agente devolve completion record; evidence e gaps pertencem ao
  orquestrador. Nenhum contrato exige retrospectiva automática ou escrita em
  `target_retrospective` como fallback.
- A saida tem evidencia, risco, confianca e proximo passo.
- O agente declara quando deve parar e devolver ao orquestrador.
- Conflitos por arquivo, `<domain_ids>`, `<consumer_runtime_surfaces>`, gate ou destino ficam detectaveis.
- Se o agente for empacotado, a mudanca respeita `docs/package-authoring-guardrails.md`.
- Se houver projecao Codex, o TOML em `codex/agents/` existe, acompanha o nome base do agente e parseia com `tomllib`.
- O agente nao generaliza aprendizado local sem approval.
- Para uma mudança de pacote, use somente a ramificação
  `destination_scope: package` de `loki-continuous-improvement`, com approval
  aplicável, Writer, checks determinísticos e Auditor independente; trabalho do
  consumidor não aciona esse fluxo.
- O contrato declara capacidades/modos, handoffs de sucesso/falha, validação,
  stop conditions, temporários, testes e completion record conforme a checklist
  24/24 da referência.

## Inputs

- Demanda do usuario.
- Manifesto, inventario e docs canonicos do pacote local.
- Agentes, commands e skills existentes.
- Politica de orquestracao e gates do Loki.
- Pesquisa atual de Claude Code ou Codex quando a superficie da plataforma estiver em duvida.

## Outputs

- Novo agente ou revisao de agente em Markdown/TOML conforme destino.
- Contrato fonte multi-adapter e projecoes de runtime quando o formato exigir.
- Contrato de papel, gatilhos, ferramentas, writes e gates.
- Registro no `manifest.yaml` quando aprovado.
- Lista de validacoes de pacote quando o destino for componente consolidado, incluindo check estrutural de agente e TOML Codex quando aplicavel.
- Backlog quando a demanda nao justificar agente.

## Limits

- Nao criar agente para prompt reutilizavel simples; crie skill.
- Nao criar agente para fluxo invocavel completo; crie command.
- Nao permitir escrita sensivel direta no MVP.
- Nao criar fan-out recursivo sem necessidade explicita.
- Nao instalar automaticamente em `.claude/**`, `.codex/**` ou `.agents/**`.

## Required Concrete Controls

- `approval` para permissao de escrita, nova politica duradoura, instalacao ou promocao normativa.
- `<human_validation_gate>` quando o agente propuser validar comportamento em `<consumer_runtime_surfaces>`.
