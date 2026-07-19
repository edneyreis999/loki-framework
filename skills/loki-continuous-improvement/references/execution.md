# Execution — loki-continuous-improvement

## Purpose And Observable Contract

Este command é o orquestrador que transforma aprendizados validados em proposta
ou promoção duradoura rastreável para o projeto consumidor ou pacote Loki, ou os
mantém em backlog quando a evidência não sustenta normatização.

- Início: Input normalizado, retrospectiva elegível e fronteiras de escopo
  conhecidas.
- Conclusão: cada candidato tem fonte, classificação, root-cause decision,
  destino, ação, gates, validators, status e risco; todos os handoffs estão
  terminais e nenhuma stop condition permanece ativa.
- Resultado verificável: candidatos deduplicados, proposta before/after ou patch
  aprovado na superfície correta, artefatos impactados, evidências, checks e
  backlog justificado.
- Saídas obrigatórias: candidatos classificados, propostas estruturadas,
  artefatos/validations/gates, resumo de causa raiz quando exigido e backlog para
  evidência insuficiente.

## Execution Profile

```yaml
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
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response. Decomponha o fluxo em unidades com
responsáveis, selecione agentes, forneça contexto autocontido, acompanhe cada
handoff até sucesso, falha, bloqueio ou parada explícita, aplique validators,
gates e approvals e consolide candidatos, artefatos, evidências, riscos e
próximos passos. Delegação não transfere a responsabilidade pelo estado global.

## Dependencies

```yaml
required_skills:
  - lf-command-creator
  - lf-agent-creator
  - lf-skill-creator
required_commands:
  - loki-retrospectiva-tecnica
