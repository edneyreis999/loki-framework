---
name: loki:continuous-improvement
type: command
status: draft
domain: continuous-improvement
required_skills:
  - loki-retrospectiva-tecnica
  - lf-command-creator
  - lf-agent-creator
  - lf-skill-creator
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - durable package policy promotion
    - command, skill, agent, template, validator, or manifest changes
    - broad normative change with cross-adapter impact
  handoff_effort:
    research: high
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:continuous-improvement

## Purpose

Promover aprendizados validados para contexto duradouro do projeto ou do
pacote, melhorando as superficies que guiam a LLM ao longo de multiplos planos:
`AGENTS.md`, `CLAUDE.md`, `docs/**/*.md` do consumidor, `docs/index.xml`,
commands, skills, agents, templates, validators, docs normativos,
`manifest.yaml` ou backlog.

## Inputs

- Retrospectivas de fases concluidas ou pausadas claramente, ou de dificuldades reais resolvidas de fato.
- Arquivo unico de retrospectiva ou diretorio contendo multiplas retrospectivas tecnicas.
- Interactions com decisoes humanas, approvals, defaults e rejeicoes.
- Builds, validacoes humanas, tasks e diffs do plano executado como evidencia transitoria.
- Atritos de execucao da retrospectiva: inferencias uteis e incorretas, scripts/comandos, outputs inesperados, mismatches de ambiente, ferramentas, validadores, handoffs, estado local, desperdicios e caminho minimo recomendado.
- Superficie duradoura candidata: `AGENTS.md`, `CLAUDE.md`, `docs/**/*.md`,
  `docs/index.xml`, command, skill, agent, template, validator, doc normativo,
  `manifest.yaml` ou backlog.
- `docs/package-authoring-guardrails.md` quando o destino atingir componente consolidado do pacote.
- `docs/project-context-catalog.md` quando o destino puder ser documentacao do
  projeto consumidor.
- Quando a fonte for erro observado, normalize tambem:
  - `Mistake Description`
  - `Expected Behavior`
  - `Actual Behavior`
  - `Context`
  - `Suspected Cause`
  - `Execution Friction Category`
  - `Minimum Next Path`
  - `Reuse Guidance`

## Outputs

- Candidatos de melhoria classificados com destino duradouro explicito.
- Proposta de patch estruturada para a superficie normativa correta.
- Lista dos artefatos normativos impactados e das validacoes, gates e checks de empacotamento exigidos.
- Para candidatos marcados com `root_cause_learning.required: true`, resumo da fase extra de causa raiz antes da proposta final.
- Backlog quando a evidencia for insuficiente.

## Allowed Writes

- Markdown transitorio do plano ativo para registrar candidatos, backlog, approvals pendentes e diff proposto.
- Edicoes em superficie duradoura apenas quando a tarefa autorizar, o destino estiver correto e `technical-review` mais `approval` ja tiverem sido satisfeitos.

## Forbidden Writes

- Artefatos transitorios como destino final de regra duradoura.
- `AGENTS.md`, `CLAUDE.md`, commands, skills, agents, templates, validators, docs consolidados ou `manifest.yaml` sem gate exigido.
- `.claude/**` sem approval explicito de instalacao ou sincronizacao.
- `.codex/**` sem approval explicito de instalacao ou sincronizacao.
- `.agents/**`
- Runtime, engine, framework ou superficies sensiveis do consumidor fora do escopo aprovado e sem gate humano.

## Required Skills

- `loki-retrospectiva-tecnica` para ler retrospectivas como fonte auditavel de aprendizado.
- `lf-command-creator` quando o destino duradouro for command, template de command ou contrato de orquestracao.
- `lf-agent-creator` quando o destino duradouro for agent ou quando houver duvida entre agent, skill e command.
- `lf-skill-creator` quando o destino duradouro for skill, layout de skill ou contrato de trigger/progressive disclosure.

## Handoffs

