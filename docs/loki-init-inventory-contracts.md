---
title: Contratos de Coverage de Inventario do loki-init
type: loki-init-inventory-contracts
status: draft
self_contained: true
---

# Contratos de Coverage de Inventario do loki-init

## Proposito e audiencia

Este documento e a referencia tecnica duravel para agentes que planejam,
investigam, materializam ou validam inventarios no `loki-init`. Ele define o que
deve ser coberto por dominio, como provar coverage e quando um root documental
e substancial. Nao concede autoria de consumer docs aos investigadores.

## Ownership e fronteiras

- Os 15 papeis de dominio sao investigadores read-only/proposal-only. Eles
  satisfazem este contrato emitindo `loki_init_research_packet` schema v1 com
  findings, fontes, coverage delta, publication intent e continuation.
- O orquestrador aceita ou rejeita packets, atualiza o registry e a coverage
  matrix, cria batches e persiste estado operacional no plan root aprovado.
- Somente `catalogador` cria, altera, move ou remove consumer `docs/**`, por
  chamadas seriais com `calling_workflow: loki-init` e mode init exato.
- Investigadores nao escrevem diretamente em `docs/loki-init/**`, nao chamam o
  `catalogador` e nao recebem fallback de escrita documental.
- Este contrato nao autoriza alteracao de runtime, codigo, assets, dados,
  configuracao, dependencias, `.agents/**`, `.claude/**`, `.codex/**`,
  `AGENTS.md` ou `CLAUDE.md`.

## Modelo universal de requirements

Cada requirement planejado possui um registro estavel:

```yaml
coverage_requirement:
  requirement_id: "<domain-id>.<stable-topic-id>"
  domain_id: "<domain-id>"
  required_depth: "map | deep"
  state: "pending | mapped | covered | not_found | not_applicable | deferred | blocked"
  source_refs: []
  evidence_packet_refs: []
  materialization_refs: []
  reason: ""
```

IDs permanecem estaveis entre cold start, continuation e refresh. Mudanca de
revision de packet nao renomeia o requirement. `source_refs` identificam fontes
tentadas/lidas; `evidence_packet_refs` apontam somente para packets aceitos; e
`materialization_refs` provam onde o `catalogador` publicou ou dispositionou o
finding. Coverage sem evidence aceita e invalida.

## Profundidade e estados

- `required_depth: map` exige localizar a superficie e suas fontes. Aceita como
  terminal `mapped`, `covered`, `not_found` ou `not_applicable`.
- `required_depth: deep` exige findings factuais suficientes para explicar o
  estado atual da superficie. Aceita como terminal `covered`, `not_found` ou
  `not_applicable`; `mapped` nunca satisfaz deep.
- `covered`: evidence aceita sustenta o finding no depth exigido.
- `mapped`: fontes/localizacoes foram identificadas, sem leitura profunda
  suficiente; satisfaz apenas `map`.
- `not_found`: fontes candidatas suficientes foram tentadas e a evidence
  registra locators, outcomes e limites da busca; ausencia presumida falha.
- `not_applicable`: evidence e `reason` explicam por que o requirement nao se
  aplica ao projeto/tipo selecionado.
- `deferred`: trabalho foi adiado com motivo e proxima condicao; nunca e estado
  terminal de sucesso.
- `blocked`: uma barreira concreta impede coverage; permite apenas resultado
  global `partial` ou `blocked`, nunca `completed`.
- `pending`: ainda nao avaliado; nao e terminal.

Nao existem quotas universais de arquivos, linhas, palavras, tokens, secoes ou
findings. O acceptance gate e evidence e coverage no depth exigido.

## Fontes, frescor e conflitos

Cada packet registra fontes tentadas e lidas, locator, outcome, relevancia e
freshness marker. Para fatos atuais, use esta precedencia:

