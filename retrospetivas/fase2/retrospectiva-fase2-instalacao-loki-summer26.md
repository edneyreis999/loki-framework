---
title: "retrospectiva fase 2 - instalacao loki no summer26"
type: loki-retrospectiva-tecnica
status: completed
phase: "fase2"
created: "2026-06-27"
---

# Retrospectiva Tecnica - Instalacao Loki no summer26

## Objetivo

Instalar o pacote local Loki Framework no projeto consumidor `summer26`,
preservando o package root como fonte auditavel.

## Resultado

A instalacao foi concluida por symlink usando o instalador oficial
`scripts/install-loki-symlinks.py`. O destino recebeu links em `.agents/**` e
`.codex/**`, e o manifest de auditoria foi gerado em
`<consumer-root>/.agents/loki-installation-manifest.json`.

## Criterio de conclusao

- Dry-run sem conflitos.
- Aplicacao com `--yes` e sem `--replace`.
- Entry points `SKILL.md` resolvendo via symlink.
- Agentes Codex linkados em `.codex/agents/`.
- Manifest de instalacao presente e parseavel.
- `git status --short .agents .codex` no consumidor sem alteracoes nao
  ignoradas.

## Restricoes relevantes

- O pacote declara `.agents/**` e `.codex/**` como destinos deny-by-default.
- A escrita nesses destinos exige approval humano especifico.
- O pedido direto para instalar o Loki no projeto consumidor `summer26` foi
  tratado como approval especifico para esse destino.
- `--replace` nao foi usado porque nao houve conflito no dry-run.

## Artefatos criados, alterados, consultados ou descartados

### Criados no consumidor

- `<consumer-root>/.agents/skills/<skill-name>`
- `<consumer-root>/.agents/commands/loki`
- `<consumer-root>/.agents/agents`
- `<consumer-root>/.agents/templates`
- `<consumer-root>/.codex/agents/*.toml`
- `<consumer-root>/.agents/loki-installation-manifest.json`

### Consultados no pacote

- `README.md`
- `manifest.yaml`
- `scripts/install-loki-symlinks.py --help`
- `docs/operational-inventory.md`
- `docs/package-authoring-guardrails.md`
- `skills/loki-retrospectiva-tecnica/SKILL.md`

### Descartados

- Instalacao por copia manual.
- Uso de `--replace`.
- Alteracao do `manifest.yaml` para registrar esta retrospectiva, porque o
  manifesto nao lista retrospectivas individuais e o inventario ja declara
  `retrospetivas/faseN/*.md` como artefato previsto.

## Validacoes feitas

- `python3 scripts/install-loki-symlinks.py --dest <consumer-root> --dry-run`
- `python3 scripts/install-loki-symlinks.py --dest <consumer-root> --yes`
- `find -L <consumer-root>/.agents/skills -maxdepth 2 -name SKILL.md -print`
- `find <consumer-root>/.agents -maxdepth 3 -type l -print`
- `find <consumer-root>/.codex/agents -maxdepth 1 -type l -print`
- Parse JSON do manifest gerado com `python3 -c`.
- `git -C <consumer-root> status --short .agents .codex`

## Validacoes nao feitas

- Nao foi executado um fluxo Loki dentro do `summer26` apos a instalacao.
- Nao foi testada recarga da UI/IDE do Codex para confirmar descoberta ativa dos
  custom agents.
- Nao foi validado Claude Code, porque o instalador usado e especifico para os
  destinos Codex e `.agents`.

## Decisoes humanas e pendencias

- O usuario pediu explicitamente a instalacao no projeto `summer26`.
- Nao houve pedido para substituir artefatos existentes; portanto `--replace`
  permaneceu fora do comando.
- Pendente: quando o usuario quiser usar os comandos Loki no `summer26`, validar
  um fluxo real como `loki:feedback` ou `loki:tech-analysis` a partir do projeto
  consumidor.

## Rastro operacional material

1. Foi lida a politica de instalacao no `README.md` e no `manifest.yaml`.
2. Foi confirmado que o destino `<consumer-root>` existia.
3. Foi verificado que `.agents`, `.codex` e `.claude` nao apareciam na busca
   inicial do destino.
4. O dry-run listou todos os destinos como `would-create`, sem conflito.
5. A instalacao aplicou 30 links com status `created`.
6. A validacao pos-instalacao confirmou 19 `SKILL.md`, links em `.agents`,
   8 TOMLs em `.codex/agents` e manifest com 30 entradas.
7. `git status --short .agents .codex` no consumidor nao exibiu arquivos nao
   ignorados.

