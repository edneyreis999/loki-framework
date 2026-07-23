# Execution — loki-continuous-improvement

## Purpose And Observable Contract

Este command é o orquestrador que transforma aprendizados validados em proposta
ou promoção duradoura rastreável para o projeto consumidor ou pacote Loki, ou os
mantém em backlog quando a evidência não sustenta normatização.

- Início: Input normalizado, pelo menos uma fonte elegível e fronteiras de
  escopo conhecidas.
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
  - lf-documentation-writing
required_commands: []
```

`loki-retrospectiva-tecnica` não é dependência deste workflow. Ele pode ser
usado opcionalmente para produzir um `retrospective_source` quando essa fonte
for desejada e sua criação estiver autorizada; uma `learning_source` ou
`analytic_inference_source` elegível não exige retrospectiva adicional. Carregue
`lf-command-creator` para command/template de command/orquestração,
`lf-agent-creator` para agent ou dúvida agent-skill-command e
`lf-skill-creator` para skill, layout e progressive disclosure.
Carregue `lf-documentation-writing` somente na ramificação package para
classificar aplicabilidade LLM-facing e rotear seu contrato canônico.
Quando o Input contiver eventos ou candidatos especializados de inferência,
carregue também [lf-analytic-inference](../../lf-analytic-inference/SKILL.md) e
seus contratos; não carregue essa skill para melhoria contínua não relacionada.

## Allowed And Forbidden Writes

`allowed_writes` limita-se a Markdown transitório do plano ativo para candidato,
backlog, approval e diff proposto; e à superfície duradoura exata somente quando
a task autorizar, o destino tiver sido confirmado e o approval aplicável estiver
satisfeito. Para `destination_scope: package`, a sequência obrigatória é
envelope aprovado quando aplicável, um `framework-artifact-writer`, checks
determinísticos e um `framework-artifact-quality-auditor` independente.

`forbidden_writes` inclui evidência transitória como destino final; qualquer
`AGENTS.md`, `CLAUDE.md`, command, skill, agent, template, validator, doc
consolidado ou `manifest.yaml` sem gates; `.claude/**` ou `.codex/**` sem
approval explícito de instalação/sincronização; `.agents/**`; runtime, engine,
framework ou superfície sensível fora do escopo e sem gate humano. Não amplie
silenciosamente os writes.

Keep roots and owners disjoint. `package_root` bounds reusable package
contracts, schemas, scripts, policy and package docs; the internal
`consumer_root`, resolved from canonical `pwd`, bounds only
`destination_scope: consumer-operational-state` at the fixed derived state
root `<consumer_root>/.loki/analytic-inference/v2`. Its active live locators are
`registry.xml`, `catalogs/<technology>/index.xml`, revisioned `rev-N.xml`
records and `.xml` events. Package writes belong
to `framework-artifact-writer`, which is forbidden from `.loki/**`. Consumer
state writes belong exclusively to one `technical-implementer` in
`task_scoped_writer` mode with canonical root, exact targets, validators and
gates; that envelope forbids package commands, contracts and docs. Consumer
docs remain a third surface owned by `catalogador` and never include `.loki`.
Only the XML v2 layout is a catalog source; JSON is never an active lookup
fallback or mutation destination.
Serialize every shared file under one owner and reject overlapping envelopes.

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
entry satisfaz o requisito mínimo de fonte quando elegível, mas não substitui
root-cause learning, approval ou validators; capture nunca promove
automaticamente.

## Conditional Analytic-Inference Intake And Reconciliation

Ative esta ramificação somente quando uma fonte persistida contiver relatório
de deep analysis com `inference_events` e/ou `generated_candidates`, ou
retrospectiva com `analytic_inference_candidates`. Ela adapta os itens ao
lifecycle existente; não cria outro workflow de promoção nem altera candidatos
genéricos.

### Source and item validation

1. Resolva o locator dentro do escopo de leitura e registre tipo da fonte,
   locator canônico, digest canônico da fonte e blocos encontrados. Locator
   ausente, ilegível, fora do escopo ou incompatível com provenance bloqueia o
   intake afetado; nunca invente substituto.
2. Para cada `inference_event`, valide integralmente schema v1, `event_id`,
   `source.analysis_ref`, run/handoff/evidence refs, inference ID/revision,
   stage, outcome, reason, capability e custos. `analysis_ref` deve identificar
   a fonte persistida ou ter lineage observável até ela.
3. Para cada `generated_candidate`, exija schema v1, stable `candidate_id`,
   `origin: generated`, status exatamente `unreviewed`, statement, demand
   relation, applicability, provenance com `generated_in_report`, evidence
   refs/freshness, investigation, distinction e downstream sem autorização de
   mutação.
4. Para cada `analytic_inference_candidate`, exija schema v1, stable
   `candidate_id`, `candidate_type: analytic-inference`, observation type
   reconhecido, status exatamente `unreviewed`, `capture_id`, locator da
   retrospectiva, lineage, applicability, provenance, classificação da
   evidência, validation, investigation, distinction, guidance e downstream
   sem autorização de mutação. Capture e locator são obrigatórios; valores
   `unavailable` permanecem explícitos.
5. Preserve facts, inferences e hypotheses separados. Contradição, schema
   inválido, provenance quebrada, status diferente de `unreviewed` ou pedido de
   mutação na fonte resulta em `block`; lista vazia é válida somente com motivo.

### Stable intake identity, replay and conflicts

Produza ledger transitório determinístico. A identidade é o par tipado
`event:<event_id>` ou `candidate:<candidate_id>`; registre locator da fonte,
digest da fonte, digest SHA-256 do payload JSON canônico e lineage/capture
observados. Os namespaces são distintos. O payload canônico usa UTF-8, chaves
ordenadas e separadores compactos, sem campos inventados.

- Primeiro ID/payload válido: `accepted`.
- Mesmo ID e payload canônico idêntico: `replayed-no-op`; não incremente
  contador, denominador, evidência ou candidato.
- Mesmo ID e payload divergente: `conflict-blocked`; preserve as duas
  provenances e não escolha vencedor.
- Deduplicate eventos globalmente por `event_id` e candidatos por
  `candidate_id`. Capture ID e locator auditam a origem, mas não substituem as
  chaves de idempotência.
- Retry parcial reabre o ledger e converge ao mesmo conjunto aceito. Nunca
  conte novamente item já aceito.

Similaridade semântica pode gerar `near-duplicate-review`, mas nunca equivale a
identidade, deduplicação exata, merge, redirect, reorganização ou remoção.

### Deterministic reconciliation and policy

Para cada inference ID/revision catalogada, combine somente eventos aceitos com
o ledger histórico e execute o reducer stdlib
`../../lf-analytic-inference/scripts/reconcile_events.py <events.json>
--policy ../../lf-analytic-inference/references/policy-v1.json`, acrescentando
`--protected` quando o registro validado tiver status `protected`. A entrada é
JSON array ou objeto com `events`; o reducer retorna JSON read-only e
`mutation_applied: false`. Exit diferente de zero ou status `blocked` bloqueia
a proposta afetada.

Reconstrua e exponha os nove componentes, inclusive `rejected_count`,
`denominators.unique_events`, `as_of_event`, freshness, score,
algorithm/policy, `applied_event_ids`, `replayed_event_ids` e diagnostics. Não
confie em contador mutável observado.

Valide o catálogo antes e depois do diff proposto com
`../../lf-analytic-inference/scripts/validate_catalog.py
--policy ../../lf-analytic-inference/references/policy-v1.json`, executado com
`cwd` igual à raiz do consumidor. Exija schema,
IDs, locators contidos, revisions, lineage acíclica, paridade exata índice ↔
registro, `active_limit` compatível e policy ID
`analytic-inference-policy-v1` com digest exato
`7d5ec8247b28c831bc705593e193f12707309839b3a745d424efa84bc6f05fc7`.
Snapshot observado que divergir da reconstrução é inválido.

O score usa apenas pesos aprovados: investigated `1`, validated `3`, material
finding `5`, task helped `8`, false positive `-6`, repeated evidence `-4`,
stale `-2` e selected `0`. Compare inclusivamente e reporte somente:

- `promotion_eligible: score >= 12`;
- `reorganization_eligible: score <= 2`;
- `purge_review_eligible: status != protected and score <= -4`.

Esses booleans são elegibilidade, não decisão. Seleção nunca melhora o score e
registro protegido nunca é purge-review eligible. Eles apenas permitem avaliar
os contratos gated de reorganização e purge abaixo; não autorizam ação,
equivalência por similaridade ou mutação automática.

### Candidate disposition and promotion-only proposal

Mapeie cada candidato especializado ao schema existente, preservando um bloco
`analytic_inference` com source type, intake identity, payload digest,
capture/lineage/provenance, reconstrução, score e elegibilidade. Escolha uma
disposição:

- `record-only`: evidência insuficiente, não elegível ou investigação futura;
- `block`: conflito, schema/locator/lineage/provenance/policy inválido ou gate
  material ausente;
- `propose-promotion`: evidência e elegibilidade sustentam somente proposta.

O status permanece `unreviewed` em todas as três disposições. Só aplicação
duradoura posterior, com todos os gates e validators resolvidos, pode mudar o
lifecycle. Nunca trate score, replay, relatório, retrospectiva ou similaridade
como aprovação.

Proposta de promoção usa `destination_scope: consumer-operational-state` e
lista targets exatos de registry/índice/registro/eventos, before/after,
eventos e snapshot esperados, lineage/provenance, dry validation e riscos. Para
qualquer aplicação, exija approval vinculada à operação/root/targets/digests;
depois, `technical-implementer` é o único state writer. O package writer nunca
recebe esses targets. Sem esse controle, esta etapa registra somente
proposta/dry-run root-bound:
`catalog_mutation_applied: false`.

### Reorganization proposal contract

Somente estado reconstruído com `reorganization_eligible: true` (`score <= 2`)
pode originar proposta; elegibilidade é necessária e não executa ação. A
proposta declara operation ID, inference IDs/revisions, targets exatos,
before/after por target, lineage antes/depois, evidência validada preservada,
motivo, risco e validators determinísticos. Preserve registros `protected` e
todo conhecimento validado; perda, ambiguidade ou lineage irresolúvel bloqueia.

Operações permitidas na proposta são `generalize`, `merge`, `deduplicate`,
`rewrite` e `reorder`. Similaridade semântica é somente sinal para review,
nunca identidade, igualdade ou autorização de merge/deduplication. Antes de
qualquer aplicação, exija approval vinculada à proposta, consumer root, targets
e digests; então serialize os targets sob owner único
`technical-implementer`, rode validação determinística de schema,
identidade, lineage, paridade e snapshot. O state writer não escreve contratos
do pacote e nenhum parecer substitui os gates. Sem todos os controles, registre
somente `reorganization_proposed: true` e `catalog_mutation_applied: false`.
Projete sempre estados separados: `reorganization_eligible` é informativo;
`reorganization_proposed` registra somente a proposta gated;
`reorganization_applied` só pode ser `true` após aplicação e validação completas.
`catalog_mutation_applied` reflete o efeito real e permanece `false` em
eligibility ou proposal.

For approved promotion or reorganization, prepare immutable revisions/events,
validate the complete proposed state, and publish the technology index last as
the commit point. Bootstrap, when required, stages inside the same consumer
state root and publishes the registry last. Immediately before each write,
revalidate canonical root identity, `lstat` ancestors, containment, hashes and
approval binding. Failure before commit preserves prior visible state and lists
staging residue; failure after commit blocks for audit, enumerates observed
residue, and never claims rollback. Identical replay is a no-op; divergent
identity collision blocks.

### Physical purge contract

This command is limited to deterministic, zero-write purge proposal and dry-run.
Physical purge is reserved to a separate physical-purge workflow and MUST NOT be executed by this command,
even when a JIT approval is present. Record the exact approval requirements for
that future workflow, but keep `catalog_mutation_applied: false`, execution
`not-run`, and never claim runtime validation or deletion.

`purge_review_eligible: true` exige registro não protegido e score reconstruído
`<= -4`, mas é apenas condição necessária. Purge é físico, irreversível,
catalog-owned, sem rollback e falha fechado. Nunca use limite, score,
similaridade, proposal approval ou policy approval como approval da operação.

#### Read-only dry-run and canonical target manifest

Antes de solicitar approval, um dry-run read-only resolve o consumer root e o
state root fixo e cria
um manifesto canônico sem remover nada. O manifesto contém:

- stable `operation_id`, sequence monotônica, `generated_at` determinístico,
  inference IDs/revisions exatos e consumer/state roots canônicos;
- para **todos** os rastros catalog-owned desses IDs: artifact kind,
  canonical contained catalog path, selector quando o rastro estiver embutido
  e SHA-256 do estado anterior;
- record, index entry, snapshot, eventos, aliases, redirects, tombstones e todo
  identificador controlado pelo catálogo, inclusive referências cruzadas;
- exclusões explícitas e refs externas com hashes de preservação, incluindo
  relatórios, retrospectivas, evidências e o próprio approval record;
- policy ID/digest exatos, `removals_per_cycle`, target count e digest SHA-256
  do manifesto canônico completo sem o próprio campo de digest.

Normalize paths fisicamente, resolva symlinks e exija que cada target permaneça
sob o state root aprovado. Path absoluto na fonte, escape, symlink para fora,
artifact kind sem target, rastro catalog-owned omitido, hash ausente ou external
ref incluída como target bloqueia o dry-run. O dry-run retorna sempre
`mutation_applied: false`.

#### Independent just-in-time approval

Cada operação exige approval separado, não reutilizável, emitido depois do
dry-run. O registro deve vincular exatamente `operation_id`, inference IDs,
canonical paths, target-set/dry-run digest, policy digest, approver identity,
source locator, status explícito `approved` e expiry ou freshness verificável.
Approval ausente, pending/rejected, expirado/stale, já consumido, emitido antes
do dry-run, de outra operação, ou com qualquer divergência de ID/path/target
set/digest/policy bloqueia sem escrita. Fixture e exemplo nunca constituem
approval real.

#### Future separate physical-purge workflow pre-delete and failure contract

Nesse workflow futuro separado, imediatamente antes da primeira exclusão,
reconstrua score/eligibility e
revalide atomicamente: registro não protegido; identity/revision; canonical
containment e ausência de symlink escape; conjunto completo e sem target extra;
before hashes; dry-run/target-set e policy digests; approval JIT íntegro;
`active_limit`; e `removals_per_cycle: 1`. Drift ou mais de um ID no ciclo
bloqueia antes da escrita.

No future physical-purge envelope, only `technical-implementer` may own exact
consumer-state targets; `framework-artifact-writer` remains forbidden from
`.loki`. This command emits no such execution envelope and performs no delete.

Nesse workflow separado, qualquer interrupção depois da primeira exclusão é
`failed` e `blocked`:
registre targets removidos, rastros residuais, hashes observados, writes
tentados e minimum next path. Nunca declare rollback, sucesso, ausência total
de rastros ou aprovação reutilizável depois de falha parcial.

#### Post-validation

Após o dry-run, valide integridade do catálogo observado, completude dos
selectors/targets/hashes, hashes das referências externas e ausência de write.
O dry-run completo pode ser terminal apenas como proposta, nunca como purge
aplicado. Não reporte ausência de rastros: nenhuma exclusão ocorre nesta task.

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
5. Aplique `interview`, `approval` e pesquisa consentida antes das ações
   dependentes. Para destino `package`, siga exclusivamente a sequência
   concreta Writer/checks/Auditor descrita neste contrato.
6. Para `destination_scope: package`, entregue o envelope aprovado ao
   `framework-artifact-writer` somente após o preflight de manutenção interna;
   se falhar, bloqueie com retorno executável ao orquestrador. Quando passar,
   classifique o artefato com `lf-documentation-writing`. O Writer deve emitir
   `llm_artifact_profile` completo e particionar os dez fixture IDs canônicos
   exatamente uma vez entre selecionados e skips justificados. Se a
   classificação for positiva, carregue o
   [contrato canônico de qualidade LLM-facing](../../lf-documentation-writing/references/llm-artifact-quality-validation.md),
   aplique seus critérios de autoria, serialize os arquivos e execute somente
   validators mecânicos e packaging checks. Se for human-only, preserve profile
   completo com `not-applicable` justificado e os dez skips; não execute
   fixtures irrelevantes. Para human-only, registre
   `second_family_calibration: not-run` e uma
   limitation explícita de que revisão isolada e segunda família não são
   requeridas pela classificação validada. O parecer independente human-only
   usa internal `not-applicable`, external `approved`, `block_reason: none` e
   `llm_consumption_quality.status: not-applicable`; os gates existentes
   continuam obrigatórios. Em seguida entregue patch real,
   baseline, arquivos descobertos, profile, checks, evidência e iteração ao
   `framework-artifact-quality-auditor`.
   O Auditor read-only valida o profile e emite `llm_consumption_quality`
   completo com `llm-artifact-quality-v1`, `rubric-v2` e `prompt-v2`. Para
   aplicável, ele executa nove heurísticas, fixtures selecionados em ao menos uma
   revisão isolada e bias controls antes do status. Somente `approved` sem
   finding, inconclusão, baixa confiança material, fixture aplicável omitido,
   skip injustificado ou bias check falho é terminal. Conflito normativo gera
   internal `needs-human-review`, external `blocked` e
   `block_reason: human_review_required`. Finding corrigível
   dentro do envelope volta ao Writer, repete checks e exige replay completo da
   auditoria.
   Ampliação material invalida controles e retorna à proposta e ao approval
   aplicável; `needs-human-review` é `blocked` e retorna ao `orchestrator` para
   uma decisão humana específica, seguido obrigatoriamente de nova auditoria.
7. Para consumer docs project-specific, delegue exclusivamente ao `catalogador`
   com o par caller/mode fixo. Para outros destinos, delegue ao Write Agent
   apropriado e preserve seus gates e validators existentes.
8. Responda com candidatos, artefatos, evidência, handoffs, gates, riscos,
   backlog e resume state.

O gate LLM-facing acima existe somente em `destination_scope: package`. Para
`consumer-context`, `consumer-operational-state`, runtime, inference e backlog,
preserve routing, owners, validators, gates e terminal states existentes; não
carregue o contrato, não execute seus fixtures e mantenha
`llm_artifact_quality: null`.

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

Para `consumer-operational-state`, use exclusivamente `technical-implementer`
com consumer root e targets exatos; nunca envie `.loki` ao package writer nem
contratos/docs do pacote ao state writer.

Na ramificação `package`, `framework-artifact-writer` é owner exclusivo dos
`target_files` e sync files declarados; o auditor tem sandbox read-only e não
recebe permissão de escrita em produção. O Writer não pode autoatestar a própria
mudança. Finding retorna ao owner somente se não ampliar objetivo, destino,
target set ou semântica aprovada; caso contrário, invalide gates e replaneje.
O Writer entrega o profile mas nunca preenche `llm_consumption_quality`; o
Auditor entrega o parecer mas nunca recebe write access. Ausência de qualquer
agente obrigatório, profile completo, partição 10/10, evidência mecânica ou
parecer completo bloqueia sem fallback.

## Validators

- Intake de inferência valida locator, schema, status `unreviewed`,
  capture/lineage/provenance e digest canônico por ID.
- Replay idêntico é no-op com snapshot idêntico; ID divergente bloqueia e nenhum
  item altera contador ou denominador mais de uma vez.
- Reducer reconstrói componentes, denominadores, último evento, freshness e
  score; catalog validator confirma locators, lineage, paridade índice-registro,
  policy ID e digest exatos.
- Thresholds são inclusivos e apenas classificam eligibility; seleção pesa zero,
  protected nunca é purge-review eligible e nenhuma mutação é inferida.
- Candidato especializado permanece `unreviewed` e usa `record-only`, `block`
  ou `propose-promotion`; proposta lista targets, before/after, dry validation,
  Writer, auditor read-only e approval.
- Reorganização exige score inclusivo `<= 2`, targets/before-after/lineage
  exatos, preservação de protected/validated knowledge, gates prévios, Writer
  único, auditor read-only e validação determinística; similaridade não é
  identidade.
- Purge review exige unprotected score inclusivo `<= -4` e manifesto read-only
  completo com roots, hashes/digests e approval JIT requerida para um workflow
  separado de purge físico; este command valida dry-run e mantém execução
  `not-run`, mutation false e
  `removals_per_cycle: 1`.
- O contrato reserva post-purge e prova de ausência física ao workflow separado
  de purge físico; neste command, validator prova somente
  determinismo/completude do manifesto e zero write.
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
  `approved`; Writer/Auditor ausente, profile incompleto, partição inválida,
  audit result ausente, `blocked`, finding, inconclusão, baixa confiança
  material, fixture aplicável omitido, skip injustificado, bias falho ou human
  review impede terminal. Human-only exige `not-applicable` justificado e não
  executa fixtures irrelevantes.

## Human Gates

- `interview`: conflito de destino, ambiguidade de escopo ou generalização.
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
    file: "<persisted-approved-learning-source>"
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
      - "inference-good | inference-bad | inference-missing | file-discovery | script-command | unexpected-output | environment-mismatch | tool-friction | validation-friction | source-friction | handoff-friction | state-friction | dependency-friction | format-friction | external-research-friction | user-correction | communication-waste | search-waste | scope-waste | safety-gate-friction | minimum-next-path"
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
    destination_scope: "package | consumer-operational-state | consumer-context | runtime | backlog"
    artifact_type: "analytic-inference-state | AGENTS.md | CLAUDE.md | project-doc | project-doc-index | command | skill | agent | template | validator | doc | manifest | backlog"
    target_file: ""
    sync_files: []
    delegate: "technical-implementer | catalogador | bibliotecario | none"
  action: "propose-patch | apply-approved-patch | record-only | block-and-ask"
  proposed_change:
    summary: ""
    before: ""
    after: ""
  required_gates:
    - "approval"
  verification:
    - "diff revisado"
    - "validacao de estrutura"
  residual_risk: []
  analytic_inference_applicability:
    state: "applicable | not-applicable"
    reason: "<non-empty source/type reason>"
  analytic_inference:
    schema_version: 1
    state_binding:
      consumer_root: "<canonical consumer root>"
      consumer_root_source: "canonical-pwd"
      state_root: "<derived fixed state root>"
      registry_locator: "<relative locator | absent>"
      catalog_locators: []
    source:
      source_type: "deep-analysis-report | technical-retrospective"
      locator: "<exact persisted source locator>"
    intake_identity:
      namespace: "event | candidate"
      id: "<event_id | candidate_id>"
      stable_key: "<event:event_id | candidate:candidate_id>"
    source_digest_sha256: "<canonical source digest>"
    payload_digest_sha256: "<canonical item payload digest>"
    capture_id: "<observed capture ID | null>"
    lineage:
      run_id: "<observed | unavailable>"
      phase: "<observed | unavailable>"
      task_id: "<observed | unavailable>"
      agent_run_id: "<observed | unavailable>"
      handoff_id: "<observed | unavailable>"
      evidence_id: "<observed | unavailable>"
    provenance:
      source_refs: []
      evidence_refs: []
      freshness: "current | stale | unknown"
    status: unreviewed
    disposition: "record-only | block | propose-promotion"
    intake_reconciliation:
      state: "accepted | replayed-no-op | conflict-blocked"
      counted: "true | false"
      replayed_identity: "<stable_key | null>"
      conflict:
        state: "none | blocked"
        conflicting_source_locators: []
        payload_digests_sha256: []
    reconstructed_snapshot:
      algorithm_version: "analytic-inference-policy-v1"
      components:
        selected_count: 0
        investigated_count: 0
        validated_count: 0
        rejected_count: 0
        material_findings_count: 0
        tasks_helped_count: 0
        false_positive_count: 0
        repeated_evidence_count: 0
        stale_count: 0
      denominators:
        unique_events: 0
      as_of_event: "<event_id | null>"
      freshness: "current | stale | unknown | unsupported"
      score: 0
      policy:
        policy_id: "analytic-inference-policy-v1"
        policy_digest_sha256: "<verified exact digest>"
    eligibility:
      promotion: "true | false"
      reorganization: "true | false"
      purge_review: "true | false"
    target_proposal:
      state: "none | proposed | blocked"
      operation: "promotion | none"
      inference_ids: []
      exact_targets: []
      before: "<exact prior state | null>"
      after: "<exact proposed state | null>"
      lineage_before: "<observed lineage | null>"
      lineage_after: "<proposed lineage | null>"
      dry_validation: []
      required_gates:
        approval: "pending | approved | rejected | not-applicable"
      writer:
        agent: "technical-implementer | none"
        destination_scope: "consumer-operational-state"
        package_contract_writes_forbidden: true
        status: "pending | completed | blocked | not-required"
      auditor:
        agent: "runtime-qa | none"
        mode: "read-only | not-required"
        status: "pending | approved | blocked | not-required"
      catalog_mutation_applied: false
  promotion_execution:
    package_artifact_flow_required: "true | false"
    llm_artifact_quality:
      state: "applicable | not-applicable | not-evaluated"
      canonical_contract: "skills/lf-documentation-writing/references/llm-artifact-quality-validation.md | not-loaded"
      llm_artifact_profile: "<complete object | null>"
      profile_evidence: []
      llm_consumption_quality: "<complete object | null>"
      audit_evidence: []
      limitations: []
      second_family_calibration: "completed | unavailable | not-run"
      correction_replay_required: "true | false"
    writer:
      agent: "framework-artifact-writer | applicable-domain-writer | none"
      envelope_status: "pending | valid | invalid"
      target_files: []
      discovered_target_files: []
      status: "pending | completed | blocked | failed | not-required"
      validator_evidence: []
      profile_status: "pending | complete | invalid | not-required"
    auditor:
      agent: "framework-artifact-quality-auditor | applicable-domain-auditor | none"
      required: "true | false"
      status: "pending | approved | blocked | not-required"
      internal_status: "pending | approved | blocked | needs-human-review | not-applicable | not-required"
      block_reason: "finding_open | validation_inconclusive | low_material_confidence | fixture_omitted | bias_check_failed | human_review_required | handoff_incomplete | none"
      findings: []
      residual_risks: []
    iteration: 0
    gates_invalidated: false
    next_destination: "writer | orchestrator | none"
```

`analytic_inference` é condicional. Para candidato genérico,
`analytic_inference_applicability.state` deve ser `not-applicable`, sua `reason`
deve ser não vazia e o bloco inteiro `analytic_inference` deve ser `null`; não
preencha locator, digests, lineage, snapshot ou eligibility por conveniência.
Quando `state: applicable`, o bloco completo acima é obrigatório, status deve
ser exatamente `unreviewed` e nenhuma chave pode ser omitida. Source/intake
identity/digests, replay/conflict/counting, snapshot/policy/eligibility,
disposition, target proposal, gates, writer/auditor e mutation state devem
round-trip sem perda para Response e Resume Contract.

## Stop Conditions

Pare diante de required input ausente; fonte inelegível/insuficiente;
escopo/permissão insuficiente; destino ambíguo ou transitório; generalização de
caso isolado sem project-specific; tentativa de relaxar gate; regra consumidora
proposta para pacote; root-cause required incompleta e não bloqueada; dependência
indisponível; handoff sem destino; conflito de writers; validator ausente/falho;
gate/approval/decisão humana pendente; ou superfície sem validação verificável.
No intake de inferência, pare também diante de locator/source incompatível,
schema/status inválido, capture/lineage/provenance quebrada, mesmo ID com payload
divergente, policy ID/digest divergente, reducer/validator bloqueado, snapshot
irreconstruível ou mutação automática. Para reorganização, pare sem
elegibilidade, preservação de protected/validated knowledge, targets,
before/after, lineage, gates, Writer ou auditor. Para purge dry-run, pare em
qualquer falha de manifesto, root binding, containment/symlink, identity,
hashes, target set ou digest. Approval JIT, delete e post-purge validation são
precondições futuras do workflow separado de purge físico, não etapas
executadas aqui.
Pare tambem antes de consumer-doc write se `catalogador` estiver indisponivel,
caller/mode divergir ou o envelope exigir qualquer precondicao init.
Para `destination_scope: package`, pare também se o Writer ou auditor estiver
indisponível; profile, partição 10/10, checks ou audit result estiver ausente ou
inválido; auditoria tiver finding, inconclusão, baixa confiança material,
fixture aplicável omitido, skip injustificado, bias falho ou human review; se o
auditor tentar editar produção; ou se uma correção não invalidar o parecer
anterior e disparar replay completo. Se a correção ampliar materialmente o
envelope, invalide e renove também os gates.
Não declare conclusão com condição ativa.

## Resume Contract

Registre por candidato fonte, digest/evidência, classificação, escopo, destino,
execution friction, `root_cause_learning`, ação, owner/writes, handoffs, gates,
validators, artefatos impactados, diff esperado, approval, status, risco,
etapas concluídas, próxima ação e condição de retomada. Preserve a evidência e
retome sem reiniciar quando esse estado bastar.

Para candidato de inferência, registre ledger, source/payload digests,
replay/conflict, conjunto contado, policy ID/digest, reducer/validator,
snapshot/componentes/denominadores/as-of/freshness/score, eligibility,
disposição, status `unreviewed`, target proposal, Writer/auditor/gates e
`catalog_mutation_applied: false`.

Para reorganização, preserve operation ID, eligibility, operação proposta,
targets, before/after, lineage, evidência preservada, Writer/auditor,
validators, gates e mutation state. Para purge, preserve dry-run manifest e
digest, IDs/paths/artifact kinds/before hashes, exclusions/external hashes,
policy, consumer/state roots, approval JIT requerida mas não emitida/consumida,
`execution: not-run`, `catalog_mutation_applied: false` e handoff explícito para
um workflow separado de purge físico. Nunca registre targets removidos nem use fixture sintético como
approval ou prova de execução.

Para `destination_scope: package`, registre também `promotion_execution`: owner
e envelope do Writer, target/discovered files, `llm_artifact_profile` completo,
partição selecionados/skips, evidência de checks, `llm_consumption_quality`
completo, profile/audit evidence, limitações, segunda família, auditor e seus
estados interno/externo, findings, iteração, gates invalidados, replay requerido
e próximo destino. Após correção ou decisão humana, marque o audit result
anterior `invalidated_by_correction: true`, incremente a iteração, preserve a
evidência anterior, volte a `auditor.pending` e execute replay completo; apenas
uma nova auditoria `approved` permite conclusão. Em destinos não-package,
registre `llm_artifact_quality: null` e preserve o resume state anterior.
Para consumer docs project-specific, registre caller/mode fixo, estado do
handoff ao `catalogador`, `blocked_by`, targets, destinations e condicao exata
de retomada; nunca substitua o writer.
# Evidence-first learning sources

Accept approved persisted technical analyses and action plans, validated
retrospective outputs, evidence audits, completion records and validated
execution-knowledge entries as `learning_sources`. Require relevance to the
declared scope and observable approval provenance. Any non-empty eligible
source family among `learning_sources`, `retrospective_source` and
`analytic_inference_sources` is sufficient for intake; none is privileged as a
mandatory source type. Deduplicate candidates by evidence lineage/capture ID
and keep contradictions as conflicts for a specific human decision. A source
never directly promotes a durable rule, and raw runtime traces are not a
default input.
