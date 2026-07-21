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
| 2 | `skills/`, `agents/`, `codex/agents/` | Command bundles, conhecimento operacional e projeções Codex versionadas que devem funcionar sem consultar arquivos externos ao pacote. |
| 3 | `docs/*.md` declarados no inventario e manifest, incluindo `usage-guide.md`, `operational-inventory.md`, `self-containment-audit.md`, workflows, guardrails e contratos de contexto | Guias, inventario, auditorias, workflows canonicos, politica de modelo/effort, checklist normativo e contrato de roteamento entre pacote e contexto duradouro do consumidor. |
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
`docs/index.xml` pertence ao projeto consumidor e e o catalogo obrigatorio para
navegacao da documentacao local. A ausencia de `docs/index.xml` deve falhar
explicitamente, sem tentativa de usar qualquer `index.md` para esse fim.

## Contratos apos o corte

Cada familia conserva apenas a sua forma canonica: manifest/report/digest
agentic 4/5/4 com WTR 1; evidencia de sessao e conhecimento de execucao em
schema 1; catalogo analitico XML v2; e escopos de instalacao schema 2. Um
formato removido deve ser rejeitado antes de leitura que possa interpretá-lo e
antes de qualquer escrita; esta regra nao cria um leitor, conversor ou remocao
automatico. Schema 1 permanece valido nas familias que o declaram
explicitamente, e JSON de control plane nao e estado analitico persistido.

A projecao retirada nao e fonte, destino nem fallback do pacote. A
compatibilidade de dominio atual continua pertencendo a documentacao duradoura
do consumidor; os fallbacks operacionais que continuem validos devem ser
declarados pelo seu proprio contrato, nunca inferidos de um formato removido.
