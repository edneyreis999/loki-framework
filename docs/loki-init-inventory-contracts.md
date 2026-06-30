---
title: Contratos de Inventario do loki:init
type: loki-init-inventory-contracts
status: draft
self_contained: true
---

# Contratos de Inventario do loki:init

## Objetivo

Este documento define o conteudo minimo dos inventarios factuais produzidos por
agentes de dominio durante `loki:init`.

O contrato existe para que cada agente escreva a propria pasta em
`docs/loki-init/<agent-name>/` com liberdade de organizacao interna. Ele define
o que deve estar coberto no conjunto da pasta, nao nomes de arquivos, quantidade
de documentos ou secoes fixas.

## Contrato Universal

Cada pasta de agente deve permitir que outro agente entenda o estado presente da
especialidade sem depender da conversa que executou o init.

O conteudo minimo deve existir em algum ponto da pasta do agente:

- Escopo inventariado: qual especialidade, subsistema, area de produto ou
  superficie foi examinada.
- Fontes lidas: arquivos, diretorios, documentos, configuracoes, dados,
  scripts, assets ou outros artefatos consultados.
- Fatos atuais da especialidade: o que existe agora nas fontes lidas, separado
  de inferencias.
- Mapa de localizacao: onde encontrar esse tipo de informacao no projeto
  consumidor.
- Cobertura: o que foi inspecionado em detalhe, apenas mapeado ou nao encontrado
  nas fontes lidas.

O inventario pode ser distribuido em varios arquivos dentro da pasta do agente.
Validadores devem avaliar a pasta inteira. Nomes como `index.md`,
`source-map.md` ou `coverage.md` podem ser usados quando ajudarem a leitura, mas
nao sao obrigatorios.

## Relacao Com Skills Tecnicas

O core do `loki:init` define o que precisa ser inventariado. Skills tecnicas
definem onde buscar, como interpretar fontes especializadas e quais validadores
extras aplicar quando uma tecnologia concreta for declarada pelo usuario, pelo
projeto consumidor ou por um plano aprovado.

Sem skill tecnica carregada, o agente deve ficar no inventario factual generico:
fontes locais, estrutura observada, fatos verificaveis e limites da cobertura.

## Agentes Cobertos

Os contratos abaixo cobrem agentes de dominio com escrita no init. Agentes de
suporte sem escrita em `docs/loki-init/**` nao precisam produzir inventario.

- `audio-designer`
- `balance-economy-designer`
- `branching-narrative-designer`
- `dialogue-editor`
- `game-business-analyst`
- `game-designer`
- `game-product-owner`
- `gameplay-engineer`
- `level-designer`
- `narrative-designer`
- `narrative-qa`
- `quest-content-designer`
- `runtime-qa`
- `scene-presentation-designer`
- `technical-artist`
- `technical-implementer`
- `tools-pipeline-engineer`
- `ux-ui-designer`

`catalogador` nao tem contrato de inventario por agente. O workflow chama o
`catalogador` uma vez no final para catalogar os inventarios ja produzidos.

## Contratos Por Especialidade

### audio-designer

A pasta deve conter inventario factual de musica, ambience, SFX, assets de
audio, gatilhos ou cues, superficies de configuracao sonora e mapa das fontes de
audio encontradas.

### balance-economy-designer

A pasta deve conter inventario factual de progressao, atributos, recompensas,
custos, lojas, recursos, sinks e sources, tabelas numericas e fontes de economia
ou balanceamento.

### branching-narrative-designer

A pasta deve conter inventario factual de escolhas, flags, condicoes, rotas,
endings, consequencias e fontes de ramificacao narrativa encontradas.

### dialogue-editor

A pasta deve conter inventario factual do corpus de dialogos, vozes ou
personagens, localizacao e idioma observados, tom, variacoes, fontes de texto e
concentracao de dialogos no projeto.

### game-business-analyst

A pasta deve conter inventario factual de objetivos de produto presentes,
publico declarado, requisitos existentes, criterios de aceite existentes,
restricoes documentadas e fontes de decisao.

### game-designer

A pasta deve conter inventario factual de core loop, regras, mecanicas,
feedback, progressao, sistemas, tuning existente e fontes de design.

### game-product-owner

A pasta deve conter inventario factual da promessa do produto, escopo atual,
prioridades documentadas, personas ou publico, marcos existentes e fontes de
roadmap ou brief quando houver.

### gameplay-engineer

A pasta deve conter inventario factual de mecanicas implementadas, estado,
superficies de runtime, eventos ou sistemas chamadores, save/load, integracoes e
fontes tecnicas.

### level-designer

A pasta deve conter inventario factual de mapas ou areas, navegacao, gating,
encounters, ritmo espacial, pontos de interesse e fontes de layout.

### narrative-designer

A pasta deve conter inventario factual de personagens, premissa ou canon atual,
lugares, lore, arcos, dialogos, rotas ou finais e fontes narrativas.

### narrative-qa

A pasta deve conter inventario factual de continuidade, flags narrativas, rotas,
regressao de conteudo, alcancabilidade documentada e fontes de QA narrativo.

### quest-content-designer

A pasta deve conter inventario factual de quests, objetivos, NPCs, etapas,
recompensas, flags, pre-condicoes, pos-condicoes e fontes de conteudo.

### runtime-qa

A pasta deve conter inventario factual de superficies perceptiveis, fluxos
executaveis, input, audio e visual, save/load, integracoes, estado de validacao
existente e gates humanos ja documentados.

### scene-presentation-designer

A pasta deve conter inventario factual de cenas, staging, camera, transicoes,
sprites ou busts, backgrounds, CGs, timing, cues e fontes de apresentacao.

### technical-artist

A pasta deve conter inventario factual de assets visuais, formatos, animacoes,
efeitos, atlas, memoria ou performance aparente, referencias asset-runtime e
fontes de arte tecnica.

### technical-implementer

A pasta deve conter inventario factual de arquitetura tecnica atual, pontos de
entrada, modulos, scripts, configuracoes, dependencias, superficies de build ou
teste e fontes tecnicas.

### tools-pipeline-engineer

A pasta deve conter inventario factual de scripts, automacoes, import/export,
validadores, geradores, ferramentas historicas, classificacao de scripts e
fontes de pipeline.

### ux-ui-designer

A pasta deve conter inventario factual de fluxos UX, HUD, menus, dialog boxes,
estados UI, feedback visual, UI de save/load, acessibilidade observada e fontes
de interface.