1. fonte local atual que implementa ou configura o comportamento;
2. teste, validator ou dado local atual que observa o comportamento;
3. documento consumidor atual e explicitamente autoritativo;
4. brief, plano ou nota historica, tratados como intent/contexto e nao como
   prova automatica do estado presente.

Uma regra explicita do projeto pode alterar a precedencia; registre a fonte da
regra. Nao resolva conflito silenciosamente: preserve as fontes conflitantes,
freshness, confidence e pergunta/gate aplicavel. Antes da reconciliacao final,
releia a fonte atual quando o finding puder ter mudado desde o fan-out ou quando
depender de documento comum materializado depois da investigacao. Isso e uma
rechecagem dirigida, nao um re-scan amplo obrigatorio.

## Bootstrap e README substancial

O bootstrap do `catalogador` cria navegacao inicial e um README para cada
investigador cuja invocacao sera tentada. Root ou README existente prova somente
bootstrap, nunca coverage terminal nem conclusao do dominio.

Um README substancial precisa permitir que uma pessoa ou agente:

- identifique dominio, objetivo, selection reason e status real;
- entenda o que pertence e nao pertence ao root;
- encontre fontes comuns, coverage plan e requirements por ID/depth;
- escolha os documentos/materializacoes relevantes e navegar por crosslinks;
- veja gaps, conflitos, perguntas, blockers e proxima atualizacao esperada.

README de titulo vazio, placeholder ou lista de links sem identidade e plano de
coverage falha. Conteudo pequeno pode ser substancial quando o projeto realmente
tem pouca evidence e essa escassez esta justificada por fontes tentadas.

## Acceptance do root documental final

Um root selecionado e substancial/final somente quando:

- o README e navegavel e reflete o estado reconciliado;
- todo requirement aplicavel esta terminal no depth exigido;
- fatos materializados possuem evidence packet aceita e fontes rastreaveis;
- inferences, unknowns, contradicoes e confidence permanecem visiveis;
- todo packet aceito foi materializado, superseded ou bloqueado/dispositionado
  com explicacao; nao ha packet orfao;
- materialization refs e hashes resolvem para os docs atuais;
- links, crosslinks e entrada no index aplicavel resolvem sem duplicata/orfao;
- conteudo pequeno, `not_found` ou `not_applicable` e sustentado pela evidence
  exigida, e nao por ausencia de texto.

Bootstrap sozinho, requirement deep apenas `mapped`, `deferred`, packet aceito
nao materializado ou qualquer batch diferente de `committed` bloqueiam
acceptance final. Batch `blocked` e terminal apenas para bookkeeping de recovery
e resultado global `partial`/`blocked`; ele nunca autoriza `completed`.

## Requirements por especialidade

Os IDs abaixo sao estaveis. `map` pede localizacao confiavel; `deep` pede estado
factual atual. Um requirement pode terminar `not_found` ou `not_applicable`
somente conforme as regras universais acima.

### audio-designer

- `audio-designer.music` (`deep`): musica existente e seu uso.
- `audio-designer.ambience` (`deep`): ambience existente e seu uso.
- `audio-designer.sfx` (`deep`): SFX existentes e seu uso.
- `audio-designer.audio-assets` (`map`): assets e formatos de audio.
- `audio-designer.triggers-cues` (`deep`): gatilhos ou cues de reproducao.
- `audio-designer.sound-configuration` (`map`): superficies de configuracao sonora.
- `audio-designer.source-map` (`map`): fontes de audio encontradas.

### balance-economy-designer

- `balance-economy-designer.progression` (`deep`): progressao existente.
- `balance-economy-designer.attributes` (`deep`): atributos e valores atuais.
- `balance-economy-designer.rewards-costs` (`deep`): recompensas e custos.
- `balance-economy-designer.shops-resources` (`deep`): lojas e recursos.
- `balance-economy-designer.sinks-sources` (`deep`): sinks e sources.
- `balance-economy-designer.numeric-tables` (`map`): tabelas numericas.
- `balance-economy-designer.source-map` (`map`): fontes de economia/balanceamento.

