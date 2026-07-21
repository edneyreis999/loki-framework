# Deep analysis — remoção de compatibilidade legada

## Status

`partial`

## Resumo executivo

A compatibilidade legada não está concentrada em um único ponto. Ela permanece
executável em quatro frentes principais:

1. leitores de schemas antigos nos estados agentic, evidências e inferência
   analítica;
2. migração e limpeza automática no instalador;
3. inputs e fallbacks públicos, como `operational_trace` e `index.md` no
   consumidor;
4. uma projeção Goose transicional, ainda não inventariada pelo contrato
   canônico do pacote.

A remoção segura deve usar uma matriz canônica por família de artefato, e não
uma regra global como “remover todo schema v1”. Cada família precisa declarar
um único formato atual e rejeitar explicitamente qualquer outro formato antes
de realizar writes.

O resultado permanece parcial porque a autoridade da árvore `goose/**` está
indefinida e o validator material de instalação já está vermelho por drift
anterior: 6 de 17 testes falham.

## Entrega e imutabilidade

- Demanda: [demanda.md](demanda.md)
- Relatório: este arquivo
- Escritas realizadas: somente criação deste relatório, após solicitação
  explícita
- Mutação do catálogo analítico: `false`
- Alterações em consumidores: `false`
- Runtime ou instalação modificados: `false`

## Objetivo, escopo e limites

O objetivo foi inventariar toda compatibilidade legada do Loki e estabelecer a
base técnica para convergir a um único contrato suportado por família de
artefato.

Foram incluídos:

- contratos agentic, evidence e analytic inference;
- instalação, remoção e manifests gerados;
- validators, fixtures, templates e mirrors;
- documentação, `manifest.yaml` e `install-scopes.json`;
- projections Codex, Claude Code e Goose.

Ficaram excluídos:

- mudanças em consumidores sem aprovação;
- migração automática de planos, evidências ou instalações existentes;
- remoção de compatibilidade funcional de domínios externos;
- implementação, commit, publicação ou Pull Request;
- leitura de estados privados de consumidores externos.

## Evidências e descoberta de superfícies

| Tecnologia ou domínio | Contrato observado | Superfícies | Confiança | Limitação |
| --- | --- | --- | --- | --- |
| Install scopes | atual 2; leitor 1/2 | installer, validators, docs | alta | consumidores não inspecionados |
| Agentic state | manifest 4, report 5, digest 4 | templates e validator XML | alta | schemas anteriores ainda aceitos |
| Session evidence | schema 1 atual | templates, collector, validator | alta | schema pouco fechado |
| Analytic inference | layout XML v2; contratos lógicos schema 1 | catálogo, eventos, migration reader | alta | fixtures JSON ambíguas |
| Codex/Claude | projections e instalação manual | agents, TOML, README | alta | paridade semântica parcial |
| Goose | 7 recipes, 5 agents, 8 skills | `goose/**` | média | autoridade e instalação indefinidas |
| RPG Maker/VisuStella | domínio externo | skill opcional | alta | deve ser preservado |

### Fontes principais

- `scripts/validate-agentic-run-state.py`
- `scripts/install-loki-symlinks.py`
- `scripts/validate-install-scopes.py`
- `scripts/validate-install-loki-upgrade.py`
- `skills/lf-analytic-inference/**`
- `skills/loki-retrospectiva-tecnica/**`
- `skills/lf-index-navigator/**`
- `templates/**`
- `skills/lf-template-library/references/templates/**`
- `agents/**` e `codex/agents/**`
- `goose/**`
- `manifest.yaml`, `install-scopes.json`, `README.md` e `docs/**`

Não houve pesquisa externa. A evidência local é suficiente para inventariar o
pacote, mas não para confirmar o contrato oficial atual de instalação e recipes
do Goose.

## Política e catálogo analítico

- Policy ID: `analytic-inference-policy-v1`
- Digest verificado:
  `cadff64025e7fc0dc6dfc3be7b225c31d42fb9714e6628935dc7b25ddc2d7130`
- Fan-out máximo: `2`
- Budget de investigação: `6`
- Timeout: `3` ticks
- Floors solicitados: não configurados
- Estado do catálogo: carregado e válido
- Serialização viva: XML v2
- Mutação aplicada: `false`

Foi carregado seletivamente o record
`ai-dc760ee701cf635634b5b6ba027c9e4dac67a5f39f8da94e4d6f09ed433815c8/rev-1`.
Ele disciplina aprovações exatas de migração, mas não foi reutilizado como
resposta direta porque a demanda atual pretende eliminar a operação de
migração. Seus invariantes genéricos de aprovação continuam relevantes para
outras operações destrutivas.

## Achados materiais

### 1. Não existe uma única versão global de schema

`schema_version=1` não significa automaticamente legado. Session evidence,
execution knowledge e write-test-review ainda usam schema 1 como formato
atual, enquanto outras famílias usam versões superiores.