```

Use `loki-retrospectiva-tecnica` como fonte auditável. Carregue
`lf-command-creator` para command/template de command/orquestração,
`lf-agent-creator` para agent ou dúvida agent-skill-command e
`lf-skill-creator` para skill, layout e progressive disclosure.

## Allowed And Forbidden Writes

`allowed_writes` limita-se a Markdown transitório do plano ativo para candidato,
backlog, approval e diff proposto; e à superfície duradoura exata somente quando
a task autorizar, o destino tiver sido confirmado e `technical-review` mais
`approval` estiverem satisfeitos.

`forbidden_writes` inclui evidência transitória como destino final; qualquer
`AGENTS.md`, `CLAUDE.md`, command, skill, agent, template, validator, doc
consolidado ou `manifest.yaml` sem gates; `.claude/**` ou `.codex/**` sem
approval explícito de instalação/sincronização; `.agents/**`; runtime, engine,
framework ou superfície sensível fora do escopo e sem gate humano. Não amplie
silenciosamente os writes.

## Planning, Participants And Handoffs

Transforme o Input normalizado em plano com ingestão, evidência, classificação,
root-cause decision, destino, responsáveis, handoffs, validators, gates e
critérios. Replaneje explicitamente quando digest, conflito, causa raiz, gate ou
validator invalidar destino, owner ou etapa posterior.

Delegue análise, pesquisa, proposta, escrita e revisão ao agente responsável
sempre que possível:

- `retrospective-digester`, read-only, para diretório, múltiplas fontes ou
  retrospectiva longa/ruidosa;
- `standards-curator`, proposal-only, para escopo `universal`,
  `probable-universal`, `project-specific` ou `backlog`, destino e gate;
- `source-researcher`, read-only, para evidência multifonte, conflito,
  duplicidade, fonte de verdade e causa raiz;
- `bibliotecario`, read-only, para localizar documentação consumidora e evitar
  duplicidade, podendo ler em paralelo quando independente;
- `catalogador` para documentação project-specific, index e roteamento mínimo;
- os creators obrigatórios para propor/revisar os artefatos correspondentes;
- um Write Agent `scoped-writer` apropriado para qualquer alteração autorizada.

Para `destination_scope: package`, o Write Agent obrigatório é
`framework-artifact-writer` e, depois do patch real e dos checks mecânicos, o
revisor obrigatório é `framework-artifact-quality-auditor`. Eles não participam
de `consumer-context`, runtime, engine ou backlog; nesses destinos, preserve o
writer e auditor de domínio já aplicáveis.

Antes de selecionar essa ramificação, faça preflight do contexto ativo de
manutenção do pacote: confirme que os dois contratos internal-only estão
localmente disponíveis. O command `both` não depende deles para
`consumer-context`, runtime ou backlog. Se um candidato `package` for executado
sem essa disponibilidade, não use fallback genérico nem declare conclusão:
responda `blocked` com agentes ausentes, motivo e próximo destino
`orchestrator` para um contexto em que os artefatos internos de manutenção
estejam disponíveis ou para reclassificar o candidato; preserve os gates e não
converta o destino em consumidor por conveniência.

Antes de invocar subagente, entregue objetivo/motivo, unidade, fatos, decisões,
restrições, fontes/paths, dependências, escopo, allowed/forbidden writes, owner,
critérios de sucesso/falha/conclusão, validators, gates/approvals, output e
destino/condições do handoff. Não use “continue” ou contexto implícito. Registre
origem, destino, objetivo, entrada, resultado esperado, status, evidência e
próximo destino; acompanhe até terminal.

## Capability Preflight And Multi-Retrospective Digestion

Para diretório ou múltiplas retrospectivas:

1. Enumere arquivos elegíveis antes de carregar conteúdo completo.
2. Execute preflight explícito do adapter. Em Codex, faça descoberta dirigida de
   ferramentas multi-agent, subagent, delegation ou `retrospective-digester`;
   ferramentas podem estar diferidas, e a superfície inicial não prova ausência.
3. Trate namespaces descobertos como evidência da sessão, não contrato do pacote.
4. Faça fan-out read-only por arquivo ou lote pequeno de mesmo escopo quando o
   runtime permitir. Se não permitir após preflight, registre evidência concreta
   e use fallback serial com o mesmo schema.
5. Cada `retrospective_digest` retorna candidatos para docs, skills, commands,
   templates/validators, package policy e backlog, além de atritos, evidências,
   confiança e mínimo próximo caminho.
6. Consolide todos os digests antes de classificar. Deduplicate por fonte,
   destino, evidência, falha repetida, superfície preventiva e minimum next path.
7. Detecte conflito/evidência fraca antes de creators, curator ou catalogador.

Não carregue retrospectivas brutas inteiras na main thread quando o digest
bastar. Reabra somente por conflito, evidência fraca ou patch aprovado.

## Evidence And Execution-Friction Intake

Separe retrospectivas, interactions, builds, tasks, diffs e validações humanas
como evidência transitória, nunca destino normativo. Para erro observado,
normalize `Mistake Description`, `Expected Behavior`, `Actual Behavior`,
`Context`, `Suspected Cause`, `Execution Friction Category`, `Minimum Next Path`
e `Reuse Guidance`.

Preserve inferências úteis/incorretas, descobertas de arquivo, scripts/comandos,
resultado esperado/real, outputs inesperados, mismatches de ambiente, atritos de
ferramenta/validator/fonte/handoff/estado/dependência/formato/pesquisa externa,
correções humanas, desperdício de comunicação/busca/escopo, safety gates,
tentativas úteis/falhas, impacto estimado, avoid-next-time e caminho mínimo.
Não promova atrito diretamente: converta-o em regra, skill, validator,
preflight, doc ou backlog somente quando reutilizável e evidenciado.

Aceite `execution_knowledge_entry` schema v1 validada como `learning_source`
adicional. Confira source refs, capture ID, run/task/agent lineage,
materialidade, claim typing/confidence, gaps, sanitização e promotion status
`unreviewed`. Deduplicate por lineage/capture ID e preserve contradições. Uma
entry não substitui `retrospective_source`, root-cause learning, technical
review ou approval; capture nunca promove automaticamente.

## Classification And Placement Matrix

Classifique `type`, `severity` e `scope` de cada candidato. Prefira a menor
superfície duradoura que teria prevenido repetição:

| Aprendizado | Destino correto | Não usar como destino final |
| --- | --- | --- |
| Regra project-wide de roteamento | `AGENTS.md` com ponteiro mínimo | task, build, retrospectiva |
| Regra específica de adapter | `CLAUDE.md` ou equivalente | conversa bruta |
| Negócio, lore, fluxo, convenção ou arquitetura do consumidor | `docs/**/*.md` + `docs/index.xml` | pacote Loki |
| Procedimento técnico reutilizável | `skills/` | task/checklist isolada |
| Workflow invocável com estado/gates | command bundle | routing doc |
| Papel especialista com julgamento | `agents/` | command/task |
| Formato/contrato recorrente | `templates/` | task individual |
| Falha de validação, gate ou write policy | validator/gate/doc normativo | checklist local |
| Evidência insuficiente | backlog/record-only | superfície normativa |

Use `catalogador` para docs project-specific e atualize `docs/index.xml` na
mesma promoção. `AGENTS.md`/`CLAUDE.md` recebem apenas roteamento mínimo; detalhe
de negócio permanece em docs. Não coloque fatos do consumidor no pacote.

### Catalogador Caller/Mode Contract

Todo handoff ao `catalogador` envia explicitamente
`calling_workflow: loki-continuous-improvement` e
`write_mode: task_scoped_writer`. Somente esse
par e valido; caller/mode ausente, desconhecido ou cruzado falha antes da
primeira escrita no `failure_destination`.

Rejeite `init-bootstrap-cataloger`, `init-publication-batch` e
`init-final-reconciliation`. Packets, batches, ledger, bootstrap, coverage e
final reconciliation do init nunca sao inputs, precondicoes ou semantica deste
caller. Preserve o envelope nao-init existente com targets, consumer root,
allowed/forbidden writes, owner, approval, validators, gates e destinations.

Se `catalogador` estiver indisponivel, bloqueie pre-write. Nao use escrita
direta do orquestrador nem writer alternativo em consumer docs. Preserve
candidato e resume state com caller/mode, targets, approvals, validators,
gates, `blocked_by`, success/failure destinations e condicao de retomada.

## Root-Cause Learning Phase And Boundary

Todo candidato declara `root_cause_learning.required`. Marque `true` para erro
médio/alto com causa genérica/suspeita, falso positivo de audit/test/review,
fonte de verdade errada ou desatualizada, contrato mal entendido, padrão
repetido sem causa comum, fix apenas de sintoma, prevenção ampla possível ou
semântica surpreendente de ambiente/engine/ferramenta/formato/integração.

Quando `true`, antes de destino final, proposta ou escrita:

1. Defina pergunta, candidato, evidências, fora de escopo, fontes locais e gate
   externo.
2. Delegue a `source-researcher` toda investigação multifonte, conflito, source
   of truth, semântica surpreendente ou causa suspeita.
3. Delegue a `retrospective-digester` busca de padrão em fontes retrospectivas.
4. Use `standards-curator` para confirmar mudança de escopo/destino/gate e
   `catalogador` quando a causa project-specific virar docs, sempre com
   `calling_workflow: loki-continuous-improvement` e
   `write_mode: task_scoped_writer`.
5. Receba somente `source_research` e `retrospective_digest` estruturados com
   fontes, fatos, inferências, conflitos, lacunas, causa, regra preventiva e
   riscos. Reabra bruto apenas se o handoff exigir.
6. Atualize fontes verificadas, root cause, stronger prevention e riscos; só
   então escolha destino, diff e gates.

A main thread não faz pesquisa multifonte direta. Esta fase é read-only e não
autoriza internet. Se versão, documentação oficial atual, bug conhecido, API ou
compatibilidade forem materiais, pare em `research-consent` e apresente a frase
exata da busca ao usuário.

## Promotion Workflow

1. Classifique e deduplicate cada candidato após consolidar digests.
2. Aplique root-cause phase quando required; bloqueie ou registre risco se não
   puder concluí-la.
3. Confirme fonte reproduzível, escopo, target file/artifact, superfície que
   preveniria repetição, before/after, validators e gates.
4. Escolha `propose-patch`, `apply-approved-patch`, `record-only` ou
   `block-and-ask`.
5. Aplique `interview`, `technical-review`, `approval` e pesquisa consentida
   antes das ações dependentes.
6. Para `destination_scope: package`, entregue o envelope aprovado ao
   `framework-artifact-writer` somente após o preflight de manutenção interna;
   se falhar, bloqueie com retorno executável ao orquestrador. Quando passar,
   serialize os arquivos e execute validators e
   packaging checks. Em seguida entregue o patch real, baseline, arquivos
   descobertos, checks e iteração ao `framework-artifact-quality-auditor`.
   Somente `approved` sem finding/inconclusão é terminal. Finding corrigível
   dentro do envelope volta ao Writer, repete checks e exige nova auditoria.
   Ampliação material invalida gates e retorna à proposta, review e approval;
   `needs-human-review` é `blocked` e retorna ao `technical-review`, seguido
   obrigatoriamente de nova auditoria.
7. Para consumer docs project-specific, delegue exclusivamente ao `catalogador`
   com o par caller/mode fixo. Para outros destinos, delegue ao Write Agent
   apropriado e preserve seus gates e validators existentes.
8. Responda com candidatos, artefatos, evidência, handoffs, gates, riscos,
   backlog e resume state.

## Write Ownership And Named Writer Routing

Leituras independentes podem ser paralelas; nenhuma promoção, patch,
catalogação ou atualização escreve em paralelo. Atribua owner único por arquivo,
detecte overlap e serialize writes.

Antes de criar, modificar, mover ou remover, selecione Write Agent apropriado e
entregue target files, alteração, allowed/forbidden writes, validators, gates,
evidências e handoff. `consumer-docs-fallback: prohibited`: somente o
`catalogador` escreve consumer docs, e sua indisponibilidade bloqueia pre-write
sem escrita direta do orquestrador ou writer alternativo.

Para package, use exclusivamente `framework-artifact-writer`; para outro
destino nao-consumer, use o applicable-domain-writer nomeado pelo envelope.
Ausencia do writer exigido bloqueia ou retorna ao orquestrador para
reclassificacao/replanejamento; nunca converta o target para outra classe por
conveniencia, velocidade ou tamanho. Preserve target files, allowed/forbidden
writes, owner, validators, gates, evidências e destinations em qualquer rota.

Na ramificação `package`, `framework-artifact-writer` é owner exclusivo dos
`target_files` e sync files declarados; o auditor tem sandbox read-only e não
recebe permissão de escrita em produção. O Writer não pode autoatestar a própria
mudança. Finding retorna ao owner somente se não ampliar objetivo, destino,
target set ou semântica aprovada; caso contrário, invalide gates e replaneje.

## Validators

- Toda proposta cita fonte aceita/reproduzível, separa evidência transitória de
  destino duradouro e nomeia target concreto.
- Explica por que a superfície preveniria o erro ou reduziria repetição.
- Atrito preserva categoria, evidência, minimum path e redução esperada de
  tokens, ferramentas, buscas ou interações.
- Múltiplas fontes citam fan-out ou preflight que justificou fallback serial.
- Todo candidato declara root-cause required; quando true, inclui fontes, causa
  e regra fortalecida, ou blocker e risco residual.
- Proposta contém before/after ou diff esperado.
- Destino no pacote lista checks dos guardrails; destino consumer declara que é
  aplicação, não fonte normativa do pacote.
- Docs duradouros atualizam `docs/index.xml`; roteamento em AGENTS/CLAUDE é
  mínimo e detalhe fica em docs.
- Writers e handoffs têm envelope, owner, estado terminal e evidência.
- Handoff ao `catalogador` declara exatamente caller/mode deste workflow;
  init modes/payloads falham pre-write e indisponibilidade bloqueia sem
  fallback documental.
- Gate/approval requerido está satisfeito antes da escrita; validators passam
  antes de conclusão.
- Destino `package` tem Writer, checks mecânicos e parecer independente
  `approved`; auditor ausente, `blocked`, finding, inconclusão ou human review
  impede terminal.

## Human Gates

- `interview`: conflito de destino, ambiguidade de escopo ou generalização.
- `technical-review`: command, skill, agent, template, validator, manifest ou
  doc consolidado.
- `approval`: promoção normativa, política duradoura, instalação,
  sincronização de docs/index/AGENTS/CLAUDE ou escrita sensível.
- `research-consent`: fonte externa atual material, com query exata.

Validator automático não substitui gate humano. Pare se controle obrigatório
estiver ausente, pendente, rejeitado, falho ou inconclusivo.

## Packaging Checks

Classifique `command`, `skill`, `agent`, `template`, `doc`, `manifest`,
`standard`, `consumer-context` ou `backlog`. Declare pacote consolidado versus
contexto consumidor. Para pacote, leia e aplique
`docs/package-authoring-guardrails.md`, liste impacto em docs/manifest e
autocontenção. Para contexto consumidor, trate docs/index/AGENTS/CLAUDE apenas
como alvos aprovados e identifique maintainer, normalmente `catalogador`.

## Anti-Magic-Memory Rule

Nenhum aprendizado vira regra duradoura sem fonte, escopo, destino, verificação
e decisão registrada. Planos, tasks, interactions, builds e retrospectivas são
evidência, não destino. Promoção no pacote aponta artefato, regra de autoria e
validação final concretos.

## Continuous Improvement Candidate Schema

Preserve este schema em cada candidato:

```yaml
continuous_improvement_candidate:
  id: "ci-001"
  source:
    file: "retrospetivas/faseN/retrospectiva-faseN-<slug>.md"
    evidence: "Resumo curto do fato observado."
    execution_knowledge_refs: []
    evidence_lineage: []
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
    destination_scope: "package | consumer-context | runtime | backlog"
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
  promotion_execution:
    package_artifact_flow_required: "true | false"
    writer:
      agent: "framework-artifact-writer | applicable-domain-writer | none"
      envelope_status: "pending | valid | invalid"
      target_files: []
      discovered_target_files: []
      status: "pending | completed | blocked | failed | not-required"
      validator_evidence: []
    auditor:
      agent: "framework-artifact-quality-auditor | applicable-domain-auditor | none"
      required: "true | false"
      status: "pending | approved | blocked | not-required"
      internal_status: "pending | pass | finding | inconclusive | needs-human-review | not-required"
      findings: []
      residual_risks: []
    iteration: 0
    gates_invalidated: false
    next_destination: "writer | technical-review | orchestrator | none"
