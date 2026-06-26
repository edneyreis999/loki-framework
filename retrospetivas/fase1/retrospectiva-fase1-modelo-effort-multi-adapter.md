---
title: "retrospectiva fase 1 - metadados multi-adapter para skills e agents"
type: loki-retrospectiva-tecnica
status: completed
phase: "fase1"
created: "2026-06-26"
---

# Retrospectiva Tecnica - Metadados Multi-Adapter

## Objetivo

Resolver a verbosidade introduzida nas skills de autoria depois da pesquisa
sobre modelo e effort em Claude Code e Codex, preservando suporte completo aos
dois runtimes.

## Resultado

A decisao aprovada foi simplificar a politica de autoria: novas skills e
agents Loki devem ser gerados como contratos multi-adapter por padrao. Em vez
de ramificar o texto por executor, as skills geradoras devem preencher o
superset de metadados conhecido de Claude Code, Codex e Loki. O runtime ativo
usa os campos que entende e ignora os demais.

## Artefatos criados ou alterados

- `pesquisas/2026-06-26-modelo-effort-por-skill-agent-claude-code-codex.md`
- `skills/loki-agent-creator/SKILL.md`
- `skills/loki-agent-creator/references/agent-contract-template.md`
- `skills/loki-skill-creator/SKILL.md`
- `skills/loki-skill-creator/references/anatomy-and-frontmatter.md`
- `.agents/skills/loki-agent-creator/SKILL.md`
- `.agents/skills/loki-agent-creator/references/agent-contract-template.md`
- `.agents/skills/loki-skill-creator/SKILL.md`
- `.agents/skills/loki-skill-creator/references/anatomy-and-frontmatter.md`

## Validacoes feitas

- `find skills -maxdepth 2 -name SKILL.md | sort`
- `find skills -maxdepth 1 -type f -name '*.md'`
- `git diff --check`
- scan restrito de referencias proibidas nos arquivos alterados e na pesquisa
  nova.
- validacao local de frontmatter, nomes de skills, paths do `manifest.yaml` e
  sincronizacao entre `skills/` e `.agents/skills/`.
- `python3 scripts/install-loki-symlinks.py --dest /tmp/loki-symlink-test --dry-run`
- parse dos TOMLs em `codex/agents/` com `tomllib`.
- comparacao byte a byte entre as fontes canonicas em `skills/` e as copias
  instaladas em `.agents/skills/` para os arquivos afetados.

## Validacoes nao feitas

- Nao houve forward-test limpo pedindo para `loki-agent-creator` criar um novo
  agente multi-adapter do zero.
- Nao houve forward-test limpo pedindo para `loki-skill-creator` criar uma nova
  skill multi-adapter do zero.
- Nao houve teste real dentro do Claude Code consumindo uma skill ou subagent
  gerado com o superset.
- Nao houve teste real no Codex consumindo um custom agent TOML gerado a partir
  do novo contrato.

## Decisoes humanas e pendencias

- O usuario aprovou assumir como decisao que o Loki deve gerar skills e agents
  com frontmatter/metadados superset multi-adapter por padrao.
- O usuario pediu que as duas skills geradoras sejam agnosticas sobre qual tool
  vai executar o artefato gerado.
- O usuario pediu reduzir a verbosidade das skills geradoras, desde que elas
  expliquem explicitamente todos os metadados a preencher.
- Continua pendente validar, com exemplo novo, se o superset fica ergonomico na
  pratica para autoria de novos artefatos.

## Aprendizados reutilizaveis

### Learning 1 - Superset multi-adapter reduz verbosidade decisoria

- Fonte: feedback do usuario sobre `skills/loki-agent-creator/SKILL.md` e
  `skills/loki-skill-creator/SKILL.md`.
- Validado: sim, por decisao humana explicita e patch aplicado.
- Evidencia: o procedimento deixou de orientar uma escolha longa entre
  superficies e passou a exigir um contrato multi-adapter por padrao.