### game-business-analyst

- `game-business-analyst.product-objectives` (`deep`): objetivos de produto presentes.
- `game-business-analyst.declared-audience` (`deep`): publico declarado.
- `game-business-analyst.requirements` (`deep`): requisitos existentes.
- `game-business-analyst.acceptance-criteria` (`deep`): criterios de aceite existentes.
- `game-business-analyst.documented-constraints` (`deep`): restricoes documentadas.
- `game-business-analyst.decision-sources` (`map`): fontes de decisao.

### game-designer

- `game-designer.core-loop` (`deep`): core loop atual.
- `game-designer.rules-mechanics` (`deep`): regras e mecanicas.
- `game-designer.feedback` (`deep`): feedback de jogo.
- `game-designer.progression-systems` (`deep`): progressao e sistemas.
- `game-designer.tuning` (`deep`): tuning existente.
- `game-designer.source-map` (`map`): fontes de design.

### game-product-owner

- `game-product-owner.product-promise` (`deep`): promessa do produto.
- `game-product-owner.current-scope` (`deep`): escopo atual.
- `game-product-owner.documented-priorities` (`deep`): prioridades documentadas.
- `game-product-owner.personas-audience` (`deep`): personas ou publico.
- `game-product-owner.milestones` (`deep`): marcos existentes.
- `game-product-owner.roadmap-brief-sources` (`map`): fontes de roadmap ou brief.

### gameplay-engineer

- `gameplay-engineer.implemented-mechanics` (`deep`): mecanicas implementadas.
- `gameplay-engineer.state` (`deep`): estado de gameplay.
- `gameplay-engineer.runtime-surfaces` (`map`): superficies de runtime.
- `gameplay-engineer.callers-events` (`deep`): eventos ou sistemas chamadores.
- `gameplay-engineer.save-load` (`deep`): save/load.
- `gameplay-engineer.integrations` (`deep`): integracoes.
- `gameplay-engineer.source-map` (`map`): fontes tecnicas.

### level-designer

- `level-designer.maps-areas` (`deep`): mapas ou areas.
- `level-designer.navigation` (`deep`): navegacao.
- `level-designer.gating-encounters` (`deep`): gating e encounters.
- `level-designer.spatial-pacing` (`deep`): ritmo espacial.
- `level-designer.points-of-interest` (`deep`): pontos de interesse.
- `level-designer.layout-sources` (`map`): fontes de layout.

### narrative-designer

- `narrative-designer.characters` (`deep`): personagens.
- `narrative-designer.premise-canon` (`deep`): premissa ou canon atual.
- `narrative-designer.places-lore` (`deep`): lugares e lore.
- `narrative-designer.arcs-dialogue` (`deep`): arcos e dialogos.
- `narrative-designer.routes-endings` (`deep`): rotas ou finais.
- `narrative-designer.source-map` (`map`): fontes narrativas.

### narrative-qa

- `narrative-qa.continuity` (`deep`): continuidade.
- `narrative-qa.narrative-flags` (`deep`): flags narrativas.
- `narrative-qa.routes` (`deep`): rotas.
- `narrative-qa.content-regression` (`deep`): regressao de conteudo.
- `narrative-qa.documented-reachability` (`deep`): alcancabilidade documentada.
- `narrative-qa.source-map` (`map`): fontes de QA narrativo.

### quest-content-designer

- `quest-content-designer.quests-objectives` (`deep`): quests e objetivos.
- `quest-content-designer.npcs-steps` (`deep`): NPCs e etapas.
- `quest-content-designer.rewards` (`deep`): recompensas.
- `quest-content-designer.flags` (`deep`): flags.
- `quest-content-designer.preconditions` (`deep`): pre-condicoes.
- `quest-content-designer.postconditions` (`deep`): pos-condicoes.
- `quest-content-designer.source-map` (`map`): fontes de conteudo.

### scene-presentation-designer

