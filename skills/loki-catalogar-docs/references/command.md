---
name: loki:catalogar-docs
type: command
status: draft
domain: documentation
required_skills: []
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - ambiguous documentation target or ownership
    - recursive tree near command limits
    - conflicting target_files or shared index writes
    - durable consumer documentation changes without recorded approval
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:catalogar-docs

## Purpose

Catalogar documentacao duradoura do consumidor em `/docs`, acionando
`catalogador` com envelope escopado, validacao de caminho, limites de recursao,
processamento bottom-up e consolidacao serial de `docs/index.xml`.

## Inputs

- `DOCS_DIR`: caminho obrigatorio do diretorio de documentacao a catalogar,
  preferencialmente relativo ao workspace.
- `RECURSIVE`: flag opcional, padrao `true`; quando `false`, catalogar somente
  `DOCS_DIR`.
- `LARGE_TREE_CONFIRMATION`: confirmacao humana obrigatoria quando a descoberta
  encontrar mais de 20 e ate 100 diretorios.
- `OUT_OF_DOCS_APPROVAL`: decisao explicita obrigatoria para qualquer alvo fora
  de `/docs`; sem esta decisao, o comando rejeita o alvo.
- Decisoes humanas ja registradas, quando o comando for executado dentro de um
  plano Loki ou outro workflow com estado retomavel.

## Outputs

- Resumo de diretorios catalogados, diretorios pulados e exclusoes aplicadas.
- Lista de arquivos criados ou atualizados, incluindo `docs/index.xml` quando
  houver consolidacao de catalogo.
- Avisos sobre conflitos, alvos fora de `/docs`, limites de arvore, documentos
  obsoletos ou lacunas que exigem decisao humana.
- Logs resumidos de handoffs para `catalogador`; nao incluir output bruto longo
  de cada invocacao.
- Estado retomavel com inputs normalizados, arvore descoberta, batches
  bottom-up, `target_files`, validadores, gates e proximo passo.

## Allowed Writes

- Somente arquivos de documentacao duradoura do consumidor explicitamente
  declarados no envelope aprovado:
  - `docs/**/*.md`;
  - `docs/index.xml`;
  - outros arquivos de documentacao dentro de `DOCS_DIR` somente quando
    `OUT_OF_DOCS_APPROVAL` registrar que o alvo e documentacao duradoura do
    consumidor.
- Reports transitorios do plano ativo apenas quando um workflow chamador
  declarar o destino exato em `target_files`.

Toda escrita deve ter `target_files`, `allowed_writes`, `write_mode`,
`scoped_write_domains`, validators e gates antes de chamar `catalogador`.

## Forbidden Writes

- `.claude/**`
- `.agents/**`
- `.codex/**`
- Caminhos absolutos externos ao workspace.
- Traversal que resolva para fora do workspace.
- Diretorios de codigo-fonte, runtime, engine, dados, assets, build ou
  configuracao que nao sejam documentacao duradoura aprovada.
- Criar `index.md` por diretorio como comportamento padrao; a primeira versao
  usa `docs/index.xml` como catalogo primario.
- Escrita paralela em `docs/index.xml` ou em qualquer indice de diretorio pai.

## Required Skills

- Nenhuma skill tecnica e obrigatoria por default.
- Carregar `lf-index-navigator` quando for necessario navegar ou auditar um
  `docs/index.xml` existente antes de montar envelopes.
- Carregar `<technology_required_skills>` somente quando o conteudo do
  consumidor exigir validacao especializada.

## Execution Profile

- `model_class`: `frontier_reasoning`.
- `default_effort`: `high`.
- `max_effort`: `xhigh`.
- `escalation_signals`: alvo documental ambiguo, arvore grande, conflito de
  `target_files`, escrita duradoura sem approval registrado ou divergencia entre
  documentos e `docs/index.xml`.
- `handoff_effort`: leitura e validacao em `medium`, documentacao duradoura em
  `high`, logs transitorios em `low`.
- `adapter_projection`: metadados sao intencao provider-neutral; Codex deve
  trata-los como consultivos salvo projecao em perfil, invocacao ou custom
  agent.

## Handoffs

- `catalogador` em modo `scoped-writer` somente quando o comando entregar
  envelope explicito com:
  - `command: loki:catalogar-docs`;
  - `write_mode: task_scoped_writer`;
  - `target_files` exatos;
  - `allowed_writes` iguais ou mais restritos que `target_files`;
  - `scoped_write_domains: ["consumer-docs", "docs-index"]`;
  - `validators`;
  - `human_gates`;
  - fontes lidas e diretorio alvo.
- `catalogador` em modo `proposal-only` quando approval de escrita ainda estiver
  ausente, quando `target_files` nao forem comprovadamente disjuntos ou quando
  o batch tocar `docs/index.xml`.

O agente nao decide escopo, recursao, paralelismo, limites ou permissao de
escrita. Essas decisoes pertencem a este comando.

## Workflow

1. Normalizar `DOCS_DIR` e `RECURSIVE`. Se faltar entrada obrigatoria, fazer
   `interview` antes de qualquer descoberta.
2. Resolver `DOCS_DIR` contra o workspace real. Rejeitar caminho absoluto
   externo, symlink ou traversal que saia do workspace.
3. Confirmar que o caminho existe, e diretorio e pertence a documentacao
   duradoura do consumidor. Alvos fora de `/docs` exigem `OUT_OF_DOCS_APPROVAL`
   e evidencia de que nao sao codigo-fonte, runtime, build ou configuracao.
