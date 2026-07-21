---
title: "Aceite integral - plano 032"
type: loki-validation-report
status: passed
---

# Aceite integral - plano 032

## Resultado

O pacote passou a matriz de aceite sem escrever em destino consumidor. O
validador de evidência de sessão foi compilado; ele exige um arquivo de
evidência como argumento e não há captura de sessão a validar neste pacote.

## Evidência mecânica

- `validate-agentic-run-state.py --self-test`: passou.
- `validate_catalog.py --technology loki-framework --policy .../policy-v1.json`:
  estado XML v2 válido, sem mutação.
- `validate-loki-init-catalogador-contracts.py --enforce-current-tree`: 31
  template checks, 27 fixtures positivas, 15 negativas e 29 pares atuais.
- `validate-install-scopes.py`: passou; inclui paridade Codex/Claude e scan
  residual Goose nas superfícies normativas.
- `validate-install-loki-upgrade.py`: 15/15 testes passaram.
- `validate-run-plan-review-state.py`: passou para os 17 task files.
- `py_compile` para scripts de inferência e session evidence, `git diff --check`,
  parse TOML (25) e parse XML (144): passaram.
- Dry-runs dos perfis `consumer`, `package-source` e `all`: passaram, sem
  escrita no destino temporário.
- Integridade: 57 entrypoints `SKILL.md`, nenhum Markdown na raiz de `skills/`;
  os 12 mirrors de templates existem e permanecem sincronizados.

## Goose e escopo

Não há arquivo físico em `goose/`; o diff contém exatamente as 20 deleções
aprovadas. `git ls-files goose` ainda lista esses paths porque as deleções não
foram staged — comportamento Git esperado. Não foi feito staging, commit,
instalação ou alteração de consumidor.

## Conclusão

Os contratos pós-corte são rejection-only para layouts legados, preservando os
schemas atuais explicitamente suportados e os fallbacks operacionais/de domínio
documentados.
