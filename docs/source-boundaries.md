---
title: Fonte Canonica e Limites do Pacote Loki
status: completed
created: 2026-06-24
type: source-boundaries
self_contained: true
---

# Fonte Canonica e Limites do Pacote Loki

## Hierarquia de Fontes

| Prioridade | Fonte | Uso no pacote |
| --- | --- | --- |
| 1 | `manifest.yaml` | Indice de componentes, destinos sugeridos, guardrails e politica de instalacao. |
| 2 | `commands/`, `skills/`, `agents/`, `codex/agents/` | Contratos operacionais e projecoes Codex versionadas que devem funcionar sem consultar arquivos externos ao pacote. |
| 3 | `docs/usage-guide.md`, `docs/operational-inventory.md`, `docs/model-effort-guidance.md`, `docs/package-authoring-guardrails.md` e `docs/project-context-catalog.md` | Guia, inventario, politica de modelo/effort, checklist normativo e contrato de roteamento entre pacote e contexto duradouro do consumidor. |
| 4 | `templates/` e `scripts/` | Contratos base e utilitarios versionados para instalar ou validar o pacote. |

## Limites

| Area | Regra |
| --- | --- |
| Fontes historicas | Blueprint e planos historicos foram internalizados no pacote. Nao sao dependencias operacionais. |
| Pacote operacional | O proprio diretorio do pacote e a fonte auditavel. Use caminhos relativos ao pacote sempre que possivel. |
| Instalacao local | `.claude/**`, `.codex/**` e `.agents/**` sao destinos do projeto consumidor, nao fontes do pacote. Escrever neles exige approval separado. |
| Documentacao do consumidor | `docs/**/*.md`, `docs/index.xml`, `AGENTS.md` e `CLAUDE.md` do projeto consumidor sao destinos de aplicacao e leitura operacional, nunca fontes normativas do pacote. |
| Runtime, engine ou framework consumidor | Superficies sensiveis declaradas pelo consumidor, incluindo dados, extensoes, midia, builds ou outras areas protegidas, nao sao dependencias do pacote. |
| Evolucao do pacote | Mudancas em componentes consolidados devem seguir `docs/package-authoring-guardrails.md` e terminar com validacao objetiva. |

## Politica de Conflito

Quando houver diferenca entre uma memoria externa e os arquivos deste pacote, vale o pacote ate que um humano aprove uma revisao do proprio pacote.

Decisoes antigas ainda abertas devem ser registradas como backlog ou pendencia futura dentro do pacote ou no plano ativo do projeto consumidor, sem exigir leitura de arquivos historicos externos.

Quando o conflito envolver regra de negocio do consumidor, vale a documentacao
duradoura do consumidor (`/docs` + `docs/index.xml`) para aquele projeto, sem
promover essa regra automaticamente para o pacote Loki.

## Checkpoint Humano

Qualquer nova dependencia fora deste diretorio precisa de approval explicito e deve ser copiada, resumida ou substituida por uma referencia interna antes de publicar o pacote para outro projeto.

`index.md` na raiz do pacote continua sendo o indice do framework. Ja
`docs/index.xml` pertence ao projeto consumidor e serve apenas para navegacao da
documentacao local.