- `standards-curator` em modo `proposal-only` para classificar o aprendizado como `universal`, `probable-universal`, `project-specific` ou `backlog`, recomendar destino e gate.
- `retrospective-digester` em modo read-only quando a entrada for um diretorio, multiplas retrospectivas independentes, ou uma retrospectiva longa/ruidosa. Antes de decidir fallback serial, executar preflight de capacidade do adaptador; em Codex, usar descoberta direcionada de ferramentas para multi-agent, subagent, delegation ou `retrospective-digester`, porque ferramentas podem estar diferidas e ausentes da superficie inicial. Usar fan-out por arquivo quando o runtime permitir; cada instancia retorna digest estruturado para o orquestrador.
- `source-researcher` em modo read-only quando a evidencia de um candidato
  precisar ser conferida em varias fontes, houver conflito de origem, risco de
  duplicidade, necessidade de distinguir fato local de referencia externa, ou
  `root_cause_learning.required` for `true`. A main thread nao faz pesquisa
  multi-fonte direta nesse caso: ela formula perguntas, escopo, fontes
  permitidas e gate externo, entao recebe apenas o handoff estruturado
  `source_research`.
- `catalogador` quando o aprendizado for `project-specific` e pertencer a
  `docs/**/*.md`, `docs/index.xml`, `AGENTS.md` ou `CLAUDE.md` do consumidor.
- `bibliotecario` quando for necessario revisar a documentacao duradoura do
  consumidor com baixo custo antes de evitar duplicidade. Pode rodar em paralelo
  com leitura de evidencias quando a pergunta documental for independente; o
  retorno deve ser consolidado antes de qualquer decisao de promocao.

## Multi-Retrospective Intake

Quando a entrada for um diretorio ou lista de retrospectivas:

1. Enumerar arquivos elegiveis de retrospectiva tecnica antes de carregar
   conteudo completo no contexto principal.
2. Executar preflight explicito de capacidade antes de escolher o modo de
   ingestao:
   - em Codex, chamar descoberta direcionada de ferramentas para
     multi-agent/subagent/delegation/`retrospective-digester`;
   - tratar namespaces descobertos como evidencia da sessao/adaptador, nao como
     contrato universal do pacote;
   - nao declarar fan-out indisponivel apenas porque a lista inicial de
     ferramentas nao mostrou subagentes;
   - registrar a evidencia concreta quando o fallback serial for necessario.
3. Criar um handoff read-only independente para `retrospective-digester` por
   arquivo, ou por lote pequeno quando os arquivos forem curtos e do mesmo
   escopo.
4. Cada digest deve retornar candidatos para `/docs`, skills, commands,
   templates, validators, package policy e backlog, alem de atritos de execucao,
   evidencias, confianca e caminho minimo recomendado.
5. Rodar handoffs em paralelo quando o ambiente permitir. Se o preflight
   confirmar que o runtime nao suporta subagentes ou fan-out, processar
   serialmente usando o mesmo formato de digest e citar a evidencia no output.
6. Consolidar todos os `retrospective_digest` no contexto principal antes de
   classificar promocao duradoura.
7. Deduplicar aprendizados por fonte, destino provavel, evidencia e superficie
   que teria prevenido repeticao.
8. Detectar conflitos e evidencia fraca antes de chamar `standards-curator`,
   `catalogador`, `lf-skill-creator`, `lf-command-creator` ou
   `lf-agent-creator`.
9. Marcar `root_cause_learning.required` por candidato. Quando for `true`,
   executar a fase read-only de causa raiz por handoff antes de fechar destino,
   proposta ou patch. A main thread nao deve carregar fontes brutas extensas
   para essa fase; use `source-researcher` e, quando houver lote de
   retrospectivas, `retrospective-digester`.
10. Nao escrever em paralelo. Toda promocao, patch, catalogacao ou atualizacao de
   skill/command/template/validator acontece serialmente pelo orquestrador apos
   gates.

