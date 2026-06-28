---
name: loki:knowledge-extraction-analysis
type: command
status: draft
domain: continuous-improvement
required_skills:
  - loki-knowledge-extraction-analysis
  - loki-external-knowledge-extraction
  - loki-framework-impact-audit
  - loki-continuous-improvement
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - many external artifacts or long instruction sets
    - incomplete Loki context or missing operational inventory
    - conflicting external patterns and Loki package policy
    - recommendations that could alter durable Loki commands, skills, agents, templates, docs, validators, or manifest
  handoff_effort:
    research: high
    documentation_transient: high
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:knowledge-extraction-analysis

## Purpose

Analisar artefatos externos, instrucoes, frameworks, comandos, skills,
documentos operacionais ou exemplos para extrair aprendizados rastreaveis que
possam melhorar o Loki Framework, sem forcar recomendacoes quando nao houver
aprendizado util.

Este comando produz uma analise estruturada para consumo posterior por
`loki:continuous-improvement`.

## Inputs

- Um ou mais artefatos externos a comparar com o Loki.
- Artefatos do Loki fornecidos no contexto ou descobertos pelo inventario
  operacional.
- Escopo da analise e destino esperado do relatorio, quando fornecidos.
- Limitacoes conhecidas de contexto, acesso a arquivos, ferramentas ou pesquisa.

## Outputs

- Relatorio Markdown `Analise de extracao de conhecimento para o Loki`.
- Handoff `external_extraction` com aprendizados candidatos, origem,
  evidencia, risco e criterio de nao-forcamento.
- Handoff `impact_audit` com artefatos Loki potencialmente impactados,
  workflows afetados, auditorias individuais, deltas, lacunas, redundancias e
  conflitos.
- Aprendizados consolidados com classificacao, origem, delta, recomendacao,
  local provavel de aplicacao, riscos, prioridade, custo, ganho e teste.
- Pontos rejeitados, pontos ja contemplados, lacunas, conflitos e recomendacoes
  finais para `loki:continuous-improvement`.
- Estrutura de ausencia de aprendizado util quando nenhum aprendizado confiavel
  for identificado.

## Allowed Writes

- Markdown transitorio de analise no plano ativo, quando o usuario pedir arquivo
  ou houver destino aprovado.
- `interaction/faseN/` para registrar perguntas ou decisoes humanas quando o
  comando estiver sendo executado dentro de um plano Loki.

## Forbidden Writes

- Mudancas diretas em commands, skills, agents, templates, validators, docs
  consolidados ou `manifest.yaml`; a saida deste comando e analitica e deve ser
  consumida por `loki:continuous-improvement` antes de promocao.
- `AGENTS.md`, `CLAUDE.md`, `docs/**/*.md` do consumidor ou `docs/index.xml`
  sem tarefa/gate de promocao posterior.
- `.claude/**`, `.codex/**` e `.agents/**` sem approval explicito de instalacao
  ou sincronizacao.
- Runtime, engine, framework ou superficies sensiveis do consumidor.

## Required Skills

- `loki-knowledge-extraction-analysis` para orquestrar as etapas, consolidar os
  handoffs e produzir a saida final.
- `loki-external-knowledge-extraction` para extrair aprendizados dos artefatos
  externos sem decidir mudancas no Loki.
- `loki-framework-impact-audit` para auditar o impacto dos aprendizados
  externos em artefatos, workflows e contratos do Loki.
- `loki-continuous-improvement` somente depois da analise, quando houver
  aprendizados validados a promover.

## Handoffs

- `source-researcher` em modo read-only quando os artefatos externos forem
  numerosos, conflitantes, incompletos ou dependerem de pesquisa aprovada.
- `standards-curator` em modo proposal-only quando a analise indicar possivel
  mudanca normativa no pacote Loki.

Se o runtime nao suportar handoffs paralelos, simule a separacao conceitual das
auditorias individuais e mantenha cada artefato afetado em uma subsecao
independente.

## Workflow

1. Carregar `loki-knowledge-extraction-analysis`.
2. Carregar `loki-external-knowledge-extraction` para mapear artefatos externos
   e produzir `external_extraction`.
3. Carregar `loki-framework-impact-audit` para ler
   `docs/operational-inventory.md`, selecionar artefatos Loki afetados e
   produzir `impact_audit`.
4. Consolidar os handoffs sem duplicar recomendacoes equivalentes.
5. Aplicar o principio de nao-forcamento: recomendar somente quando houver
   problema real, compatibilidade ou rejeicao consciente, mudanca concreta,
   origem rastreavel e ausencia de duplicacao ruidosa.
6. Produzir o formato completo exigido pelo contrato de saida da orquestradora.
7. Encerrar com recomendacao executiva para `loki:continuous-improvement`.

## Validators

- A analise separa observacao, interpretacao e recomendacao.
- Cada recomendacao tem origem rastreavel em artefato externo e delta em
  relacao ao Loki.
- Pontos ja contemplados, rejeitados, incompativeis ou sem evidencia suficiente
  nao viram recomendacoes implementaveis.
- A auditoria usa `docs/operational-inventory.md` ou declara sua ausencia.
- A etapa externa retorna `external_extraction` antes da auditoria do Loki.
- A etapa de impacto retorna `impact_audit` antes da consolidacao final.
- A saida inclui testes de validacao para aprendizados implementaveis.
- A analise nao inventa cobertura do Loki quando ela nao estiver visivel no
  contexto.
- A analise nao promove mudanca duradoura diretamente.

## Human Gates

- `interview` quando os artefatos externos, escopo ou destino da analise forem
  insuficientes para uma conclusao confiavel.
- `technical-review` se a analise recomendar mudanca em command, skill, agent,
  template, validator, doc consolidado ou `manifest.yaml`.
- `approval` para qualquer promocao normativa posterior, instalacao ou escrita
  sensivel.

## Packaging Checks

- A analise deve deixar claro se uma recomendacao posterior tocaria o pacote
  Loki, contexto duradouro do consumidor ou backlog.
- Se tocar o pacote, `loki:continuous-improvement` deve aplicar
  `docs/package-authoring-guardrails.md` antes de qualquer patch.

## Stop Conditions

- Nenhum artefato externo foi fornecido ou descoberto.
- Nao ha contexto suficiente para diferenciar Loki de artefatos externos.
- O pedido exige aplicar mudancas antes de produzir a analise.
- As recomendacoes dependeriam de pesquisa externa nao autorizada.

## Resume Contract

Registrar artefatos externos analisados, artefatos Loki considerados, inventario
lido ou limitacao, auditorias concluidas, aprendizados consolidados, rejeicoes,
lacunas, conflitos, decisoes pendentes, gates e proximo passo recomendado para
`loki:continuous-improvement`.
