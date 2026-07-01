---
name: rpg-maker-mz-data-json
description: Reference the required RPG Maker MZ data JSON workflow for reviewing or editing `data/*.json`, Database arrays, Common Events, maps, events, switches, variables, troops, actors, enemies, skills, items, weapons, armors, states, tilesets, or animations with structured parsing, restricted diff, and runtime gates.
when_to_use:
  - "Use when reviewing or editing RPG Maker MZ data JSON, Database arrays, Common Events, maps, events, switches, variables, troops, actors, enemies, skills, items, weapons, armors, states, tilesets, or animations."
  - "Use when structured parsing, restricted diff, and runtime gates are required."
argument-hint: "[data file, IDs, intended change, validation gates]"
arguments:
  required: []
  optional:
    - data_file
    - ids
    - intended_change
    - validation_gates
disable-model-invocation: false
user-invocable: false
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: coding
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - database IDs or runtime behavior are affected
  - parse or diff validation is unclear
  - playtest gate is required
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/rpg-maker-mz-data-json/SKILL.md"
shell: {}
type: skill-dependency
status: reference
source_policy: dependency-reference-not-copy
---

# rpg-maker-mz-data-json

## Role In Loki

Dependencia obrigatoria para qualquer revisao ou edicao de `data/*.json` no projeto consumidor, Database, Common Events, mapas, eventos, switches, variables, troops, actors, enemies, skills, items, weapons, armors, states, tilesets ou animations.

## Required References

- `references/common-event-command-contracts.md` quando a task interpretar, gerar ou auditar `code`/`parameters` de comandos de evento.
- `references/common-event-lifecycle.md` quando Common Events paralelos, switches de trigger, `command117`, input lock ou handoffs forem afetados.
- `references/json-write-style-and-diff.md` antes de qualquer escrita automatizada em `data/*.json`.
- `references/common-event-merge-and-editor-slots.md` quando criar, mover, renumerar ou mesclar Common Events.
- `references/historical-migration-scripts.md` quando revisar, adaptar ou considerar executar scripts historicos que alteram `data/*.json`.

## Procedure

1. Confirme arquivo alvo, IDs e nomes no JSON real do projeto consumidor.
2. Use parser JSON estruturado; nao use substituicao textual para alterar comandos, arrays ou Database entries.
3. Quando houver `code` de evento, confirme a semantica no engine da versao alvo antes de escrever ou auditar.
4. Preserve estilo de escrita do arquivo alvo e pare se o diff virar reflow massivo.
5. Para Common Events novos ou movidos, valide se o editor reconhece os slots e remapeie callers `code:117`.
6. Para scripts historicos ou geradores de fase, classifique `read-only` versus mutador e confirme precondicoes atuais antes de qualquer execucao.
7. Rode parse JSON depois da escrita, revise diff restrito e exija Playtest quando runtime for afetado.

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
- Classificacao de validacao: `structural_validation`, `runtime_pending` ou `playtest_validated`.
- Gate de Playtest quando runtime for afetado.

## Allowed Writes

Nenhuma escrita e autorizada por este arquivo. A permissao real vem da task ativa, da skill instalada no ambiente e dos gates do plano.

## Forbidden Writes

- Escrita manual ad hoc que quebre estrutura JSON.
- Alteracao de IDs nao planejados.
- Validar runtime sem Playtest humano.
- Executar script mutador historico sem preflight, precondicoes atuais e autorizacao explicita.

## Gates

- `parse-json`
- `diff-restricted-to-target`
- `playtest` quando a alteracao for executada pelo jogo.

## Source Boundary

Este arquivo declara o contrato minimo esperado da skill no pacote Loki. Ele nao depende de uma copia local de artefatos de sessao para ser entendido.