Nao jogue retrospectivas brutas inteiras no contexto principal quando um digest
estruturado bastar. Reabra a retrospectiva completa apenas para resolver
conflito, conferir evidencia fraca ou preparar patch aprovado.

## Root-Cause Learning Phase

Depois da classificacao inicial, todo candidato deve declarar se merece uma
rodada extra de causa raiz antes da proposta final.

Marque `root_cause_learning.required: true` quando pelo menos um destes sinais
aparecer:

- erro de severidade media ou alta com causa ainda generica ou apenas suspeita;
- audit, validator, teste ou revisao passou falsamente;
- a falha veio de fonte de verdade errada, spec desatualizada, memoria do agente
  ou contrato tecnico mal entendido;
- ha chance clara de transformar o aprendizado em regra mais forte descobrindo
  a fonte de verdade;
- o mesmo padrao aparece em varias retrospectivas, mas a causa comum ainda nao
  foi isolada;
- a proposta atual previne apenas o sintoma, nao a classe de erro;
- ambiente, engine, ferramenta, formato ou integracao teve semantica
  surpreendente.

Quando `root_cause_learning.required` for `true`:

1. Rodar uma fase read-only por handoff antes de promover ou escrever qualquer
   superficie duradoura.
2. Usar `source-researcher` como agente responsavel pela pesquisa de causa raiz:
   localizar fonte de verdade, conflitos, contratos tecnicos e evidencias
   independentes.
3. Usar `retrospective-digester` para procurar ocorrencias relacionadas em
   retrospectivas proximas quando houver lote ou catalogo.
4. Usar `standards-curator` para confirmar se a causa raiz muda escopo, destino
   ou gate.
5. Usar `catalogador` quando a causa raiz for project-specific e precisar virar
   documentacao do consumidor.
6. Atualizar o candidato com fontes verificadas, causa raiz, regra preventiva
   fortalecida e riscos residuais.
7. So entao escolher destino final, diff proposto e gates.

Essa fase nao autoriza internet automaticamente. Se a causa depender de versao,
documentacao oficial atual, bug conhecido, API externa ou compatibilidade, pare
e solicite consentimento de pesquisa externa com a frase exata da busca.

### Root-Cause Handoff Boundary

A main thread deve manter esta fase compacta:

1. Definir a pergunta de pesquisa, candidato, evidencias conhecidas, fora de
   escopo, fontes locais permitidas e status do gate externo.
2. Despachar `source-researcher` em modo read-only para qualquer pesquisa
   multi-fonte, conflito de fonte, fonte de verdade errada, semantica tecnica
   surpreendente ou causa ainda suspeita.
3. Despachar `retrospective-digester` em modo read-only quando a causa comum
   depender de buscar padroes em retrospectivas longas ou multiplas fontes
   retrospectivas.
4. Receber e consolidar somente retornos estruturados (`source_research` e
   `retrospective_digest`), com fontes, fatos, inferencias, conflitos, lacunas,
   causa raiz proposta, regra preventiva e riscos residuais.
5. Reabrir fontes brutas na main thread apenas quando o handoff indicar
   conflito, evidencia fraca, trecho indispensavel para patch aprovado ou
   stop condition.
6. Nao transformar pesquisa externa em padrao automatico. Se `source-researcher`
   indicar que fonte externa atual e material, parar para `research-consent`.

## Placement Matrix

