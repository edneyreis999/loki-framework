---
title: Loki Framework Local
type: framework-index
status: approved-for-manual-installation
created: 2026-06-24
self_contained: true
---

# Loki Framework Local

Este diretorio contem o pacote operacional aprovado do Loki Framework. Ele deve ser autocontido: apos instalado, nao depende de blueprint, planos historicos, `.agents`, `.claude` ou arquivos de um projeto especifico fora deste diretorio para ser entendido e usado.

## Conteudo

- `manifest.yaml`: indice operacional, politica de instalacao, guardrails e lista dos artefatos.
- `README.md`: instrucoes de instalacao local para Claude Code e Codex, sem executar copia automaticamente.
- `commands/`: comandos Loki do MVP.
- `skills/`: skills Loki e extensoes especializadas opcionais quando o
  projeto consumidor exigir.
- `agents/`: agentes operacionais, incluindo `standards-curator`,
  `source-researcher`, `bibliotecario` e `catalogador`.
- `templates/`: contratos base para comandos e componentes.
- `docs/`: guia de uso, workflows canonicos de execucao e aprendizado,
  inventario operacional, limites de fonte e contrato do catalogo XML do
  projeto consumidor.

## Status

Pacote aprovado para instalacao manual futura. Escrever em `.claude/**`,
`.agents/**` ou no runtime/engine/framework do projeto consumidor ainda exige
aprovacao explicita separada.