4. Aplicar exclusoes deterministicas: `.git/`, `node_modules/`, `dist/`,
   `build/`, `.next/`, `.cache/`, `.turbo/` e `coverage/`.
5. Quando `RECURSIVE` for `true`, mapear a arvore ate profundidade maxima 10.
   Abortar acima de 100 diretorios. Exigir `LARGE_TREE_CONFIRMATION` acima de
   20 diretorios.
6. Montar ordem bottom-up, das folhas para o diretorio raiz. Quando
   `RECURSIVE` for `false`, usar somente `DOCS_DIR`.
7. Para cada nivel bottom-up, calcular `target_files` antes de qualquer
   handoff. Permitir paralelismo apenas quando os envelopes do mesmo nivel
   tiverem `target_files` disjuntos e nao tocarem `docs/index.xml` nem indice
   de diretorio pai.
8. Rodar handoffs independentes do `catalogador` somente dentro dos envelopes
   aprovados. Consolidar retornos antes de subir para o proximo nivel.
9. Serializar qualquer escrita em `docs/index.xml` ou indice pai em uma etapa
   unica, depois que os lotes filhos terminarem ou entregarem propostas.
10. Executar validators, registrar avisos e produzir resumo final com arquivos
    afetados, gates pendentes e estado retomavel.

## Validators

- O caminho resolvido existe, e diretorio e permanece dentro do workspace.
- O alvo pertence a `/docs` ou possui `OUT_OF_DOCS_APPROVAL` registrado.
- A descoberta nao inclui `.git/`, `node_modules/`, `dist/`, `build/`,
  `.next/`, `.cache/`, `.turbo/` ou `coverage/`.
- A profundidade descoberta e menor ou igual a 10.
- O total de diretorios e menor ou igual a 100.
- `LARGE_TREE_CONFIRMATION` existe quando o total de diretorios e maior que 20.
- Todo handoff para `catalogador` contem `target_files`, `allowed_writes`,
  `write_mode`, `scoped_write_domains`, validators e gates.
- Batches paralelos possuem `target_files` disjuntos.
- `docs/index.xml` e indices pais sao escritos somente em etapa serial.
- Quando `docs/index.xml` for alterado, o XML resultante e parseavel e contem
  `path`, `summary`, `use_when`, `not_covered`, `keywords` e `sections` para os
  documentos catalogados.

## Human Gates

- `interview` quando `DOCS_DIR`, `RECURSIVE` ou a classificacao do alvo estiver
  ambigua.
- `approval` antes de qualquer escrita em documentacao duradoura do consumidor.
- `approval` especifico para alvo fora de `/docs`.
- `human-validation` quando o usuario precisar revisar a coerencia final do
  catalogo ou aceitar alteracoes em conteudo duradouro.
- `technical-review` para mudancas neste contrato, no wrapper da skill, no
  agente `catalogador`, em roteamento, manifestos, escopos de instalacao ou
  validadores do pacote.

## Packaging Checks

- `commands/loki-catalogar-docs.md` usa namespace `loki:` e frontmatter de
  comando.
- `skills/loki-catalogar-docs/SKILL.md` existe como wrapper com o mesmo stem.
- `skills/loki-catalogar-docs/references/command.md` esta sincronizado com este
  contrato.
- `manifest.yaml`, `install-scopes.json`, `docs/operational-inventory.md` e o
  roteador compartilhado sao atualizados quando o comando for aceito no pacote.
- `find skills -maxdepth 2 -name SKILL.md | sort` lista o wrapper.
- `find skills -maxdepth 1 -type f -name '*.md'` nao retorna arquivos soltos.
- O scan focado de referencias proibidas nao encontra dependencia normativa em
  `.claude/**`, `.agents/**`, `.codex/**`, caminho local de usuario ou plano
  historico.

## Stop Conditions

- `DOCS_DIR` ausente, ambiguo, inexistente, nao diretorio ou fora do workspace.
- O alvo esta fora de `/docs` sem `OUT_OF_DOCS_APPROVAL`.
- O alvo e diretorio de codigo-fonte, runtime, engine, dados, assets, build ou
  configuracao, salvo decisao humana explicita e escopo documental claro.
- A arvore excede profundidade 10.
- A arvore excede 100 diretorios.
- A arvore tem mais de 20 diretorios sem `LARGE_TREE_CONFIRMATION`.
- Um batch paralelo nao prova `target_files` disjuntos.
- Qualquer escrita em `docs/index.xml` ou indice pai foi planejada em paralelo.
- Falta envelope explicito para `catalogador`.
- Falta `approval` para escrita duradoura.
- Um validator falha ou fica inconclusivo.
- A execucao exigiria escrever em `.claude/**`, `.agents/**` ou `.codex/**`.

## Resume Contract

Manter `LokiCatalogarDocsState` ou resumo equivalente com:

- inputs originais e normalizados;
- workspace root e `DOCS_DIR` resolvido;
- decisao de recursividade;
- exclusoes aplicadas;
- arvore descoberta, profundidades e total de diretorios;
- batches bottom-up;
- envelopes entregues ao `catalogador`;
- `target_files`, `allowed_writes` e conflitos detectados;
- validators executados e resultados;
- gates humanos pendentes;
- arquivos afetados;
- proximo passo seguro.

Se a execucao parar, registrar `blocked_by`, validator ou gate exato antes de
retomar.