- `scene-presentation-designer.scenes-staging` (`deep`): cenas e staging.
- `scene-presentation-designer.camera-transitions` (`deep`): camera e transicoes.
- `scene-presentation-designer.sprites-busts` (`map`): sprites ou busts.
- `scene-presentation-designer.backgrounds-cgs` (`map`): backgrounds e CGs.
- `scene-presentation-designer.timing-cues` (`deep`): timing e cues.
- `scene-presentation-designer.source-map` (`map`): fontes de apresentacao.

### technical-artist

- `technical-artist.visual-assets-formats` (`map`): assets visuais e formatos.
- `technical-artist.animations-effects` (`deep`): animacoes e efeitos.
- `technical-artist.atlases` (`map`): atlas.
- `technical-artist.memory-performance` (`deep`): memoria ou performance aparente.
- `technical-artist.asset-runtime-references` (`deep`): referencias asset-runtime.
- `technical-artist.source-map` (`map`): fontes de arte tecnica.

### technical-implementer

- `technical-implementer.architecture` (`deep`): arquitetura tecnica atual.
- `technical-implementer.entry-points` (`deep`): pontos de entrada.
- `technical-implementer.modules-scripts` (`map`): modulos e scripts.
- `technical-implementer.configuration-dependencies` (`deep`): configuracoes e dependencias.
- `technical-implementer.build-test-surfaces` (`deep`): superficies de build ou teste.
- `technical-implementer.source-map` (`map`): fontes tecnicas.

### ux-ui-designer

- `ux-ui-designer.ux-flows` (`deep`): fluxos UX.
- `ux-ui-designer.hud-menus` (`deep`): HUD e menus.
- `ux-ui-designer.dialog-boxes-ui-states` (`deep`): dialog boxes e estados UI.
- `ux-ui-designer.visual-feedback` (`deep`): feedback visual.
- `ux-ui-designer.save-load-ui` (`deep`): UI de save/load.
- `ux-ui-designer.observed-accessibility` (`deep`): acessibilidade observada.
- `ux-ui-designer.source-map` (`map`): fontes de interface.

## Relacao com skills tecnicas

O core define requirements e acceptance. Skills tecnicas definem onde buscar,
como interpretar fontes especializadas e quais validators extras aplicar quando
tecnologia concreta estiver sustentada por fonte ou decisao. Sem skill tecnica,
o investigator permanece factual: fontes locais, estrutura observada, facts,
inferences tipadas e limites de coverage; nao inventa semantica especializada.

## Checklist de validacao

- Os 15 dominios selecionados possuem requirements com IDs estaveis e depth.
- Todo state e valido; `mapped` falha para deep; `pending`/`deferred` falham
  para sucesso; `blocked` produz somente partial/blocked.
- `not_found` inclui tentativas suficientes; `not_applicable` inclui reason.
- Evidence refs resolvem para packets aceitos e materialization refs/hashes
  resolvem para os docs atuais.
- Investigadores nao possuem consumer docs writes; `catalogador` e o unico
  consumer docs writer e cada chamada usa caller/mode init exato.
- READMEs atendem identidade, navegacao, selecao e coverage plan; bootstrap nao
  e confundido com conclusao.
- Facts possuem fontes; inferences, unknowns, conflitos e freshness permanecem
  visiveis.
- Packets aceitos e batches possuem destino terminal; final reconciliation e
  links/index aplicaveis passaram.
- Nenhum gate universal depende de quantidade de arquivos ou volume textual.

## Manutencao

Atualize este contrato quando um dominio ganhar/perder responsabilidade, quando
o schema de coverage mudar ou quando validators demonstrarem que um requirement
nao e estavel ou nao separa `map` de `deep`. Alteracoes sao package policy e
seguem a rota `destination_scope: package`: envelope e approval aplicavel,
`framework-artifact-writer`, checks e
`framework-artifact-quality-auditor` independente. O catalogo/index do package
e mantido em tarefa separada; este documento nao cria consumer docs.