| Aprendizado observado | Destino duradouro correto | Nao usar como destino final |
| --- | --- | --- |
| Regra project-wide que deve guiar toda LLM do projeto consumidor | `AGENTS.md` | `tasks.md`, `task-N.M.md`, `interaction/`, `builds/`, retrospectiva |
| Regra especifica de Claude Code, Codex ou adaptador equivalente | `CLAUDE.md` ou artefato equivalente de contexto duradouro do consumidor | `tasks.md`, `interaction/`, conversa bruta |
| Regra de negocio, lore, fluxo funcional ou convencao especifica do software consumidor | `docs/**/*.md` + `docs/index.xml`; `AGENTS.md` ou `CLAUDE.md` recebem apenas ponteiro minimo se necessario | pacote Loki, task ou retrospectiva isolada |
| Procedimento tecnico reutilizavel | `skills/` | `AGENTS.md`, task ou checklist solta |
| Workflow invocavel com estado, gates e outputs | `commands/` | `AGENTS.md`, retrospectiva |
| Papel especialista com julgamento proprio | `agents/` | `commands/`, task local |
| Lacuna recorrente de formato ou contrato | `templates/` | task individual |
| Falha de validator, gate ou politica de escrita | validator, gate doc ou doc normativo do pacote | checklist local sem promocao |
| Regra ainda sem evidencia suficiente | backlog | qualquer superficie normativa |

## Validators

- Toda proposta cita pelo menos uma fonte aceita e reproduzivel.
- O candidato separa claramente evidencia transitoria de destino duradouro.
- O destino proposto e concreto: arquivo, artefato ou categoria instalavel especifica.
- A proposta explica por que a superficie escolhida teria prevenido o erro ou reduzido a repeticao.
- Quando a fonte incluir atrito de execucao, a proposta preserva categoria, evidencia, caminho minimo e como a superficie proposta reduziria tokens, ferramentas, buscas ou interacoes futuras.
- Quando a entrada for diretorio ou multiplas retrospectivas, a proposta cita a
  evidencia de fan-out usado ou o preflight concreto que justificou fallback
  serial.
- Todo candidato declara `root_cause_learning.required`. Quando for `true`, a
  proposta inclui fontes checadas, causa raiz e regra preventiva fortalecida,
  ou registra explicitamente por que a fase ficou bloqueada.
- A proposta inclui comparacao `before/after` ou diff esperado para a superficie normativa.
- Se o destino tocar o pacote, os checks de `docs/package-authoring-guardrails.md` aparecem explicitamente.
- Se o destino tocar `docs/**/*.md`, `docs/index.xml`, `AGENTS.md` ou
  `CLAUDE.md` do consumidor, a proposta declara que esses arquivos sao destino
  de aplicacao, nao fonte normativa do pacote.
- Se a proposta criar ou mudar documentacao duradoura do consumidor, ela
  atualiza `docs/index.xml` na mesma promocao.
- Se a proposta tocar `AGENTS.md` ou `CLAUDE.md` do consumidor, o conteudo e de
  roteamento minimo; a regra de negocio detalhada continua em `/docs`.

## Human Gates

- `interview` quando houver conflito de destino, ambiguidade de escopo ou duvida de generalizacao.
- `technical-review` quando o candidato alterar command, skill, agent, template, validator, `manifest.yaml` ou doc consolidado.
- `approval` para promocao normativa, mudanca de politica duradoura,
  instalacao, sincronizacao para `docs/**/*.md`, `docs/index.xml`, `AGENTS.md`
  ou `CLAUDE.md`, ou qualquer escrita sensivel.

## Packaging Checks

- Classificar a mudanca como `command`, `skill`, `agent`, `template`, `doc`,
  `manifest`, `standard`, `consumer-context` ou `backlog`.
- Declarar se o destino final e componente consolidado do pacote ou contexto duradouro do projeto consumidor.
- Se o destino for o pacote, listar impacto em docs, `manifest.yaml` e autocontencao.
- Se o destino for `docs/**/*.md`, `docs/index.xml`, `AGENTS.md` ou
  `CLAUDE.md` do consumidor, tratar esses arquivos como alvo de aplicacao
  aprovado, nunca como fonte normativa do pacote.
- Quando o destino for documentacao do consumidor, declarar qual agente fara a
  manutencao: normalmente `catalogador`.

## Anti-Magic-Memory Rule

Nenhum aprendizado vira regra duradoura sem fonte, escopo, destino, verificacao e decisao registrada.