O corte precisa declarar uma matriz como:

| Família | Formato canônico observado |
| --- | --- |
| Agentic run manifest | 4 |
| Agent run report | 5 |
| Agentic digest | 4 |
| Write-test-review | 1 |
| Session evidence | 1 |
| Execution knowledge | 1 |
| Analytic inference persisted layout | XML v2 |
| Install scopes | 2 |

A regra transversal deve ser: somente o valor listado para aquela família é
aceito; qualquer outro valor ou shape falha explicitamente antes de writes.

### 2. O validator agentic mantém leitores legados

`scripts/validate-agentic-run-state.py` declara
`EVIDENCE_SCHEMAS = {"2", "3", "4", "5"}` e contém uma fixture antiga cuja
validação bem-sucedida é obrigatória. Schemas desconhecidos também conseguem
evitar partes de checks condicionais por não existir uma rejeição global e
fechada para cada root.

Os templates ainda emitem `legacy_reader_optional="true"` em:

- `templates/agentic-run-manifest-template.xml`;
- `templates/agent-run-report-template.xml`;
- `templates/agentic-run-digest-template.xml`;
- mirrors correspondentes em `lf-template-library`.

O contrato de orchestration ainda contém texto histórico dizendo que readers
retêm schema 1 e writers emitem schema 2, embora os templates atuais já estejam
em 4/5/4.

### 3. Evidência ainda carrega campos de política legada

O template de session evidence persiste:

- `automatic_agent_retrospective=false`;
- `dual_capture=false`;
- `legacy_retrospective_fallback=false`.

O manifest agentic também contém `legacy_retrospective_fallback=false`.

Remover somente esses campos seria insuficiente: o validator atual não fecha
integralmente a gramática dessa política. O corte deve substituir esses campos
por uma regra positiva e fechada que preserve a proibição de retrospectiva
automática, captura dupla e fallback.

### 4. A retrospectiva ainda aceita um input público legado

`skills/loki-retrospectiva-tecnica` ainda declara `operational_trace` como
input contextual, embora `execution_evidence_sources` seja o caminho atual.

O contrato final deve remover `operational_trace` do input suportado e possuir
fixture negativa que o rejeite explicitamente.

### 5. Analytic inference ainda possui leitor v1 executável

`skills/lf-analytic-inference` conserva:

- schemas JSON legados de registry, catalog e event;
- regras de leitura read-only de `.loki/analytic-inference/v1/**`;
- validação completa de registry, records, eventos, lineage e collisions;
- geração de proposta copy-only v1 → v2;
- operação CLI `migration-dry-run`.

Remover apenas os arquivos de schema não elimina a compatibilidade. É
necessário retirar o reader, a operação CLI, os contratos, as referências em
workflows e as fixtures de sucesso associadas.

Algumas fixtures JSON continuam sendo atuais porque exercitam o control plane
ou o codec XML. Elas não devem ser removidas apenas por serem JSON. Já fixtures
como `catalog-empty.json`, `catalog-invalid.json` e `catalog-limit.json`
precisam ser classificadas individualmente como atuais, obsoletas ou futuros
casos de rejeição.

### 6. O instalador contém uma implementação completa de migração

`scripts/install-loki-symlinks.py` e
`scripts/validate-install-scopes.py` aceitam schemas 1 e 2. O instalador ainda
contém:

- branch `artifacts.commands` para schema 1;
- flag `--cleanup-legacy-commands`;
- descoberta e validação de `.agents/commands/loki/**`;
- planejamento, revalidação e aplicação de cleanup;
- histórico `removed_legacy_links` no manifest gerado;
- migração de diretório de skill contendo somente symlink `SKILL.md`;
- tratamento de parent directory symlinks legados.

Há ainda risco de aceitação silenciosa: `artifacts.commands` é validado para
schema 1, mas não se transforma em `LinkSpec` no contrato atual.

Os casos de parent symlink, arquivo real e destino consumer-owned não devem
simplesmente desaparecer dos testes. Eles devem permanecer como casos negativos
de segurança e non-interference, sem cleanup automático.

### 7. O fallback documental do consumidor ainda é público

`skills/lf-index-navigator` usa `docs/index.xml` como contrato atual, mas procura
`index.md` quando o catálogo XML não existe. Esse fallback do consumidor deve
ser removido e substituído por falha explícita.

O `index.md` localizado na raiz deste pacote é uma superfície canônica do
framework segundo `docs/source-boundaries.md` e deve ser preservado.

### 8. Codex e Claude não têm a mesma cobertura observável

Existem 25 agents Markdown e 25 TOMLs Codex com nomes pareados. A inspeção
encontrou:

