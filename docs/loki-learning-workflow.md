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

Os executores podem gerar digest, backlog, completion reports e entries de
execution knowledge a partir de fontes persistidas. Esses artefatos tambem sao
fontes de evidencia, nao promocao automatica. Qualquer aprendizado duradouro
continua passando por `loki-continuous-improvement` e pelos gates aplicaveis.

O fluxo normalmente comeca depois do
[Workflow de Execucao de Plano do Loki](loki-plan-execution-workflow.md), mas
tambem pode ser acionado por feedback humano, bug, playtest, validacao manual,
artefato externo a comparar com o Loki, descoberta tecnica fora de uma fase
formal ou auditoria interna de conformidade do pacote.

## Fluxo

1. Um sinal aparece: feedback humano, bug, dificuldade tecnica, decisao de produto, build, validacao, artefato externo, auditoria interna ou repeticao de erro.
2. Se a fase ainda esta em execucao, use `loki-enrich-tasks` apenas para melhorar o plano atual. O aprendizado fica local: `tasks.md`, `task-N.M.md` ou `interaction/faseN/`.
3. Primeiro resolva o problema de fato. Nao transforme tentativa promissora em regra.
4. Quando a fase terminar, pausar claramente, ou a dificuldade real for resolvida, use `loki-retrospectiva-tecnica`.
5. A retrospectiva registra objetivo, artefatos, validacoes, decisoes humanas, evidencia do que resolveu, riscos e candidatos de melhoria.
6. Quando o sinal vier de um executor, trate digest, backlog, completion
   reports e execution-knowledge entries validadas como evidencia de entrada.
   Deduplicate por lineage/capture ID e nao promova nada so porque foi capturado.
7. Quando o sinal vier de artefatos externos, use `loki-knowledge-extraction-analysis` para produzir aprendizados rastreaveis antes de qualquer promocao. Ele gera analise para consumo posterior por `loki-continuous-improvement`, sem aplicar mudancas duradouras diretamente.
8. So depois use `loki-continuous-improvement` para avaliar se algum candidato merece virar contexto duradouro. Quando houver um diretorio ou multiplas retrospectivas, use `retrospective-digester` em modo read-only para digerir cada arquivo antes da consolidacao.
9. Todo candidato declara `root_cause_learning.required`. Quando for `true`, rode a fase read-only de causa raiz antes de escolher destino, diff ou patch: normalmente `source-researcher` para fonte de verdade/conflitos e `retrospective-digester` para padroes em retros. Pesquisa externa continua exigindo consentimento explicito.
10. O candidato e classificado por escopo: `universal`, `probable-universal`, `project-specific` ou `backlog`.
11. O destino e escolhido pela superficie que teria evitado a repeticao do problema.
12. Quando o escopo for auditoria interna de conformidade do pacote, `loki-self-healing` pode analisar artefatos internos e aplicar correcoes claras no working tree, sem stage ou commit. Achados especulativos continuam como `investigar` ou backlog.
13. Mudancas duradouras passam por gates: normalmente `technical-review`; e `approval` quando houver promocao normativa, instalacao, sincronizacao ou escrita sensivel.
14. Quando `destination_scope: package`, depois dos gates o
    `framework-artifact-writer` aplica o patch sob envelope exclusivo, classifica
    a aplicabilidade LLM-facing independentemente do modo documental e emite o
    `llm_artifact_profile`. As seis classes positivas sao `agent-facing`,
    `instruction-bearing`, `routing`, `prompt-assembly`, `context-hydration` e
    `validation-contract`; human-only usa `not-applicable` justificado. Se
    aplicavel, o Writer segue a fonte canonica
    [LLM Artifact Quality Validation Contract](../skills/lf-documentation-writing/references/llm-artifact-quality-validation.md),
    aplica os requisitos de autoria e entrega perfil, particao dos dez fixture
    IDs, arquivos e checks ao `framework-artifact-quality-auditor` independente.
    O Auditor read-only emite `llm_consumption_quality` com `rubric-v2`,
    `prompt-v2`, revisao isolada e bias controls; o Writer nunca autoaprova.
    Finding, inconclusao, baixa confianca material, fixture omitido, skip
    injustificado, bias ou validator falho bloqueiam; conflito normativo retorna
    `needs-human-review`. Toda correcao invalida o parecer anterior e exige
    replay completo. Destinos nao-package preservam integralmente seus routing,
    owners, validators, formatos e permissoes anteriores.
15. Quando `destination_scope: consumer-operational-state`, resolva e registre
    o `consumer_root` internamente a partir do `pwd` canonico e derive exclusivamente
    `<consumer-root>/.loki/analytic-inference/v2/`. O `technical-implementer`
    recebe envelope `task_scoped_writer`, targets exatos e ownership serial por
    arquivo. Registry ausente ou vazio permanece read-only e produz zero writes;
    somente uma mutacao aprovada pode inicializar o estado.
