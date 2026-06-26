---
title: Instalacao do Loki Framework em Claude Code e Codex
date: 2026-06-26
status: pesquisa
topic: loki-framework-install
scope: distribuicao-local
sources:
  - https://code.claude.com/docs/en/skills
  - https://code.claude.com/docs/en/plugins
  - https://code.claude.com/docs/en/plugin-marketplaces
  - https://code.claude.com/docs/en/discover-plugins
  - https://code.claude.com/docs/en/commands
  - https://developers.openai.com/codex/skills
  - https://developers.openai.com/codex/plugins
  - https://developers.openai.com/codex/plugins/build
  - https://developers.openai.com/codex/subagents
  - https://developers.openai.com/codex/custom-prompts
  - https://developers.openai.com/codex/import
  - https://developers.openai.com/codex/guides/agents-md
---

# Instalacao do Loki Framework em Claude Code e Codex

## Pergunta

Qual e a melhor forma de instalar
`/Users/edney/projects/coreto/summer26/docs/05-Loki-Framework/002-loki-framework-local`
em um projeto consumidor, deixando comandos, skills e agentes prontos para uso
no Claude Code e no Codex?

A hipotese inicial era criar um plugin no marketplace do Codex. A pesquisa
comparou essa opcao com instalacao local por copia/sync, skills standalone,
plugins Claude Code, plugins Codex e marketplaces locais.

## Resposta curta

A melhor solucao inicial nao e comecar por marketplace. O caminho mais seguro e
criar um instalador/adaptador local do Loki Framework que usa o pacote atual
como fonte canonica e instala cada superficie no destino correto de cada
ferramenta.

Recomendacao:

1. Manter `002-loki-framework-local` como fonte auditavel.
2. Criar um instalador local com `--dry-run`, `--apply`, `--target` e
   `--surfaces claude,codex`.
3. Para Claude Code, instalar inicialmente como configuracao standalone em
   `.claude/`.
4. Para Codex, instalar skills em `.agents/skills` e converter agentes para
   `.codex/agents/*.toml`.
5. Depois que o pacote estabilizar, gerar plugin Claude Code.
6. Depois, gerar plugin Codex focado em skills e dependencias opcionais.
7. Marketplace entra apenas para distribuicao versionada entre projetos ou
   pessoas.

## Fontes locais analisadas

- [[05-Loki-Framework/002-loki-framework-local/README|README do pacote Loki local]]
- [[05-Loki-Framework/002-loki-framework-local/manifest.yaml|Manifest do pacote Loki local]]
- [[05-Loki-Framework/002-loki-framework-local/docs/usage-guide|Guia de uso]]
- [[05-Loki-Framework/002-loki-framework-local/docs/operational-inventory|Inventario operacional]]
- [[05-Loki-Framework/002-loki-framework-local/docs/source-boundaries|Limites de fonte]]

O pacote local ja esta estruturado como um pacote operacional:

