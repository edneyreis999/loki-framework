---
name: loki:self-healing
type: command
status: draft
domain: package-maintenance
required_skills:
  - loki-self-healing
  - lf-framework-impact-audit
  - lf-command-creator
  - lf-skill-creator
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - broad package scope
    - staged-file input with working tree divergence
    - corrections affecting commands, skills, agents, templates, docs, scripts, or manifest
    - conflicting package rules or incomplete operational inventory
  handoff_effort:
    research: medium
    coding: high
    documentation_transient: medium
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:self-healing

## Purpose

Auditar artefatos internos do Loki Framework contra os padroes do proprio
pacote e aplicar correcoes diretamente no working tree, sem approval adicional
por arquivo, sem staging automatico e sem commit automatico.

O comando usa a mesma mecanica geral de `loki:knowledge-extraction-analysis`:
primeiro entende o todo, depois analisa arquivos individualmente em paralelo
quando o runtime permitir, consolida achados e aplica correcoes serialmente.

## Inputs

- Um arquivo especifico do pacote Loki.
- Um diretorio de arquivos do pacote Loki.
- Um workflow Loki especifico, como `loki:run-plan`,
  `loki:continuous-improvement` ou `loki:knowledge-extraction-analysis`.
- Arquivos em staged, usando a lista do indice git.
- Escopo opcional de fora de escopo, quando fornecido pelo usuario.

## Outputs

- Correcoes aplicadas no working tree, dentro do escopo recebido.
- Relatorio de self-healing com escopo, fontes lidas, arquivos analisados,
  problemas corrigidos, problemas deixados sem alteracao, validadores
  executados e riscos residuais.
- Lista de arquivos alterados para revisao humana posterior.

## Allowed Writes

- Arquivos do pacote Loki dentro do escopo explicitamente selecionado:
  `commands/**`, `skills/**`, `agents/**`, `codex/agents/**`, `templates/**`,
  `docs/**`, `README.md`, `index.md`, `manifest.yaml` e `scripts/**`.
- Arquivos relacionados obrigatorios quando a correcao exigir consistencia de
  pacote, como `manifest.yaml`, `docs/operational-inventory.md`,
  `skills/lf-command-workflows/SKILL.md` ou
  `scripts/install-loki-symlinks.py`.

## Forbidden Writes

- `git add`, `git commit`, `git reset`, `git checkout` ou qualquer alteracao no
  indice git.
- `.claude/**`, `.codex/**`, `.agents/**` como destinos instalados ou espelhos
  locais.
- Arquivos fora do package root.
- Superficies de runtime, engine, framework ou projeto consumidor.
- Mudancas fora do escopo recebido, exceto arquivos de registro obrigatorios
  para manter o pacote coerente.

## Required Skills

- `loki-self-healing` para o procedimento de auditoria interna, correcao
  serializada e relatorio.
- `lf-framework-impact-audit` como referencia de selecao de artefatos,
  auditoria individual, deltas, lacunas, redundancias e conflitos quando a
  correcao envolver workflows ou multiplos artefatos.
- `lf-command-creator` quando a correcao tocar `commands/**`,
  `skills/lf-command-workflows/**` ou contrato de workflow invocavel.
- `lf-skill-creator` quando a correcao tocar `skills/**`, layout de skill,
  frontmatter, progressive disclosure ou referencias de skill.

## Handoffs

- Use handoffs read-only por arquivo ou grupo independente quando o runtime
  permitir analise paralela. Cada handoff retorna achados e proposta, nao
  escreve.
- A thread principal consolida os achados e aplica todas as escritas
  serialmente.

## Workflow

1. Resolver o escopo de entrada.
   - Para `staged`, usar a lista do indice git, mas aplicar correcoes somente
     aos arquivos no working tree.
   - Para workflow, mapear artefatos relacionados via
     `docs/operational-inventory.md`, `manifest.yaml` e contratos em
     `commands/` e `skills/`.
2. Ler `docs/operational-inventory.md`, `manifest.yaml`,
   `docs/package-authoring-guardrails.md` e os contratos relevantes antes de
   propor correcao.
3. Entender o todo: relacoes entre artefatos, wrapper de comando, skill,
   referencias, instalador, inventario, manifest e docs impactados.
4. Analisar arquivos individualmente em paralelo quando possivel. Se nao houver
   paralelismo, manter subsecoes independentes por arquivo.
5. Classificar achados como `corrigir agora`, `nao alterar`, `investigar`,
   `fora de escopo` ou `bloqueado`.
6. Corrigir apenas achados claros, verificaveis, dentro do escopo e com baixo
   risco de degradar o contrato do pacote.
7. Aplicar correcoes serialmente usando o menor patch coerente.
8. Rodar validadores de pacote proporcionais ao escopo.
9. Encerrar com relatorio de mudancas e lembrar que o usuario deve revisar,
   selecionar e stagear manualmente.

## Validators

- `find skills -maxdepth 2 -name SKILL.md | sort`
- `find skills -maxdepth 1 -type f -name '*.md'`
- Validacao de frontmatter de skills: `name`, `description` e nome da pasta.
- Validacao de paths do `manifest.yaml`.
- Scan de referencias proibidas em fontes normativas do pacote.
- `python3 scripts/install-loki-symlinks.py --dest /tmp/loki-symlink-test --dry-run`
  quando a mudanca tocar skills, commands, agents, templates ou instalador.
- Validadores especificos do artefato corrigido quando houver.

## Human Gates

- Nao ha approval previo por arquivo dentro do escopo solicitado pelo usuario.
- Ha revisao humana posterior obrigatoria: o comando deixa alteracoes no working
  tree e nunca faz stage nem commit.
- Parar para pergunta humana apenas quando o escopo for impossivel de resolver,
  quando a correcao exigiria escrever fora do package root, ou quando houver
  conflito real entre regras do pacote.

## Stop Conditions

- Nenhum escopo foi fornecido e nao ha arquivos staged.
- O escopo aponta para fora do package root.
- A unica correcao possivel exigiria alterar `.claude/**`, `.codex/**`,
  `.agents/**`, indice git ou runtime do consumidor.
- A correcao dependeria de informacao externa atual, pesquisa web ou decisao de
  produto nao presente nos artefatos Loki.
- Ha conflito entre regras internas sem criterio claro de desempate.

## Resume Contract

Registrar escopo resolvido, arquivos candidatos, fontes globais lidas, analises
por arquivo, correcoes aplicadas, arquivos alterados, validadores executados,
falhas de validacao, itens nao alterados e proximo passo esperado do usuario:
revisar diff e stagear manualmente o que quiser manter.