- 19 TOMLs incorporando a fonte Markdown exata;
- 2 com fonte incorporada mas drift textual;
- 4 projections custom cuja validação atual cobre principalmente nome e shape
  superior, não paridade semântica completa.

Claude Code usa cópia manual filtrada por `install-scopes.json`. O README manda
copiar templates, mas `manifest.claude_code_target` não declara templates e não
existe validator equivalente ao instalador Codex.

As contagens publicadas no README também estão desatualizadas.

### 9. Goose é uma projection transicional sem autoridade definida

A árvore rastreada contém:

- 7 recipes;
- 5 agents;
- 8 skills.

Ela não aparece em `manifest.yaml`, `install-scopes.json`, README, source
boundaries, operational inventory ou no instalador.

Seis recipes têm counterpart em comandos root. A recipe
`loki-migrate-command-to-recipe` não possui counterpart canônico e existe
justamente para migrar Loki/Codex/Claude para Goose, mantendo os artefatos root
como fontes de compatibilidade até depreciação.

Isso conflita com `docs/source-boundaries.md`, que define o pacote raiz como
fonte canônica. A recipe também aponta por padrão para
`docs/goose-command-recipe-migration-reference.md`, arquivo inexistente.

Antes do plano, é necessário decidir se Goose será:

1. projection oficialmente suportada e semanticamente validada a partir das
   fontes root; ou
2. removida do inventário ativo como artefato transicional/histórico.

Manter Goose como segunda fonte canônica não é compatível com o objetivo de um
único contrato.

### 10. O baseline de instalação já está vermelho

`python3 scripts/validate-install-loki-upgrade.py` executou 17 testes e falhou
em 6. As falhas são anteriores ao corte proposto:

- contagens esperadas 92/61/101 versus contagens atuais 99/68/108;
- manifest esperado 92 versus 99;
- dependências esperadas de `loki-agentic-development` desatualizadas.

Os dry-runs atuais resultam em:

| Profile | Skills | Agents | Codex agents | Templates | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| consumer | 52 | 23 | 23 | 1 | 99 |
| package-source | 43 | 12 | 12 | 1 | 68 |
| all | 57 | 25 | 25 | 1 | 108 |

Esse baseline deve ficar verde antes da remoção, preferencialmente derivando
expectativas de `install-scopes.json` em vez de manter constantes frágeis.

## Achados negativos e preservações obrigatórias

- Não foi encontrada operação que aplique automaticamente a migração de
  inferência v1; existe proposta/dry-run, não apply.
- Execution knowledge schema 1 é atual e já rejeita outras versões.
- Regras nos command routers que proíbem legacy paths são invariantes atuais de
  rejeição, não compatibilidade a remover.
- Fallback GitHub MCP → `gh`, degradação serial quando fan-out não está
  disponível e degradação tipada de adapters são estratégias operacionais, não
  retrocompatibilidade.
- Compatibilidade RPG Maker/VisuStella, load order, saves e migração de dados de
  jogos são funcionalidade de domínio externo e permanecem fora do corte.
- Os 18 pares de templates raiz ↔ `lf-template-library` estão byte-identical e
  essa paridade deve ser preservada.
- `frameworks-de-referencia/**` é fonte externa não normativa e não deve ser
  reescrita por este trabalho.

## Alternativas

| Alternativa | Resultado |
| --- | --- |
| Matriz canônica por artefato e fixtures negativas antes do corte | **Recomendada** |
| Remover globalmente `v1`, `fallback`, `compatibility` ou `migration` | Rejeitada: falsos positivos e regressões |
| Manter readers antigos temporariamente | Rejeitada: perpetua dois contratos |
| Fazer apenas limpeza documental | Rejeitada: branches executáveis permanecem |
| Converter Goose em projection governada semanticamente | Recomendada, condicionada à decisão de autoridade |
| Remover Goose sem decisão explícita | Rejeitada: pode apagar uma superfície suportada |

## Estratégia técnica recomendada

1. Documentar uma matriz canônica por família de artefato.
2. Fechar os validators para rejeitar qualquer versão, atributo ou child não
   listado no contrato atual.
3. Criar primeiro fixtures negativas para cada formato legado conhecido.
4. Restaurar o baseline verde de instalação.
5. Remover readers, flags, CLI operations e branches de migração.
6. Remover inputs e fallbacks públicos legados.
7. Atualizar templates raiz e mirrors na mesma mudança.
8. Atualizar Codex, Claude e a projection Goose conforme a decisão aprovada.
9. Atualizar `manifest.yaml`, `install-scopes.json`, README, docs e inventários.
10. Executar scans proibidos e todos os validators de integridade.

Casos antigos devem falhar com mensagens estáveis e antes de qualquer write.
Não deve haver cleanup ou migração implícita.

## Candidates investigados