Planos, tasks, interactions, builds e retrospectivas podem fornecer evidencia, mas nao sao o destino final de contexto duradouro.

Se o destino for o proprio pacote, o candidato deve apontar artefato concreto de promocao, regra de autoria aplicavel e validacao final esperada.

## Continuous Improvement Candidate Format

```yaml
continuous_improvement_candidate:
  id: "ci-001"
  source:
    file: "retrospetivas/faseN/retrospectiva-faseN-<slug>.md"
    evidence: "Resumo curto do fato observado."
  mistake:
    description: ""
    expected_behavior: ""
    actual_behavior: ""
    context: ""
    suspected_cause: ""
  execution_friction:
    categories:
      - "inference-good | inference-bad | file-discovery | script-command | unexpected-output | environment-mismatch | tool-friction | validation-friction | source-friction | handoff-friction | state-friction | dependency-friction | format-friction | external-research-friction | user-correction | communication-waste | search-waste | scope-waste | safety-gate-friction | minimum-next-path"
    observed_sequence: ""
    useful_attempts: []
    failed_attempts: []
    scripts_or_commands:
      - command: ""
        purpose: ""
        expected_result: ""
        actual_result: ""
        reuse_guidance: ""
    environment_mismatch: ""
    minimum_next_path: []
    avoid_next_time: []
    estimated_waste_impact: "low | medium | high"
  retrospective_digests:
    - source_file: ""
      digest_confidence: "low | medium | high"
      candidate_counts:
        project_docs: 0
        skills: 0
        commands: 0
        templates_or_validators: 0
        package_policy: 0
        backlog: 0
  classification:
    type: "factual-error | misunderstanding | missing-context | ambiguous-instruction | validation-gap | workflow-gap | execution-friction | environment-friction | tool-waste | prompt-gap"
    severity: "low | medium | high"
    scope: "universal | probable-universal | project-specific | backlog"
  root_cause_learning:
    required: "true | false"
    reason: ""
    triggers:
      - "false-positive-validation | wrong-source-of-truth | repeated-pattern | symptom-only-fix | surprising-engine-semantics | weak-suspected-cause | broad-prevention-potential"
    research_questions: []
    automatic_phase:
      status: "not-needed | pending | completed | blocked"
      handoffs:
        - "source-researcher | retrospective-digester | standards-curator | catalogador"
      sources_checked: []
      findings_summary: ""
      root_cause: ""
      stronger_prevention_rule: ""
      residual_unknowns: []
  context_gap:
    missing_information: ""
    ambiguity: ""
    why_this_surface_would_prevent_repeat: ""
  destination:
    artifact_type: "AGENTS.md | CLAUDE.md | project-doc | project-doc-index | command | skill | agent | template | validator | doc | manifest | backlog"
    target_file: ""
    sync_files: []
    delegate: "catalogador | bibliotecario | none"
  action: "propose-patch | apply-approved-patch | record-only | block-and-ask"
  proposed_change:
    summary: ""
    before: ""
    after: ""
  required_gates:
    - "technical-review"
    - "approval"
  verification:
    - "diff revisado"
    - "validacao de estrutura"
  residual_risk: []
```

## Stop Conditions

- Evidencia insuficiente.
- Destino ambiguo.
- O destino correto e um artefato transitorio do plano, nao uma superficie duradoura.
- A proposta tenta generalizar um caso isolado sem marcar `project-specific`.
- Mudanca proposta relaxa gate de seguranca.
- A proposta nao identifica o artefato normativo correto ou termina sem validacao verificavel.
- A proposta tenta colocar regra de negocio do consumidor dentro do pacote Loki.
- `root_cause_learning.required` esta `true`, mas a fase extra nao foi
  concluida nem registrada como bloqueada com risco residual.

## Resume Contract

Cada candidato deve declarar fonte, classificacao, escopo, destino,
`root_cause_learning`, acao, gate, validadores, artefatos impactados, diff
esperado, status de approval e risco residual.
