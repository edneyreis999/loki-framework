# Execution — loki-init

## Purpose And Observable Contract

Este command é o orquestrador que cria ou audita documentação mínima duradoura e
estado operacional retomável de um consumidor recém-instalado, sem modificar o
runtime do projeto.

- Início: Input normalizado, raiz consumidora resolvida, destinos dentro das
  fronteiras permitidas e modo válido.
- Conclusão: inventário comum, contexto de tecnologia, inventários de domínio,
  catálogo e estado do plano foram materializados ou auditados; cada agente e
  handoff atingiu estado terminal; validators e gates foram registrados; e não
  resta stop condition ativa.
- Resultado verificável: `docs/**` e `planos/000-init-loki/**` contêm os outputs
  aplicáveis, completion records, evidência sanitizada ou gaps explícitos, e
  `loki_init_state` retomável.
- Saídas obrigatórias: cumpra integralmente `references/response.md` e os Output
  Contracts abaixo.

`loki-init` é a identidade canônica; `init-loki` pode ser alias de adapter, sem
criar outro workflow.

## Execution Profile

```yaml
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - consumer documentation bootstrap
    - multi-agent fan-out and serial consolidation
    - consumer write boundaries
  handoff_effort:
    research: medium
    coding: low
    documentation_transient: medium
    documentation_durable: high
    validator: medium
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response. Decomponha o fluxo em unidades com
responsáveis, selecione agentes, forneça contexto autocontido, acompanhe todos
os handoffs até sucesso, falha, bloqueio ou parada explícita, aplique validators,
gates e approvals e consolide outputs, evidências, riscos e próximos passos.
Mantenha responsabilidade pelo progresso e estado global depois de delegar.

## Dependencies And Conditional Skills

```yaml
required_skills: []
required_commands: []
```

Carregue `lf-index-navigator` somente quando `docs/index.xml` existir e precisar
ser lido. Carregue `<technology_required_skills>` somente quando inventário,
usuário ou especialista declarar tecnologia concreta. O core passa tecnologia e
skills candidatas aos envelopes, mas não executa regra de engine. Todo agente
invocado devolve completion record; o orquestrador captura evidence sanitizada
ou declara gap explícito, sem auto-retrospectiva.

## Mandatory Inventory Contract

Leia integralmente
[`docs/loki-init-inventory-contracts.md`](../../../docs/loki-init-inventory-contracts.md)
antes de construir envelopes. Ele é a fonte obrigatória para contrato universal,
frescor e cobertura de cada pasta de domínio. Valide a pasta inteira; não imponha
nome, quantidade de arquivos ou seções que o contrato não exige.

## Allowed And Forbidden Writes

`allowed_writes` do consumidor:

- `docs/**` dentro de `consumer_project_root`;
- `planos/000-init-loki/**` dentro de `consumer_project_root`.

A invocação aprova somente esses destinos. Preserve conteúdo existente em modo
merge/audit; nunca sobrescreva silenciosamente. `forbidden_writes` inclui
runtime, engine, código, assets, dados gerados, build outputs, dependências,
`<consumer_runtime_surfaces>`, `<sensitive_write_patterns>`, `.agents/**`,
`.codex/**`, `.claude/**`, `AGENTS.md`, `CLAUDE.md` e qualquer path fora dos
dois roots.

## Preflight And Execution Plan

1. Consuma o registro normalizado e monte plano com etapas, dependências,
   responsáveis, envelopes, writes, validators, gates e critérios de conclusão.
2. Declare allowed/forbidden writes e crie ou audite `docs/`, plan root,
   `interaction/fase1/`, `builds/fase1/` e `retrospetivas/fase1/` somente quando
   necessários ao modo ativo.
3. Faça preflight explícito da capacidade de agentes/delegação do adapter antes
   de alegar indisponibilidade. Em Codex, solicite a capacidade e use descoberta
   dirigida de ferramentas multi-agent/subagent; namespaces descobertos são
   evidência da sessão, não contrato universal.
4. Verifique se o adapter concede a cada agente escrita escopada em seu
   `target_inventory_dir` quando aplicável e no próprio
   evidence capture pelo orquestrador. Marque `blocked` ou `skipped` com motivo antes do
   fan-out quando não conceder.
5. Faça preflight do catálogo. Use `manifest.yaml` instalado como fonte primária
   de `supported_project_types`, `agent_project_tag_policy` e
   `agents[].project_tags`. Superfícies aprovadas como `.codex/agents`,
   `.agents/agents`, `agents/`, `codex/agents/` ou lista equivalente comprovam
   disponibilidade, não tags nem autorização de escrita.
6. Registre fonte do catálogo, tipos suportados, base tag, tags por agente,
   agentes disponíveis, ferramentas e limites de descoberta.
7. Replaneje explicitamente quando capability, catálogo, hint, evidência,
   validator ou handoff invalidar seleção, ordem, owner ou etapa posterior.

## Common Inventory And Technology Context

Execute primeiro o inventário comum sequencial: mapeie árvore com
`max_scan_depth`, includes e excludes; filtre binários, gerados e arquivos
grandes; registre docs, manifests, comandos, stack, áreas, concerns, lacunas e
superfícies sensíveis. Git é evidência auxiliar, nunca requisito. Produza ou
audite `docs/loki-init/project-inventory.md`; se impossível, registre falha
estruturada em `builds/fase1/`.

Depois detecte ou aplique hints de projeto, engine e framework. Selecione
exatamente um `selected_project_type` de `supported_project_types`; `core` é tag
base sempre incluída, não tipo classificável. Hint fora da lista vira conflito
ou open question antes do fan-out. Registre evidência, confiança, skills
técnicas candidatas, superfícies sensíveis, validators e gates em
`technology-context.md` ou `engine-context.md`.

## Agent Classification

Construa `inventory_required` como união ordenada, sem duplicatas, dos agentes
com tag base `core` e dos agentes com `selected_project_type`. Registre
`inventory_required_reasons` por agente. Para `software-development`, apenas
agentes `core` são válidos enquanto não houver especialista com essa tag.

Classifique os 15 Write Agents de domínio como
`init_inventory_domain_writer`:

- `audio-designer`, `balance-economy-designer`, `game-business-analyst`,
  `game-designer`, `game-product-owner`,
  `gameplay-engineer`, `level-designer`, `narrative-designer`, `narrative-qa`,
  `quest-content-designer`, `runtime-qa`, `scene-presentation-designer`,
  `technical-artist`, `technical-implementer` e `ux-ui-designer`.

Classifique somente `catalogador` como `init_final_cataloger`. Classifique
`standards-curator`, `retrospective-digester`, `execution-context-reader`,
`source-researcher` e `bibliotecario` como `init_support_only`.

Mantenha `catalogador` fora do fan-out mesmo quando requerido. Agentes support
only são invocados somente para leitura, pesquisa, validação, classificação ou
orientação necessária; não recebem `target_inventory_dir` nem escrevem docs
finais, runtime, assets, código ou config.

## Self-Contained Agent Envelope

Delegue análise, pesquisa, implementação, teste e revisão ao agente que possua a
responsabilidade correspondente sempre que possível; mantenha no command apenas
coordenação, acompanhamento e consolidação.

Antes de invocar qualquer agente, entregue objetivo/motivo, unidade de trabalho,
fatos, decisões, restrições, sources, dependências, escopo, allowed/forbidden
writes, owner, critérios de sucesso/falha/conclusão, validators, gates,
approvals, output esperado e destino/condições do handoff. Proíba referências
implícitas como “continue” ou “use o contexto acima”.

Cada domain writer recebe no mínimo:

```yaml
agent_init_envelope:
  agent: "<agent-name>"
  project_tags: []
  selection_reason: []
  init_class: "init_inventory_domain_writer"
  target_inventory_dir: "docs/loki-init/<agent-name>/"
  inventory_contract: "docs/loki-init-inventory-contracts.md"
  allowed_writes:
    - "docs/loki-init/<agent-name>/**"
  allowed_sources:
    - "docs/loki-init/project-inventory.md"
    - "docs/loki-init/technology-context.md"
    - "docs/index.xml"
    - "<agent-specific-source>"
  forbidden_writes:
    - ".agents/**"
    - ".codex/**"
    - ".claude/**"
    - "AGENTS.md"
    - "CLAUDE.md"
    - "<consumer_runtime_surfaces>"
  completion_record:
    required: true
    evidence_capture_owner: "orchestrator"
    gap_states: ["partial", "unavailable", "unsupported"]
    source_scope:
      - "own execution trace"
      - "own target_inventory_dir or structured support result"
      - "own validations, blockers, useful and bad inferences, tool friction and residual risks"
  write_mode:
    final_artifacts: "direct-target-inventory-dir"
```

Support-only recebe o mesmo contrato sem inventory dir, com
`final_artifacts: structured-support-result-only`. Catalogador recebe envelope
final apenas na consolidação, com pastas validadas em `allowed_sources` e
destinos exatos em `allowed_writes`; ambos devolvem completion record.

Registre para cada handoff origem, destino, objetivo, entrada, resultado
esperado, status, evidência recebida e próximo destino. Acompanhe até estado
terminal; invocação não é conclusão.

## Fan-Out, Write Ownership And Direct-Write Exception

Registre a matriz `available -> inventory_required -> selected -> planned ->
invoked | blocked | skipped`, com motivos, classe, output, inventory dir e
completion/evidence state por agente. Todo requerido deve alcançar uma dessas categorias.

Execute domain writers em lotes conservadores. Use `agents.max_threads` quando
conhecido; caso contrário, use 6 como teto inicial. Registre limites configurado
e observado e feche agentes concluídos antes de abrir novo lote. Leituras
independentes podem ser paralelas; atribua owner único por arquivo, detecte
overlap e serialize writes compartilhados.

Cada domain writer escreve a própria pasta e devolve completion record; o
handoff do orquestrador não os substitui. Sem conteúdo útil, o agente devolve
falha estruturada. Support-only não escreve artefato persistente por padrão.

Qualquer criação, alteração, movimento ou remoção deve ser delegada ao Write
Agent apropriado sempre que ele existir. Escrita direta pelo orquestrador é
exceção somente após registrar indisponibilidade de Write Agent; conveniência,
velocidade ou tamanho não justificam. Declare antes target files,
allowed/forbidden writes, owner único, validators, gates/approvals, critérios e
evidências. Pare se o envelope não cobrir a mudança. Registre no completion
record o tipo de implementação direta, motivo da ausência, oportunidade/escopo
de futuro Write Agent, evidências e riscos.

## Serial Consolidation

Depois do fan-out:

1. Valide a materialização de cada inventory dir e completion/evidence state requerido.
2. Valide cada pasta inteira contra o contrato obrigatório.
3. Reabra docs/fontes atuais antes de conclusão duradoura sensível a frescor;
   não faça rescan amplo quando frescor não importar.
4. Invoque `catalogador` exatamente uma vez, depois das validações, com fontes e
   destinos exatos. Ele não recebe inventory dir próprio.
5. Consolide conflitos e perguntas em `conflicts-and-decisions.md` e
   `open-questions.md`; atualize `docs/index.xml`, `docs/loki-init/README.md`,
   estado/tasks do init e próximo command recomendado.

## Output Contracts

Documentação permitida inclui `docs/index.xml`, `docs/loki-init/README.md`,
`project-inventory.md`, technology/engine context, open questions, conflicts and
decisions e `docs/loki-init/<agent-name>/**`.

Estado permitido inclui `tasks.md`, `task-1.1.md` quando materializado,
`interaction/fase1/**`, `builds/fase1/**` e `retrospetivas/fase1/**` sob plan
root.

Domain inventory contém fontes, fatos separados de inferências, mapa, cobertura,
limites e falha estruturada quando necessário. Resultado do catalogador lista
fontes, destinos, conflitos e lacunas. Support result contém `Status`, `Sources
Attempted`, `Sources Read`, `Evidence Map`, `Missing Evidence`, `Minimum Next
Question`, `Do Not Assume` e `Context Budget Used`. Cada retrospectiva contém
objetivo, status, artefatos, validações, decisões, atritos, inferências úteis e
ruins, ferramentas, mismatches, riscos e próximo caminho mínimo.

## Validators

- Apenas docs root e plan root foram escritos; runtime, assets, dados gerados,
  mirrors e arquivos de contexto proibidos permaneceram intactos.
- `project-inventory.md` existe ou há falha estruturada em builds.
- Contexto de tecnologia registra evidência, confiança,
  `selected_project_type` e skills sugeridas sem hardcode de engine.
- Tipo selecionado pertence aos tipos suportados; base tag é `core`, `core` não
  é tipo suportado, cada agente tem tags não vazias/válidas e cada
  `codex_agents[].source_agent` aponta para agente existente.
- Fan-out registra capability preflight, discovery, catálogo, tipos, tags,
  available, required, planned, invoked, blocked e skipped com motivos.
- Capacidade de escrita de retrospective foi registrada ou bloqueio/pulo
  justificado; classes domain, final cataloger e support-only estão separadas.
- Required inventory é exatamente a união ordenada por tags; todo requerido tem
  estado rastreado; regra de software-development/core foi respeitada.
- Catalogador está somente na classe final, nunca no fan-out paralelo.
- Cada domain writer materializou e validou sua pasta contra o contrato.
- Conclusões freshness-sensitive foram rechecadas sem rescan desnecessário.
- Catalogador rodou no máximo uma vez, somente depois das validações.
- Cada agente invocado devolveu completion record; o orquestrador capturou
  evidence ou registrou gap explícito, sem retrospectiva automática.
- Support-only não escreveu docs finais, index, tasks ou runtime.
- `docs/index.xml` foi atualizado quando docs duradouros foram criados.
- Tasks e resume state refletem status, conflitos, validators e próximo command.
- Nenhum comportamento perceptível, runtime, integração, save/load, gameplay,
  UI, áudio, build ou persistência foi declarado validado sem human validation.

Registre cada validator, resultado, evidência e justificativa de não
aplicabilidade. Validator obrigatório ausente, falho ou inconclusivo interrompe
o fluxo.

## Human Gates

- `approval` para destino fora dos dois roots ou escrita sensível.
- `technical-review` para contrato de pacote, agent, skill, template ou
  validator.
- `human-validation` antes de declarar runtime, comportamento, integração,
  build, gameplay, UI, áudio ou persistência validados.
- `interview` para root, destino, modo, conflito ou classificação material
  ambígua.

Aplique cada gate antes da ação dependente. Validação automática não substitui
gate humano. Pare quando gate/approval obrigatório estiver ausente, pendente ou
rejeitado.

## Stop Conditions

Pare diante de root/destino/modo ambíguo; escopo ou permissão insuficiente;
destino fora dos roots; conflito sem merge seguro; dependência ou handoff sem
destino; writer concorrente; validator ausente/falho; gate/approval ou decisão
humana pendente; inventário comum/falha estruturada impossível; domain writer
sem capacidade para pasta ou falha; agente sem retrospective; catalogador antes
da validação ou sem envelope exato; ou pedido runtime sem skill, validator e
human validation. Não declare conclusão com qualquer condição ativa.

## Resume Contract

Mantenha `loki_init_state` em `tasks.md` ou build report equivalente com roots,
modo, fase/status, paths criados/auditados, arquivos escaneados/lidos, filtros,
áreas, tipos/engines detectados, selected type, git availability, agent outputs,
capability/discovery/catalog source, supported types, tag policy/tags,
available/required/reasons/classes/selected/planned/invoked/blocked/skipped,
inventory dirs/contracts, catalog/support/retrospective outputs, retrospective
write capability, batch limits, write modes, conflicts, open questions,
validators, gates, blockers, etapas concluídas, próximo command/ação e condição
para continuar. Preserve evidência e retome desse estado sem reiniciar.

Use esta forma mínima estável:

```yaml
loki_init_state:
  consumer_project_root: ""
  docs_root: "docs"
  plan_root: "planos/000-init-loki"
  mode: "full-init"
  current_phase: "fase1"
  status: ""
  created_or_audited_paths: []
  inventory:
    files_scanned: []
    files_deep_read: []
    ignored_patterns: []
    project_areas: []
    detected_project_type: []
    selected_project_type: ""
    detected_engines: []
    git_available: false
  agent_outputs: {}
  agent_fanout:
    capability_preflight: ""
    discovery_method: ""
    agent_catalog_source: []
    supported_project_types: []
    agent_project_tag_policy:
      base_tag: ""
      selection_rule: ""
    agent_project_tags: {}
    compatible_tools_found: []
    available: []
    inventory_required: []
    inventory_required_reasons: {}
    init_inventory_domain_writers: []
    init_final_cataloger: []
    init_support_only_agents: []
    selected: []
    planned: []
    invoked: []
    blocked: []
    skipped: []
    skipped_reasons: {}
    target_inventory_dirs: {}
    inventory_contracts: {}
    cataloger_outputs: {}
    target_retrospectives: {}
    retrospective_write_capability: {}
    support_outputs: {}
    retrospective_outputs: {}
    batch_limit_configured: null
    batch_limit_observed: null
    write_mode_by_agent: {}
  conflicts: []
  open_questions: []
  validators_run: []
  gates: []
  completed_steps: []
  blocked_by: []
  next_recommended_command: ""
  next_action: ""
  resume_condition: ""
```
