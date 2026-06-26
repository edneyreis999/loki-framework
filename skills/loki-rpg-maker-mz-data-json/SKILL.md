---
name: loki-rpg-maker-mz-data-json
description: Reference the required RPG Maker MZ data JSON workflow for reviewing or editing `data/*.json`, Database arrays, Common Events, maps, events, switches, variables, troops, actors, enemies, skills, items, weapons, armors, states, tilesets, or animations with structured parsing, restricted diff, and runtime gates.
type: skill-dependency
status: reference
source_policy: dependency-reference-not-copy
---

# loki-rpg-maker-mz-data-json

## Role In Loki

Dependencia obrigatoria para qualquer revisao ou edicao de `data/*.json` no projeto consumidor, Database, Common Events, mapas, eventos, switches, variables, troops, actors, enemies, skills, items, weapons, armors, states, tilesets ou animations.

## Inputs

- Arquivo JSON alvo.
- IDs ou superficies afetadas.
- Plano de alteracao.
- Critérios de validacao.

## Outputs Expected By Loki

- Plano de edicao estruturada.
- Lista de arquivos e IDs afetados.
- Evidencia de parse JSON depois da escrita.
- Diff restrito ao escopo.
- Gate de Playtest quando runtime for afetado.

## Allowed Writes

Nenhuma escrita e autorizada por este arquivo. A permissao real vem da task ativa, da skill instalada no ambiente e dos gates do plano.

## Forbidden Writes

- Escrita manual ad hoc que quebre estrutura JSON.
- Alteracao de IDs nao planejados.
- Validar runtime sem Playtest humano.

## Gates

- `parse-json`
- `diff-restricted-to-target`
- `playtest` quando a alteracao for executada pelo jogo.

## Source Boundary

Este arquivo declara o contrato minimo esperado da skill no pacote Loki. Ele nao depende de uma copia local em `.agents/` para ser entendido.