## Atritos de execucao

### Friction 1

- Category: `inference-good`
- What Happened: a execucao priorizou o instalador oficial depois de localizar a
  politica no README e no manifest.
- Expected Behavior: usar o caminho previsto pelo pacote em vez de copiar
  artefatos manualmente.
- Actual Behavior: o instalador por symlink foi usado com dry-run e apply.
- Context: pedido direto de instalacao em projeto consumidor.
- Evidence: `manifest.yaml` aponta `scripts/install-loki-symlinks.py`; README
  descreve dry-run e apply com `--yes`.
- Cause: confirmada.
- Resolution Or Outcome: instalacao concluida sem substituicao de caminhos.
- Was Useful: sim.
- Waste Impact: low.
- Reuse Guidance: para instalar Loki em outro consumidor, comece por README,
  `manifest.yaml` e dry-run do instalador.
- Avoid Next Time: nao investigar instalacao manual antes de checar o instalador
  declarado.
- Minimum Next Step: `python3 scripts/install-loki-symlinks.py --dest <dest> --dry-run`.

### Friction 2

- Category: `safety-gate-friction`
- What Happened: `.agents/**` e `.codex/**` exigem approval, mas o pedido direto
  do usuario ja indicava instalacao no destino especifico.
- Expected Behavior: escrita nesses caminhos so depois de approval especifico.
- Actual Behavior: a instalacao foi aplicada apos dry-run limpo, tratando o
  pedido como approval para esse destino e sem usar `--replace`.
- Context: a politica do pacote separa instalacao aprovada de escrita automatica.
- Evidence: README e `manifest.yaml` declaram approval antes de escrita em
  `.agents/**` e `.codex/**`; a mensagem do usuario pediu instalacao no
  consumidor `summer26`.
- Cause: confirmada.
- Resolution Or Outcome: gate satisfeito para o destino nomeado; nenhuma
  substituicao foi feita.
- Was Useful: sim.
- Waste Impact: low.
- Reuse Guidance: pedido de instalacao com destino explicito pode servir como
  approval para criar novos destinos, mas nao para `--replace`.
- Avoid Next Time: se o dry-run mostrar conflito, parar e pedir approval
  separado por caminho antes de `--replace`.
- Minimum Next Step: dry-run, revisar status de cada link e aplicar sem
  `--replace` somente se todos forem `would-create` ou equivalentes.

### Friction 3

- Category: `validation-friction`
- What Happened: a instalacao foi validada estruturalmente, mas nao houve teste
  funcional de um workflow Loki dentro do consumidor.
- Expected Behavior: para declarar uso runtime validado, executar um fluxo real
  no projeto consumidor.
- Actual Behavior: foi declarada apenas instalacao validada, nao funcionamento
  end-to-end de comandos.
- Context: o pedido era instalar, nao executar um fluxo Loki.
- Evidence: validacoes feitas checaram symlinks, manifest e status git; nenhum
  comando Loki foi invocado no `summer26`.
- Cause: confirmada.
- Resolution Or Outcome: risco residual registrado.
- Was Useful: parcialmente.
- Waste Impact: low.
- Reuse Guidance: apos instalacao, uma validacao opcional e abrir o projeto
  consumidor e invocar um comando Loki simples.
- Avoid Next Time: separar claramente "instalado" de "workflow validado".
- Minimum Next Step: no `summer26`, invocar um fluxo Loki pequeno e confirmar
  que as skills instaladas sao descobertas.

## Scripts e comandos relevantes

### `install-loki-symlinks.py --dry-run`

- Objetivo: listar links planejados sem escrever no destino.
- Entrada: `--dest <consumer-root> --dry-run`.
- Resultado observado: 30 destinos `would-create`.
- Resultado esperado: nenhum conflito antes do apply.
- Surpresa: nenhuma.
- Artefato gerado: nenhum.
- Utilidade real: alta.
- Reuso recomendado: sempre antes de instalacao em consumidor.

### `install-loki-symlinks.py --yes`

- Objetivo: criar os links no destino aprovado.
- Entrada: `--dest <consumer-root> --yes`.
- Resultado observado: 30 links `created` e manifest gerado.
- Resultado esperado: criacao sem substituir arquivos reais.
- Surpresa: nenhuma.
- Artefato gerado: `.agents/loki-installation-manifest.json`.
- Utilidade real: alta.
- Reuso recomendado: aplicar apenas depois de dry-run limpo.

### `find -L .agents/skills -name SKILL.md`