```

## Stop Conditions

Pare diante de required input ausente; fonte inelegível/insuficiente;
escopo/permissão insuficiente; destino ambíguo ou transitório; generalização de
caso isolado sem project-specific; tentativa de relaxar gate; regra consumidora
proposta para pacote; root-cause required incompleta e não bloqueada; dependência
indisponível; handoff sem destino; conflito de writers; validator ausente/falho;
gate/approval/decisão humana pendente; ou superfície sem validação verificável.
Pare tambem antes de consumer-doc write se `catalogador` estiver indisponivel,
caller/mode divergir ou o envelope exigir qualquer precondicao init.
Para `destination_scope: package`, pare também se o Writer ou auditor estiver
indisponível, se auditoria tiver finding/inconclusão/human review, se o auditor
tentar editar produção, ou se uma correção ampliar materialmente o envelope sem
invalidar e renovar os gates.
Não declare conclusão com condição ativa.

## Resume Contract

Registre por candidato fonte, digest/evidência, classificação, escopo, destino,
execution friction, `root_cause_learning`, ação, owner/writes, handoffs, gates,
validators, artefatos impactados, diff esperado, approval, status, risco,
etapas concluídas, próxima ação e condição de retomada. Preserve a evidência e
retome sem reiniciar quando esse estado bastar.

Para `destination_scope: package`, registre também `promotion_execution`: owner
e envelope do Writer, target/discovered files, evidência de checks, auditor e
seus estados interno/externo, findings, iteração, gates invalidados e próximo
destino. Após correção ou decisão humana, o estado volta a `auditor.pending`;
apenas uma nova auditoria `approved` permite conclusão.
Para consumer docs project-specific, registre caller/mode fixo, estado do
handoff ao `catalogador`, `blocked_by`, targets, destinations e condicao exata
de retomada; nunca substitua o writer.
# Evidence-first learning sources

Prefer validated retrospective outputs, evidence audits, completion records
and validated execution-knowledge entries as `learning_sources`. Deduplicate
candidates by evidence lineage/capture ID and keep
contradictions as conflicts for human/technical review. A transient evidence
source never directly promotes a durable rule, and raw runtime traces are not a
default input.
