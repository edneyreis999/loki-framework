---
name: "<namespace:command-name>"
type: command
status: draft
domain: "<domain>"
required_skills: []
---

# <namespace:command-name>

## Purpose

<Resultado esperado em uma frase.>

## Inputs

- <Entrada obrigatoria 1>
- <Entrada opcional ou contextual>

## Outputs

- <Artefato, decisao ou proposta produzida>

## Allowed Writes

- <Paths ou superficies permitidas>

## Forbidden Writes

- <Paths ou superficies proibidas>

## Required Skills

- <Skill obrigatoria quando aplicavel>

## Handoffs

- <Agente ou subprocesso em read-only/proposal-only>

## Validators

- <Check automatico exigido>

## Human Gates

- <interview | approval | human-runtime-validation | technical-review | domain-approval | visual-ux-confirmation>

## Packaging Checks

- <Se o comando fizer parte do pacote, declarar namespace, impacto em manifest/docs e validacoes de estrutura/autocontencao.>

## Stop Conditions

- <Situacao que pausa ou encerra a execucao>

## Resume Contract

<Onde salvar estado, pergunta pendente, arquivos afetados, validacoes e proximo passo.>
