---
title: Auditoria de Autocontencao do Loki Framework Local
type: self-containment-audit
status: completed
created: 2026-06-24
self_contained: true
---

# Auditoria de Autocontencao

## Resultado

O pacote deve operar com os arquivos presentes neste diretorio. Blueprint, planos historicos, `.agents`, `.claude`, `.codex` e arquivos de jogo do projeto consumidor nao sao fontes obrigatorias para entender ou executar os contratos do pacote.

## Referencias Permitidas Fora do Pacote

| Categoria | Exemplos | Motivo |
| --- | --- | --- |
| Destinos de instalacao | `.claude/**`, `.codex/**`, `.agents/**` | Locais para onde o pacote pode ser copiado ou linkado apos approval humano. |
| Destinos de contexto duradouro do consumidor | `docs/**/*.md`, `docs/index.xml`, `AGENTS.md`, `CLAUDE.md` | Superficies que o Loki pode recomendar ou sincronizar apos approval, sem transforma-las em fonte normativa do pacote. |
| Superficies sensiveis declaradas do consumidor | Caminhos declarados pelo consumidor para runtime, extensoes, midia, builds ou outras areas protegidas | Arquivos que um plano futuro pode analisar ou modificar com gates; nao sao dependencias do pacote. |
| URLs de documentacao | URLs oficiais de Claude Code, Codex ou OpenAI | Referencias externas de pesquisa, nao arquivos locais necessarios para instalar o pacote. |

## Referencias Nao Permitidas

- Caminhos para blueprint fora deste diretorio.
- Caminhos para planos historicos fora deste diretorio.
- Dependencia de uma skill local em `.agents/` para explicar uma skill do pacote.
- Caminhos fixos de um projeto especifico, como um nome de jogo ou workspace local.
- Regras de negocio do consumidor copiadas para `commands/`, `skills/`,
  `agents/`, `templates/`, `docs/` ou `manifest.yaml` do pacote Loki.

## Checklist

- `manifest.yaml` usa apenas caminhos internos para fontes normativas.
- `docs/source-boundaries.md` declara o pacote como fonte canonica.
- `docs/package-authoring-guardrails.md` reforca que nenhuma nova fonte normativa pode apontar para fora do package root.
- `docs/project-context-catalog.md` separa pacote Loki de documentacao duradoura
  do consumidor.
- Skills especializadas por tecnologia usam caminhos relativos ao projeto consumidor, sem nome de engine, framework ou projeto fixo.
- `lf-index-navigator` e `bibliotecario` tratam `docs/index.xml` como alvo de
  navegacao do consumidor, nao como fonte normativa do pacote.
- Templates de agentes e comandos usam superficies genericas do projeto consumidor.
- README usa `PACKAGE_ROOT` para exemplos de instalacao portaveis.