16. Promocao e reorganizacao nesse state root exigem diff/manifesto, validators,
    `technical-review` e approval root-bound antes do write. Purge exige dry-run
    e uma approval JIT propria, posterior, single-use e ligada a root, IDs,
    paths, hashes e digests exatos. Score indica elegibilidade, nunca autoridade.
17. Para docs duradouros do consumidor, preserve `catalogador`; para outros
    destinos de runtime, preserve o writer e auditor de dominio aplicaveis. Os
    agentes de artefatos do pacote nao sao instalados nem recebem permissao
    nesses destinos.
18. A promocao termina com diff, validacao e registro do risco residual.

## Inferencias Analiticas no Aprendizado

`loki-deep-analysis` pode emitir `inference_events` imutaveis e
`generated_candidates`. A retrospectiva pode emitir candidatos especializados
para observacoes materiais `inference-good`, `inference-bad` e
`inference-missing`, sempre com `capture_id`, locator, lineage e provenance.
Todo candidato nasce com status `unreviewed`; report, captura, evidencia e
retrospectiva nao promovem conhecimento e nao autorizam mutacao do catalogo.
O unico destino desse material para avaliacao duradoura e
`loki-continuous-improvement`.

No intake, melhoria continua valida locator, schema, status, capture, lineage,
provenance e digests. Eventos e candidatos usam identidades estaveis: replay
com ID e payload canonico identicos e no-op e nao conta novamente; o mesmo ID
com payload divergente bloqueia. Um reducer deterministico reconstrói snapshot,
componentes, denominadores, freshness e score. Limites de score determinam
somente elegibilidade para promocao, reorganizacao ou revisao de purge; nao
autorizam nenhuma dessas operacoes.

Consulta e manutencao catalog-backed resolvem o consumer root exclusivamente do
`pwd` canonico; o command deve iniciar na raiz do consumidor. Nao aceitam root
explicito, metadata de adapter, Git, ambiente, source paths, docs ou descoberta
de `.loki` como override. O pacote
nao fornece catalogo base nem overlay: `registry.xml`, indices `index.xml`,
records `rev-N.xml` e events `.xml` vivos existem somente em
`<consumer-root>/.loki/analytic-inference/v2/`. Estado
ausente ou vazio retorna `insufficient`, `mutation_applied: false` e zero writes.

O layout v1/JSON e legado read-only. Ele nao participa do lookup ativo nem
recebe mutacao; serve apenas como fonte inventariada de uma migracao copy-only
separada, com technical review e approval exata vinculada ao root e aos digests.

Promocao e reorganizacao exigem targets exatos, before/after, lineage,
validators, `technical-review`, approval, writer e auditor aplicaveis. Purge e
exclusao fisica e irreversivel apenas de registros nao protegidos elegiveis e
de todos os seus rastros pertencentes ao catalogo. A elegibilidade ainda e
insuficiente: primeiro ha dry-run com manifesto canonico completo e, depois,
approval novo e just-in-time para a operacao, inference IDs, paths,
target-set digest e policy digest exatos. Relatorios externos, retrospectivas,
evidencias, approvals e demais artefatos fora do catalogo sao preservados. Uma
falha ou rastro residual deixa a operacao em estado bloqueado, nunca em sucesso
parcial silencioso.

## Artefatos participantes

### Command bundles

| Command | Contribuicao no workflow |
| --- | --- |
| `loki-enrich-tasks` | Usa aprendizado transitorio para melhorar a fase atual, sem promover regra duradoura. |
| `loki-deep-analysis` | Emite report, eventos imutaveis e candidatos `unreviewed` para avaliacao posterior, sem mutar o catalogo. |
| `loki-retrospectiva-tecnica` | Registra evidencia auditavel depois de fase concluida, pausa clara ou dificuldade resolvida de fato. |
| `loki-continuous-improvement` | Classifica candidatos, escolhe destino duradouro, exige gates e prepara ou aplica patch aprovado. |
| `loki-agentic-development` | Pode produzir digest, backlog, completion/evidence e refs de execution knowledge para melhoria futura, sem promocao automatica. |
| `loki-knowledge-extraction-analysis` | Analisa artefatos externos e entrega aprendizados rastreaveis para `loki-continuous-improvement`, sem promover mudanca diretamente. |
| `loki-self-healing` | Audita artefatos internos do pacote e aplica correcoes escopadas no working tree, sem stage ou commit automatico. |

### Knowledge and support skills