```text
002-loki-framework-local/
|-- manifest.yaml
|-- README.md
|-- agents/
|-- commands/
|-- skills/
|-- templates/
`-- docs/
```

Inventario observado:

- 7 comandos Loki em `commands/*.md`.
- 12 skills em `skills/*/SKILL.md`.
- 7 agentes em `agents/*.md`.
- Templates de tarefas, analise tecnica, contrato de comando e indice de docs.
- Documentacao de guardrails, workflows, limites e uso.

## Achados sobre Claude Code

Claude Code trata skills como extensoes reutilizaveis que podem ser invocadas
diretamente com `/skill-name` e tambem descobertas automaticamente quando
relevantes. A documentacao atual tambem registra que comandos customizados
foram incorporados ao modelo de skills: um arquivo em `.claude/commands/deploy.md`
e uma skill em `.claude/skills/deploy/SKILL.md` podem produzir o mesmo comando
`/deploy`, e os comandos antigos em `.claude/commands/` continuam funcionando.

Isso implica que o pacote Loki pode continuar instalando `commands/*.md` em
`.claude/commands/loki/` no curto prazo, mas a direcao mais moderna e migrar os
fluxos principais para skills com `SKILL.md`, mantendo comandos como wrappers
ou atalhos quando isso melhorar a ergonomia.

Claude Code tambem tem plugins. Plugins podem empacotar skills, agents, hooks e
MCP servers em diretorios autocontidos. A propria documentacao recomenda:

- usar configuracao standalone em `.claude/` para workflows pessoais,
  customizacao de um unico projeto e experimentacao;
- usar plugins quando a funcionalidade precisa ser compartilhada, versionada,
  reutilizada entre projetos ou distribuida por marketplace.

Claude Code tambem tem marketplace. Um marketplace e um catalogo de plugins.
Ele nao instala tudo automaticamente: primeiro o marketplace e adicionado, depois
cada plugin e instalado. Para publicar um marketplace local ou privado, a
estrutura usa `.claude-plugin/marketplace.json`.

### Implicacao para o Loki em Claude Code

Para o Loki, o melhor ciclo e:

1. Instalar standalone em `.claude/` enquanto o pacote ainda esta mudando.
2. Validar nomes, triggers, outputs, agents e templates em projetos reais.
3. Converter para plugin Claude Code quando o formato estabilizar.
4. Criar marketplace Claude Code apenas quando houver distribuicao para varios
   projetos ou usuarios.

## Achados sobre Codex

Codex tambem usa skills como formato principal de workflows reutilizaveis. A
documentacao atual diz que skills sao o formato de autoria para workflows e
plugins sao a unidade de distribuicao instalavel quando se quer compartilhar ou
empacotar skills com apps, MCP ou outros componentes.

Para descoberta local, Codex le skills em:

- `.agents/skills` no projeto ou em diretorios pais ate a raiz do repo;
- `$HOME/.agents/skills`;
- `/etc/codex/skills`;
- skills de sistema embutidas.

Codex tambem suporta plugins e marketplaces. Para plugins locais ou de repo, a
documentacao usa marketplaces em `.agents/plugins/marketplace.json` ou
`~/.agents/plugins/marketplace.json`, apontando para diretorios de plugin. O
plugin precisa de `.codex-plugin/plugin.json`.

Ponto critico: prompts customizados do Codex ainda existem, mas estao
depreciados. Eles funcionam como slash commands em `~/.codex/prompts`, mas a
documentacao recomenda usar skills para workflows reutilizaveis. Portanto, nao
vale projetar `loki:tech-analysis`, `loki:run-plan` e similares como prompts
Codex de longo prazo. Eles devem virar skills ou skill wrappers.

Codex tambem tem agentes customizados, mas o formato nao e o mesmo dos agentes
Markdown do Claude Code. Para Codex, agentes customizados ficam em arquivos TOML
standalone sob:

- `.codex/agents/` para agentes de projeto;
- `~/.codex/agents/` para agentes pessoais.

Cada arquivo TOML precisa declarar pelo menos:

- `name`;
- `description`;
- `developer_instructions`.

### Implicacao para o Loki em Codex

O mapeamento atual do README do pacote para Codex precisa ser corrigido. Ele
sugere staging em:

```text
.agents/commands/
.agents/agents/
.agents/skills/
```

Pelo que a documentacao atual do Codex descreve, somente `.agents/skills/` e um
destino oficial para skills de repo. Para Codex, o destino recomendado deve ser:

```text
.agents/skills/loki-*/
.codex/agents/*.toml
AGENTS.md
```

Os arquivos `commands/*.md` do Loki nao devem ser tratados como uma superficie
Codex primaria. Eles devem ser convertidos para skills invocaveis ou para
documentacao de workflow usada pelas skills. Se houver necessidade de atalho
manual estilo slash command em Codex, `~/.codex/prompts` pode existir como
compatibilidade pessoal, mas nao deve ser o caminho canonico porque prompts
customizados estao depreciados.

## Comparativo de opcoes

| Opcao | Serve para | Vantagens | Problemas | Recomendacao |
| --- | --- | --- | --- | --- |
| Copia manual para `.claude/` e `.agents/` | Teste rapido | Simples, auditavel, sem packaging | Erro humano, mapeamento divergente, dificil rollback | Usar apenas como MVP controlado |
| Instalador local com dry-run | Uso em varios projetos locais | Repetivel, validavel, rollback possivel, preserva fonte unica | Precisa escrever script e conversores | Melhor proximo passo |
| Plugin Claude Code | Distribuir skills, commands/skills e agents no Claude Code | Nativo para Claude, versionavel, namespaced | Requer empacotar e validar | Fazer depois do instalador |
| Plugin Codex | Distribuir skills Codex, apps/MCP e talvez metadados | Bom para workflows Codex estaveis | Nao resolve diretamente commands Markdown nem agents Markdown | Fazer depois, focado em skills |
| Marketplace Codex | Catalogar plugins Codex para instalacao | Bom para time, repo ou pessoal com varios plugins | Overhead alto para iteracao inicial | Nao comecar por aqui |
| Marketplace Claude Code | Catalogar plugins Claude Code | Bom para distribuicao versionada | Overhead alto se ha um unico pacote em mudanca | Usar quando houver release |
| Global install | Tornar Loki disponivel em todos os projetos | Conveniente | Mistura contexto, aumenta risco, vai contra guardrails locais | Evitar |
| Symlink do pacote inteiro | Atualizacao instantanea | Rapido para desenvolvimento local | Pode quebrar caching de plugin e vazar dependencias externas | Usar so para dev, nao release |

## Mapeamento recomendado por artefato

### Skills Loki

Origem:

```text
002-loki-framework-local/skills/*/SKILL.md
```

Claude Code standalone:

```text
.claude/skills/<skill-name>/SKILL.md
```

Codex standalone:

```text
.agents/skills/<skill-name>/SKILL.md
```

Observacoes:

- Este e o artefato mais portavel entre Claude Code e Codex.
- As descricoes precisam ser curtas, especificas e com bons gatilhos, porque
  ambas as ferramentas usam descricoes para descoberta.
- Skills com referencias devem manter recursos dentro do proprio diretorio da
  skill para evitar caminhos quebrados em plugin/cache.

### Comandos Loki

Origem:

```text
002-loki-framework-local/commands/*.md
```

Claude Code standalone curto prazo:

```text
.claude/commands/loki/*.md
```

Claude Code recomendado medio prazo:

```text
.claude/skills/loki-<workflow>/SKILL.md
```

Codex recomendado:

```text
.agents/skills/loki-<workflow>/SKILL.md
```

Observacoes:

- Em Claude Code, comandos customizados antigos continuam funcionando, mas
  skills sao o caminho unificado atual.
- Em Codex, tratar comandos como skills e mais alinhado com a documentacao do
  que criar prompts customizados.
- O instalador pode gerar uma skill wrapper para cada comando Loki, preservando
  o nome conceitual `loki:feedback`, `loki:run-plan`, etc. no corpo da skill.

### Agentes Loki

Origem:

```text
002-loki-framework-local/agents/*.md
```

Claude Code standalone:

```text
.claude/agents/*.md
```

Codex recomendado:

```text
.codex/agents/*.toml
```

Conversao Codex proposta:

```toml
name = "runtime-qa"
description = "Avalia risco de QA e define checklist/evidencias sem validar runtime por conta propria."
developer_instructions = """
<conteudo normalizado de agents/runtime-qa.md>
"""
sandbox_mode = "read-only"
```

Observacoes:

- O frontmatter dos agentes Markdown Loki ja tem campos como `name`, `type`,
  `status` e `mode`. O instalador pode usar `mode: read-only` para sugerir
  `sandbox_mode = "read-only"` no Codex.
- Nem todo campo Claude Code tem equivalente direto em Codex; por isso a
  conversao deve ser explicita, nao uma copia cega.

### Templates Loki

Origem:

```text
002-loki-framework-local/templates/*
```

Claude Code standalone:

```text
.claude/templates/loki/
```

Codex recomendado:

```text
.agents/skills/<skill-name>/references/
```

ou dentro de um plugin Codex:

```text
plugins/loki-framework/skills/<skill-name>/references/
```

Observacoes:

- Codex nao tem, pela documentacao consultada, uma pasta global de templates de
  projeto equivalente a `.claude/templates`.
- Templates usados por skills Codex devem morar junto da skill ou dentro do
  plugin para continuar autocontidos.

### Documentacao do pacote

Origem:

```text
002-loki-framework-local/docs/*
```

Destino recomendado:

- manter no pacote fonte;
- incluir dentro do plugin quando virar release;
- copiar apenas docs de uso estritamente necessarias para o projeto consumidor.

Observacoes:

- O pacote ja declara que contexto especifico do projeto consumidor nao pertence
  ao Loki. Esse contrato deve continuar.
- `docs/index.xml` do projeto consumidor deve catalogar contexto duradouro do
  consumidor, nao regras internas do pacote Loki.

## Design recomendado do instalador

Nome sugerido:

```bash
scripts/install-loki
```

Interface sugerida:

```bash
scripts/install-loki \
  --package-root docs/05-Loki-Framework/002-loki-framework-local \
  --target /caminho/do/projeto \
  --surfaces claude,codex \
  --dry-run
```

Aplicacao:

```bash
scripts/install-loki \
  --package-root docs/05-Loki-Framework/002-loki-framework-local \
  --target /caminho/do/projeto \
  --surfaces claude,codex \
  --apply
```

Flags uteis:

- `--dry-run`: lista origem, destino e conflitos sem escrever.
- `--apply`: aplica copias/conversoes.
- `--surface claude`: instala apenas Claude Code.
- `--surface codex`: instala apenas Codex.
- `--mode standalone`: instala direto em `.claude/`, `.agents/` e `.codex/`.
- `--mode plugin`: gera estrutura de plugin.
- `--overwrite never|prompt|loki-only`: controla sobrescrita.
- `--rollback-file <path>`: grava manifesto de rollback.
- `--include-optional rpg-maker-mz`: instala extensoes opcionais.

### Regras do instalador

O instalador deve:

- ler `manifest.yaml` como inventario;
- recusar rodar se `--target` for igual ao pacote fonte;
- sempre ter `--dry-run` como comportamento padrao;
- criar um manifesto de instalacao com data, origem, destino e lista de arquivos;
- nao usar `rsync --delete`;
- nao apagar arquivos existentes sem marcador de origem Loki;
- nao instalar globalmente por padrao;
- nao copiar `.agents/` como fonte normativa;
- nao promover contexto do consumidor para dentro do pacote Loki;
- validar que cada skill tem `SKILL.md`, `name` e `description`;
- validar que cada agente Codex gerado tem `name`, `description` e
  `developer_instructions`;
- deixar claro quando reiniciar Claude Code ou Codex e necessario.

## Estrutura de saida recomendada

### Saida standalone Claude Code

```text
<target>/
|-- .claude/
|   |-- agents/
|   |   |-- bibliotecario.md
|   |   |-- catalogador.md
|   |   `-- ...
|   |-- commands/
|   |   `-- loki/
|   |       |-- loki-feedback.md
|   |       `-- ...
|   |-- skills/
|   |   |-- loki-feedback/
|   |   |-- loki-run-plan-execution/
|   |   `-- ...
|   `-- templates/
|       `-- loki/
`-- CLAUDE.md
```

### Saida standalone Codex

```text
<target>/
|-- .agents/
|   `-- skills/
|       |-- loki-feedback/
|       |-- loki-run-plan-execution/
|       `-- ...
|-- .codex/
|   `-- agents/
|       |-- bibliotecario.toml
|       |-- runtime-qa.toml
|       `-- ...
`-- AGENTS.md
```

### Roteamento minimo em `AGENTS.md`

Exemplo de bloco para projeto consumidor:

```md
## Loki Framework

When the user invokes Loki workflows, feedback diagnosis, technical analysis,
action-plan generation, plan execution, task enrichment, or technical
retrospectives, use the matching `loki-*` skills from `.agents/skills`.

Durable consumer project context belongs in `docs/**/*.md` and `docs/index.xml`.
Do not store project-specific business rules, lore, runtime facts, or local
decisions inside the Loki Framework package.

For Codex custom agents generated from Loki, use `.codex/agents/*.toml` only
when the user explicitly asks for subagent delegation or parallel agent work.
```

### Roteamento minimo em `CLAUDE.md`

Exemplo de bloco para projeto consumidor:

```md
## Loki Framework

Use Loki skills and commands for feedback diagnosis, technical analysis, action
plans, plan execution, task enrichment, retrospectives, and continuous
improvement.

Project-specific durable context belongs in `docs/**/*.md` and `docs/index.xml`.
Do not promote consumer context into the Loki package.

Prefer Loki skills for reusable procedures. `.claude/commands/loki/*` may be
used as command aliases or compatibility wrappers.
```

## Plugin Claude Code proposto

Quando o standalone estiver validado, a estrutura de plugin Claude Code pode
ser:

```text
loki-framework-plugin/
|-- .claude-plugin/
|   `-- plugin.json
|-- agents/
|-- skills/
|-- commands/
|-- hooks/
`-- docs/
```

Racional:

- Claude Code plugins sao adequados quando o objetivo e compartilhar, versionar
  e reutilizar entre projetos.
- Skills e agentes ficam namespaced pelo plugin, reduzindo colisao.
- Marketplace Claude Code pode listar esse plugin depois.

Ponto de atencao:

- Plugins instalados podem ser copiados para cache. Portanto, o plugin deve ser
  autocontido e nao depender de `../` para buscar templates ou docs fora do
  diretorio do plugin.

## Plugin Codex proposto

Quando houver estabilidade, a estrutura de plugin Codex pode ser:

```text
loki-framework-codex/
|-- .codex-plugin/
|   `-- plugin.json
|-- skills/
|   |-- loki-feedback/
|   |-- loki-run-plan-execution/
|   `-- ...
`-- docs/
```

Manifesto minimo conceitual:

```json
{
  "name": "loki-framework",
  "version": "0.1.0",
  "description": "Loki Framework workflows for feedback, technical analysis, action plans, execution, retrospectives, and continuous improvement.",
  "skills": "./skills/"
}
```

Marketplace Codex local de repo:

```text
<target>/
|-- .agents/
|   `-- plugins/
|       `-- marketplace.json
`-- plugins/
    `-- loki-framework/
```

Exemplo conceitual:

```json
{
  "name": "local-loki",
  "plugins": [
    {
      "name": "loki-framework",
      "source": {
        "source": "local",
        "path": "./plugins/loki-framework"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

Ponto de atencao:

- O plugin Codex resolve melhor a distribuicao de skills.
- Ele nao substitui automaticamente o formato `.codex/agents/*.toml`.
- Se agentes customizados Codex forem necessarios, o instalador ainda deve
  gerar esses TOML no projeto consumidor ou o pacote deve documentar um passo de
  importacao/conversao.

## Por que nao comecar por marketplace Codex

Marketplace e uma boa camada de distribuicao, mas nao e a melhor primeira
camada de autoria. A pesquisa indica que o problema imediato do Loki nao e
descoberta publica ou instalacao por catalogo; e compatibilidade entre
superficies diferentes:

- Claude Code aceita comandos Markdown, skills, agents e plugins.
- Codex prefere skills para workflows, TOML para custom agents e plugins para
  distribuicao.
- O pacote atual ainda tem `commands/*.md` como artefatos centrais.
- O README/manifest atual aponta destinos Codex que precisam ajuste.

Comecar por marketplace Codex criaria uma embalagem antes de corrigir o
mapeamento. O marketplace faria sentido depois que:

- comandos Loki forem expressos como skills ou wrappers;
- agentes Loki tiverem conversor para `.codex/agents/*.toml`;
- templates e docs necessarios estiverem autocontidos;
- o instalador conseguir validar a estrutura;
- houver uma versao estavel do pacote.

## Correcoes recomendadas no pacote atual

### README

Atualizar a secao Codex para substituir:

```text
.agents/commands/
.agents/agents/
.agents/skills/
```

por:

```text
.agents/skills/
.codex/agents/
AGENTS.md
```

Tambem explicar:

- comandos Loki viram skills no Codex;
- prompts customizados Codex sao apenas compatibilidade, nao destino canonico;
- agentes Markdown precisam conversao para TOML;
- templates Codex devem morar em `references/` das skills ou dentro do plugin.

### Manifest

Atualizar `install_policy.codex_target` para refletir destinos oficiais:

```yaml
codex_target:
  skills: ".agents/skills/"
  agents: ".codex/agents/"
  instructions: "AGENTS.md"
  command_workflows: ".agents/skills/"
```

Adicionar nota de conversao:

```yaml
codex_conversion:
  commands: "Convert command markdown to command-like skills; do not rely on deprecated custom prompts."
  agents: "Convert agent markdown to .codex/agents/*.toml with name, description, developer_instructions."
  templates: "Bundle templates under skill references or plugin-local docs."
```

### Skills

Garantir que todas as skills tenham:

- `name`;
- `description`;
- escopo de uso claro;
- quando nao usar;
- entradas;
- saidas;
- referencias autocontidas quando necessario.

### Agentes

Garantir que cada agente tenha:

- descricao curta para Claude Code;
- campo ou secao que permita gerar `description` Codex;
- corpo completo que possa virar `developer_instructions`;
- indicacao de modo (`read-only`, `proposal-only`, `write-capable`) para
  orientar sandbox/guardrails.

## Plano de implementacao sugerido

### Fase 1: instalador standalone

Objetivo: instalar Loki em um projeto local sem plugin.

Tasks:

- Criar script `scripts/install-loki`.
- Ler `manifest.yaml`.
- Implementar `--dry-run` padrao.
- Copiar skills para `.claude/skills` e `.agents/skills`.
- Copiar commands para `.claude/commands/loki`.
- Converter agents Markdown para `.codex/agents/*.toml`.
- Copiar agents Markdown para `.claude/agents`.
- Gerar blocos sugeridos de `AGENTS.md` e `CLAUDE.md` como patch proposto, nao
  escrita cega.
- Gerar manifesto de instalacao e rollback.

Validacao:

```bash
find .claude .agents .codex -maxdepth 4 -type f | sort
```

Depois abrir Claude Code e Codex em nova sessao para verificar descoberta.

### Fase 2: normalizar comandos como skills

Objetivo: reduzir divergencia entre Claude Code e Codex.

Tasks:

- Para cada `commands/loki-*.md`, criar ou apontar uma skill correspondente.
- Decidir se comandos Claude Code continuam como wrappers.
- Mover templates necessarios para `references/` das skills que precisam deles.
- Atualizar `README.md` e `manifest.yaml`.

Validacao:

- Conferir se cada workflow principal pode ser invocado por skill.
- Conferir se os comandos Claude Code nao duplicam instrucao divergente.

### Fase 3: plugin Claude Code

Objetivo: distribuir Loki no Claude Code como pacote versionado.

Tasks:

- Criar `.claude-plugin/plugin.json`.
- Incluir skills, agents, comandos/wrappers, docs e templates necessarios.
- Validar com `claude plugin validate`.
- Testar com plugin local.
- Opcionalmente criar `.claude-plugin/marketplace.json`.

Validacao:

```bash
claude plugin validate ./plugins/loki-framework
```

### Fase 4: plugin Codex

Objetivo: distribuir Loki no Codex como plugin de skills.

Tasks:

- Criar `.codex-plugin/plugin.json`.
- Incluir `skills/` autocontidas.
- Criar marketplace local em `.agents/plugins/marketplace.json` ou pessoal em
  `~/.agents/plugins/marketplace.json`.
- Testar instalacao pelo browser de plugins do Codex.
- Documentar conversao/instalacao separada de `.codex/agents/*.toml`, se
  necessaria.

Validacao:

```bash
codex plugin marketplace list
```

E depois verificar `/plugins` e `/skills` em uma nova sessao Codex.

## Riscos e mitigacoes

### Risco: divergencia entre Claude Code e Codex

Mitigacao:

- Tratar `skills/` como nucleo compartilhado.
- Tratar `commands/` como wrappers Claude Code ou artefatos de autoria.
- Converter agentes por ferramenta, sem copiar formato errado.

### Risco: instalar artefatos em destinos nao oficiais

Mitigacao:

- Atualizar README/manifest.
- Codex: `.agents/skills` para skills e `.codex/agents` para agents.
- Claude Code: `.claude/skills`, `.claude/agents` e, por compatibilidade,
  `.claude/commands/loki`.

### Risco: marketplace antes de estabilidade

Mitigacao:

- Comecar por standalone + instalador.
- Promover para plugin apenas depois de validacao em projetos consumidores.

### Risco: referencias quebradas em plugin/cache

Mitigacao:

- Tornar cada plugin autocontido.
- Evitar `../` para acessar arquivos fora do plugin.
- Colocar templates em `references/` quando forem usados por skills.

### Risco: `.agents/` virar fonte normativa indevida

Mitigacao:

- Manter `.agents/` como destino de instalacao local ou estado efemero.
- Nao copiar artefatos de `.agents/` de volta para o pacote Loki.
- Tratar `002-loki-framework-local` como fonte canonica.

### Risco: skills demais no contexto inicial

Mitigacao:

- Descricoes curtas e fortes.
- Namespacing `loki-`.
- Separar extensoes opcionais, como RPG Maker MZ, e instalar so quando o projeto
  consumidor exigir.

### Risco: validacao falsa de runtime

Mitigacao:

- Preservar gate humano ja descrito no pacote.
- O instalador nao deve declarar comportamento validado.
- Skills de execucao devem exigir evidencia observavel e registrar pendencias.

## Decisao recomendada

Adotar uma arquitetura de duas camadas:

1. **Camada fonte:** `002-loki-framework-local` continua sendo o pacote
   canonico, autocontido e auditavel.
2. **Camada adaptadora:** um instalador gera/copias artefatos especificos para
   Claude Code e Codex.

Nao usar marketplace como primeira solucao. Usar marketplace apenas como camada
de distribuicao depois que os mapeamentos estiverem corretos e validados.

## Proximo passo concreto

Criar uma task para implementar o instalador local com estes criterios minimos:

- dry-run padrao;
- suporte a `--target`;
- suporte a `--surfaces claude,codex`;
- copia de skills;
- copia de Claude agents;
- conversao de Codex agents para TOML;
- patch sugerido para `AGENTS.md` e `CLAUDE.md`;
- manifesto de instalacao;
- plano de rollback;
- atualizacao do README e `manifest.yaml` para remover destinos Codex
  incorretos.

Essa task deve ser feita antes de qualquer plugin marketplace.