- Resumo: quando o objetivo e distribuir os mesmos artefatos para Claude Code e
  Codex, a autoria deve favorecer uma lista explicita de metadados suportados,
  nao uma matriz decisoria repetida no corpo das skills geradoras.

### Learning 2 - Skills e agents precisam de superset por formato, nao por runtime atual

- Fonte: pesquisa local e docs oficiais consultadas durante a alteracao.
- Validado: parcialmente. A regra foi aplicada nas skills geradoras, mas ainda
  falta forward-test criando artefatos novos.
- Evidencia: `loki-skill-creator` agora lista o superset de frontmatter de
  `SKILL.md` e os metadados Codex de `agents/openai.yaml`; `loki-agent-creator`
  agora lista campos Loki/common, Claude Code subagent e Codex custom agent
  TOML.
- Resumo: o contrato fonte pode ser agnostico, mas alguns runtimes ainda exigem
  projecoes de formato. Para agents, Claude Code usa Markdown/YAML e Codex usa
  TOML em `codex/agents/`.

### Learning 3 - Pesquisa nao deve virar fluxo verboso quando a decisao ja foi tomada

- Fonte: primeira revisao pos-pesquisa das duas skills geradoras.
- Validado: sim, por simplificacao posterior aprovada pelo usuario.
- Evidencia: a matriz "quando usar skill, subagent, profile/config ou custom
  agent" foi substituida por uma regra direta de metadados superset.
- Resumo: detalhes de pesquisa e caveats devem ficar em referencias; o
  procedimento principal deve conter a regra operacional que o autor precisa
  executar.

## Evidencia do que resolveu

- Feedback inicial: as alteracoes estavam verbosas e ainda obrigavam o autor a
  raciocinar por runtime.
- Decisao humana: gerar superset multi-adapter por padrao.
- Resolucao aplicada: `loki-agent-creator` e `loki-skill-creator` agora
  declaram essa decisao no procedimento principal e movem listas detalhadas de
  metadados para referencias.
- Validacao estrutural: checks de skill, manifest, diff, dry-run do instalador
  e parse de TOML passaram.

## Riscos residuais

- A lista de metadados Claude Code pode mudar; quando houver nova pesquisa
  oficial, as referencias devem ser atualizadas.
- O Codex pode ignorar campos extras em `SKILL.md`, mas isso ainda deve ser
  forward-testado com uma skill nova gerada pelo Loki.
- O superset reduz verbosidade decisoria, mas pode aumentar ruido no
  frontmatter dos artefatos gerados se valores neutros forem mal escolhidos.
- `.agents/**` continua sendo destino instalado e nao fonte normativa; as
  fontes canonicas permanecem em `skills/`.
- A pesquisa nova ainda esta sem commit e aparece como arquivo untracked.

## Candidatos para melhoria continua

```yaml
continuous_improvement_candidates:
  - summary: "Adicionar exemplos compactos de valores neutros validos para o superset multi-adapter."
    artifact_type: "skill-reference"
    destination_scope: "package"
    likely_destinations:
      - "skills/loki-skill-creator/references/anatomy-and-frontmatter.md"
      - "skills/loki-agent-creator/references/agent-contract-template.md"
    required_gates:
      - "technical-review"
    evidence:
      - "A regra exige preencher campos mesmo quando um runtime nao usa todos eles."

  - summary: "Forward-testar loki-skill-creator e loki-agent-creator criando artefatos novos com o superset."
    artifact_type: "validation"
    destination_scope: "package"
    likely_destinations:
      - "builds ou validation logs de uma fase futura"
    required_gates:
      - "technical-review"
    evidence:
      - "Validacoes atuais sao estruturais; ainda falta teste de autoria do zero."
```

## Proximo passo

Executar `loki:continuous-improvement` somente se o usuario quiser promover os
candidatos acima para novas regras, exemplos ou validadores do pacote. Sem essa
promocao, esta retrospectiva fica como evidencia transitoria da decisao e das
validacoes realizadas.