| Skill | Contribuicao no workflow |
| --- | --- |
| `lf-external-knowledge-extraction` | Extrai aprendizados de artefatos externos sem decidir mudancas no Loki. |
| `lf-framework-impact-audit` | Audita quais comandos, skills, agents, docs ou templates Loki seriam impactados por um aprendizado externo. |
| `lf-execution-knowledge-capture` | Define o contrato de captura transitoria que CI pode consumir, mas nunca promove por conta propria. |
| `lf-analytic-inference` | Define lookup seletivo, schemas, replay idempotente, snapshot, score e elegibilidade de manutencao sem mutacao automatica. |
| `lf-internal-command-workflows` | Roteia workflows internos de manutencao do pacote, incluindo melhoria continua, extracao de conhecimento e self-healing. |
| `lf-command-creator` | Ajuda quando o aprendizado deve virar ou alterar um command com estado, gates e outputs. |
| `lf-agent-creator` | Ajuda quando o aprendizado pede um papel especialista com julgamento proprio. |
| `lf-skill-creator` | Ajuda quando o aprendizado deve virar procedimento reutilizavel com trigger e progressive disclosure. |

### Agents

| Agent | Contribuicao no workflow |
| --- | --- |
| `standards-curator` | Classifica escopo como `universal`, `probable-universal`, `project-specific` ou `backlog`. |
| `retrospective-digester` | Digerir uma retrospectiva ou lote pequeno em paralelo read-only, extraindo aprendizados, atritos, candidatos e evidencias para o orquestrador. |
| `source-researcher` | Confere evidencia, fonte de verdade, causa raiz, duplicidade, lacunas e conflitos multi-fonte antes de promocao duradoura. |
| `catalogador` | Promove aprendizado `project-specific` para `/docs` do consumidor e atualiza `docs/index.xml`. |
| `bibliotecario` | Localiza contexto duradouro existente antes de criar duplicidade. |
| `runtime-qa` | Fornece evidencia de validacao humana ou checklist quando o aprendizado depende de comportamento perceptivel. |
| `technical-implementer` | Writer exclusivo de `consumer-operational-state` sob `.loki/analytic-inference/v2/`, sempre com consumer root canonico, targets exatos, validators, gates e ownership serial; fora desse envelope retorna proposta. |
| `framework-artifact-writer` | Aplica somente promocao `package` em targets exatos, sob envelope, checks e ownership exclusivo; nunca escreve `.loki` nem substitui writers de consumidor/runtime. |
| `framework-artifact-quality-auditor` | Revisa de forma independente o patch de pacote depois dos checks; nao corrige producao, bloqueia finding/incerteza e nao substitui `technical-review` nem `approval`. |
| `execution-knowledge-cataloger` | Produz entry transitoria sanitizada e nao promovida; nao participa da decisao normativa. |

## Destinos corretos

Use esta regra simples:

| Aprendizado | Destino duradouro |
| --- | --- |
| Regra de negocio, lore, fluxo funcional ou termo do projeto consumidor | `docs/**/*.md` do consumidor + `docs/index.xml` |
| Regra project-wide para toda LLM do consumidor | `AGENTS.md` com roteamento minimo |
| Regra especifica de Claude Code, Codex ou adaptador | `CLAUDE.md` ou equivalente |
| Procedimento tecnico reutilizavel | `skills/` |
| Workflow invocavel com estado, outputs e gates | command bundle em `skills/loki-*/` |
| Papel especialista com julgamento proprio | `agents/` |
| Formato repetivel | `templates/` |
| Evidencia insuficiente ou caso isolado | backlog |

## O que nao fazer

- Nao promover aprendizado enquanto o problema ainda esta sendo testado.
- Nao usar retrospectiva como regra final. Ela e fonte auditavel.
- Nao promover uma correcao que previne apenas o sintoma quando `root_cause_learning.required` ainda precisa de pesquisa read-only.
- Nao guardar regra de negocio do consumidor no pacote Loki.
- Nao duplicar regra longa em `AGENTS.md` ou `CLAUDE.md`; esses arquivos devem rotear para a fonte certa.
- Nao alterar pacote, instalacao ou contexto duradouro sem gate exigido.
- Nao aplicar o gate LLM-facing package a destinos consumer, runtime ou
  backlog, nem permitir que o Writer aprove o proprio artefato.

## Checklist rapido

Antes de promover qualquer aprendizado, confirme:

- Qual fonte prova o aprendizado?
- O que era esperado e o que aconteceu?
- O que realmente resolveu?
- `root_cause_learning.required` e `true` ou `false`? Se for `true`, quais fontes read-only confirmam a causa raiz?
- O escopo e universal, provavel-universal, especifico do projeto ou backlog?
- Qual arquivo deveria ter prevenido a repeticao?
- Qual gate humano falta?
- Como validar que a nova regra funciona?

Se qualquer resposta estiver incerta, registre como candidato ou backlog, nao como regra aplicada.
# Evidence-first learning flow

`completion record -> sanitized evidence -> read-only audit -> explicit human
retrospective -> deduplicated candidate -> gated promotion`. Evidence gaps stay
gaps. The auditor reads manifests/sanitized snapshots on demand and labels its
inferences; it never receives private reasoning or directly promotes policy.