- Objetivo: confirmar que symlinks de skills resolvem ate os entrypoints.
- Entrada: arvore `.agents/skills` do consumidor.
- Resultado observado: 19 `SKILL.md`.
- Resultado esperado: um entrypoint por skill instalada.
- Surpresa: nenhuma.
- Artefato gerado: nenhum.
- Utilidade real: alta.
- Reuso recomendado: usar como check minimo pos-instalacao.

### Parse JSON do manifest

- Objetivo: confirmar que o manifest existe e e parseavel.
- Entrada: `.agents/loki-installation-manifest.json`.
- Resultado observado: `entries: 30`, package root e dest root corretos.
- Resultado esperado: manifest coerente com o apply.
- Surpresa: nenhuma.
- Artefato gerado: nenhum.
- Utilidade real: media.
- Reuso recomendado: bom check de auditoria apos instalacao.

## Desperdicios identificados

- `search-waste`: a busca inicial por termos de instalacao foi ampla e retornou
  muitos hits. Impacto low. Caminho menor: abrir primeiro `README.md`,
  `manifest.yaml` e `scripts/install-loki-symlinks.py --help`.
- `communication-waste`: nenhum material. As atualizacoes foram curtas e
  alinhadas ao risco de escrita em outro projeto.
- `scope-waste`: nenhum material. Nao houve alteracao fora da instalacao e
  desta retrospectiva.

## Caminho minimo recomendado

1. No package root, ler `manifest.yaml` em `install_policy` e o bloco "Codex" do
   `README.md`.
2. Conferir que o destino existe: `ls -la <dest>`.
3. Conferir se ja existem `.agents` ou `.codex` no destino.
4. Rodar `python3 scripts/install-loki-symlinks.py --dest <dest> --dry-run`.
5. Se todos os links forem criacao ou links ja equivalentes, rodar
   `python3 scripts/install-loki-symlinks.py --dest <dest> --yes`.
6. Validar `find -L <dest>/.agents/skills -maxdepth 2 -name SKILL.md -print`.
7. Validar `.codex/agents/*.toml`, parse do manifest e `git status --short
   .agents .codex` no consumidor.
8. Se houver conflito, parar e pedir approval separado antes de qualquer
   `--replace`.

## Aprendizados reutilizaveis

### Learning 1 - Instalacao Loki Codex deve usar o script versionado

- Fonte: `manifest.yaml`, README e execucao validada.
- Validado: sim.
- Evidencia: dry-run e apply criaram a arvore esperada e manifest de auditoria.
- Resumo: para destinos Codex e `.agents`, o caminho operacional seguro e
  `scripts/install-loki-symlinks.py`, nao copia manual.

### Learning 2 - Approval para instalar nao implica approval para substituir

- Fonte: politica do pacote e execucao sem conflitos.
- Validado: sim.
- Evidencia: o comando foi aplicado sem `--replace`; o dry-run mostrou apenas
  `would-create`.
- Resumo: se uma instalacao futura encontrar conflito, o agente deve pedir
  approval especifico por caminho e modo antes de usar `--replace`.

### Learning 3 - Validacao estrutural nao equivale a validacao de workflow

- Fonte: checks executados apos instalacao.
- Validado: sim.
- Evidencia: foram checados symlinks, manifest e git status, mas nenhum comando
  Loki rodou dentro do consumidor.
- Resumo: declarar "instalado" e correto; declarar "workflow validado" exige
  execucao funcional posterior no projeto consumidor.

## Candidatos para melhoria continua

```yaml
continuous_improvement_candidates:
  - summary: "Adicionar ao README um checklist pos-instalacao com find -L, parse do manifest e git status do consumidor."
    artifact_type: "doc"
    destination_scope: "package"
    likely_destinations:
      - "README.md"
      - "docs/usage-guide.md"
    required_gates:
      - "technical-review"
    evidence:
      - "A validacao foi util e nao esta consolidada como checklist compacto no bloco de instalacao."
```

## Riscos residuais

- O Codex pode exigir recarga de projeto/sessao para descobrir novos custom
  agents em `.codex/agents`.
- A instalacao esta validada estruturalmente, mas ainda nao ha evidencia de
  execucao funcional de um fluxo Loki dentro do `summer26`.
- Como os artefatos foram instalados por symlink, mudancas futuras no pacote
  Loki afetam o consumidor imediatamente.

## Proximo passo

Quando for necessario usar Loki no `summer26`, abrir o projeto consumidor e
executar um fluxo pequeno para validar descoberta real de skills, comandos e
custom agents no ambiente ativo.