| Candidate | Estado | Resultado |
| --- | --- | --- |
| `gen-032-contract-state` | selected, investigated, validated | readers antigos continuam executáveis |
| `gen-032-install-projection` | selected, investigated, validated | installer e Goose mantêm transição ativa |
| `gen-032-baseline-drift` | selected, investigated, validated | validator de upgrade já possui 6 falhas |

Esses candidates permanecem `unreviewed` para fins de promoção durável. Este
relatório não autoriza mutação do catálogo.

## Investigações delegadas

| Handoff | Agent run | Evidence | Escopo | Estado |
| --- | --- | --- | --- | --- |
| `ho-032-contract-001` | `ar-032-contract-001` | `ev-032-contract-001` | agentic/evidence/inference | complete |
| `ho-032-delivery-001` | `ar-032-delivery-001` | `ev-032-delivery-001` | instalação/docs/projections/Goose | complete |

As duas investigações foram read-only, independentes e respeitaram o fan-out
máximo de 2. Não houve transcript bruto persistido nem métricas confiáveis de
token/tool usage; custos desconhecidos não foram tratados como zero.

## Validators executados

| Validator | Estado | Evidência |
| --- | --- | --- |
| catálogo de inferência | passed | registry/index/record válidos |
| `validate-agentic-run-state.py --self-test` | passed | confirma inclusive fixture legada positiva |
| `validate-install-scopes.py` | passed | contrato dual é aceito hoje |
| `validate-install-loki-upgrade.py` | **failed** | 6 de 17 testes falharam |
| `validate-loki-init-catalogador-contracts.py --enforce-current-tree` | passed | 31 templates, 27 positivos, 15 negativos, 29 pares |
| dry-runs de instalação | passed | totais 99/68/108 |
| paridade de templates | passed | 18/18 byte-identical |
| parse YAML Goose | passed | 7/7 recipes |
| zero mutation do catálogo | passed | hashes permaneceram iguais |

## Riscos e gaps

- Uma remoção lexical ampla pode quebrar schemas atuais e fallbacks
  operacionais necessários.
- Remover os testes de cleanup sem preservar testes de non-interference pode
  permitir tocar arquivos consumer-owned.
- A projection Goose pode continuar divergindo do pacote raiz.
- Remover campos `legacy_*=false` sem fechar o schema pode enfraquecer, em vez
  de fortalecer, a proibição.
- A paridade semântica das projections Codex custom ainda não é comprovada.
- Não existe validator geral de cobertura Goose ou da instalação Claude.
- A prevalência de formatos legados em consumidores não foi medida e não muda
  o contrato final, mas afeta comunicação de breaking change.

## Gates e roteamento

| Destino | Permitido | Condição |
| --- | --- | --- |
| `loki-human-decision-preflight` | **sim** | decidir autoridade de `goose/**` |
| investigação adicional | sim | pesquisa oficial Goose e classificação das fixtures ambíguas |
| `loki-generate-action-plan` | ainda não | decisão Goose aprovada e baseline de instalação verde |
| `loki-continuous-improvement` | sim | apenas avaliação; nunca promoção automática |

## Próximos passos

1. Executar `loki-human-decision-preflight` para classificar `goose/**` como
   projection suportada ou artefato transicional a remover.
2. Restaurar `validate-install-loki-upgrade.py` ao baseline verde, sem ainda
   alterar o comportamento legacy.
3. Gerar o plano executável com fixtures negativas antes das remoções.
4. Exigir technical review antes de qualquer mudança no pacote.
5. Validar instalações somente em destino explicitamente aprovado.

## Resume state

```yaml
deep_analysis_resume_state:
  status: partial
  delivery_mode: report-artifact
  report_destination: planos/032-remove-legacy-compatibility/analise.md
  objective: Remove Loki legacy compatibility and converge each artifact family on one supported contract.
  policy_id: analytic-inference-policy-v1
  policy_digest: cadff64025e7fc0dc6dfc3be7b225c31d42fb9714e6628935dc7b25ddc2d7130
  completed_stages:
    - preflight
    - technology-discovery
    - selective-catalog-retrieval
    - candidate-expansion
    - specialist-investigation
    - consolidation
    - zero-mutation-validation
  terminal_handoffs:
    - ho-032-contract-001
    - ho-032-delivery-001
  candidate_decisions:
    - gen-032-contract-state:selected-validated
    - gen-032-install-projection:selected-validated
    - gen-032-baseline-drift:selected-validated
  validator_outcomes:
    - analytic-inference-catalog:passed
    - agentic-run-self-test:passed
    - install-scopes:passed
    - install-upgrade:failed-6-of-17
    - catalogador-current-tree:passed
    - template-mirrors:passed
    - goose-yaml:passed
  blockers:
    - goose-authority-unresolved
    - install-upgrade-validator-red
  next_destination: loki-human-decision-preflight
  minimum_next_path: Decide Goose authority, then restore the installation validator baseline.
```
