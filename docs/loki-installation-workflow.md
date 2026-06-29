---
title: Workflow de Instalacao do Loki em Projetos Consumidores
type: installation-workflow
status: draft
created: 2026-06-29
self_contained: true
---

# Workflow de Instalacao do Loki em Projetos Consumidores

Este e o guia humano canonico para instalar ou sincronizar o Loki Framework em
um projeto consumidor sem transformar o pacote em runtime, sem copiar fontes
geradas de volta para o pacote e sem misturar perfis de instalacao.

## Ideia central

O Loki e instalado em um consumidor como superficie documental e operacional:
commands, skills, agents, templates e projecoes Codex ficam disponiveis no
projeto alvo, mas a fonte auditavel continua sendo este pacote.

Instalar nao e escrever no runtime, engine, framework, assets ou dados do
consumidor. O fluxo sempre passa por leitura da politica local, dry-run,
approval explicito do destino, aplicacao controlada, validacao pos-instalacao e
registro claro do que ficou instalado.

![[loki-installation-workflow.excalidraw.md]]

## Fluxo

1. Identifique o destino consumidor e confirme que ele e um projeto local
   aprovado para receber artefatos Loki.
2. Leia a secao Codex de `README.md`, a secao "Instalacao Codex por Symlink" de
   `docs/usage-guide.md`, `manifest.yaml` em `install_policy` e
   `install-scopes.json` antes de qualquer escrita no destino.
3. Escolha exatamente um perfil:
   - `consumer`: artefatos `both` e `consumer-only`;
   - `package-source`: artefatos `both` e `internal-only`;
   - `all`: todos os escopos, apenas para validacao ou desenvolvimento.
4. Para projetos consumidores comuns, use `consumer`. Nao instale
   `package-source` em consumidor apenas para obter workflows de manutencao
   interna do pacote.
5. Rode primeiro o dry-run:

   ```bash
   PACKAGE_ROOT="$(pwd)"
   DEST="<consumer-root>"
   python3 "$PACKAGE_ROOT/scripts/install-loki-symlinks.py" --dest "$DEST" --dry-run --profile consumer
   ```

6. Revise a saida do dry-run. Todos os links planejados devem estar dentro de
   `.agents/**` ou `.codex/**` do destino, apontando para fontes dentro de
   `PACKAGE_ROOT`.
7. Se o dry-run mostrar conflito, symlink legado, manifest de outro perfil ou
   artefato fora do perfil solicitado, pare. Corrija manualmente o destino
   aprovado, normalmente usando o manifest anterior como guia de rollback, e
   rode novo dry-run antes de aplicar.
8. Aplique somente depois de approval explicito para o caminho do destino e o
   modo de execucao:

   ```bash
   python3 "$PACKAGE_ROOT/scripts/install-loki-symlinks.py" --dest "$DEST" --yes --profile consumer
   ```

9. Use `--replace` somente com approval separado, escopado ao destino e ao
   modo. Sem `--replace`, conflitos devem bloquear a instalacao.
10. Depois da aplicacao, valide a instalacao.

Validacao pos-instalacao:

```bash
python3 "$PACKAGE_ROOT/scripts/validate-install-scopes.py"
find -L "$DEST/.agents/skills" -maxdepth 2 -name SKILL.md | sort
find -L "$DEST/.agents/commands/loki" -maxdepth 1 -name 'loki-*.md' | sort
find "$DEST/.agents/agents" -maxdepth 1 -type l -name '*.md' | sort
find "$DEST/.codex/agents" -maxdepth 1 -type l -name '*.toml' | sort
python3 - "$DEST" <<'PY'
import json
import pathlib
import sys

manifest = pathlib.Path(sys.argv[1]) / ".agents/loki-installation-manifest.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
print(f"profile={data.get('install_profile')} links={len(data.get('links', []))}")
assert all("install_scope" in link for link in data.get("links", []))
PY
git -C "$DEST" status --short .agents .codex
```

11. Se o consumidor precisar de roteamento em `AGENTS.md`, `CLAUDE.md` ou docs
    duradouras, trate isso como sincronizacao separada. Nao atualize esses
    arquivos durante a instalacao basica sem pedido explicito.
12. Para trocar entre perfis, faca rollback manual dos links registrados em
    `.agents/loki-installation-manifest.json`, confirme que os destinos eram
    symlinks para `PACKAGE_ROOT`, rode novo dry-run limpo e so entao aplique o
    novo perfil. Perfis nao sao camadas incrementais.

## Artefatos participantes

### Fontes do pacote

| Artefato | Contribuicao no workflow |
| --- | --- |
| `README.md` | Define a politica local de instalacao, destinos, comandos de dry-run, apply e rollback. |
| `docs/usage-guide.md` | Explica o uso operacional do instalador, perfis, validacao e limites. |
| `manifest.yaml` | Declara politica de instalacao, destinos Codex, gates e arquivos do pacote. |
| `install-scopes.json` | Define quais comandos, skills e agentes pertencem a cada escopo instalavel. |
| `scripts/install-loki-symlinks.py` | Planeja e aplica symlinks por perfil, gera manifest e bloqueia conflitos. |
| `scripts/validate-install-scopes.py` | Valida escopos, neutralidade de artefatos `both`, TOMLs Codex e metadados. |

### Destinos no consumidor

| Destino | Conteudo esperado |
| --- | --- |
| `.agents/skills/<skill-name>` | Symlink para `skills/<skill-name>`. |
| `.agents/commands/loki/<command>.md` | Symlink para `commands/<command>.md`. |
| `.agents/agents/<agent>.md` | Symlink para `agents/<agent>.md`. |
| `.agents/templates` | Symlink para `templates`. |
| `.codex/agents/<agent>.toml` | Symlink para `codex/agents/<agent>.toml`. |
| `.agents/loki-installation-manifest.json` | Manifest gerado com origem, destino, perfil, escopo e status dos links. |

## Gates e pontos de parada

- Pare se o destino nao foi aprovado explicitamente.
- Pare se `README.md` e `docs/usage-guide.md` ainda nao foram lidos para a
  instalacao atual.
- Pare se o dry-run nao foi executado ou nao foi revisado.
- Pare se o dry-run apontar artefatos fora de `.agents/**` ou `.codex/**` do
  destino.
- Pare se existir manifest de outro perfil, artefato Loki fora do perfil
  solicitado ou symlink legado que possa causar escrita atraves de diretorio
  linkado.
- Pare se a correcao exigir alterar runtime, engine, framework, assets, dados
  persistidos ou arquivos de negocio do consumidor.
- Pare se a unica forma de continuar for usar `--replace` sem approval
  separado.
- Nao atualize `AGENTS.md`, `CLAUDE.md` ou `docs/index.xml` do consumidor como
  efeito colateral da instalacao basica.

## Validacao esperada

Uma instalacao bem-sucedida deve demonstrar:

- `scripts/validate-install-scopes.py` passa no package root;
- os entrypoints `SKILL.md` resolvem via `find -L`;
- comandos Loki instalados correspondem ao perfil escolhido;
- agentes Markdown e TOMLs Codex existem como symlinks;
- `.agents/loki-installation-manifest.json` e JSON parseavel e registra
  `install_profile`, `install_scope` e `links`;
- `git -C "$DEST" status --short .agents .codex` mostra o impacto local para
  revisao humana;
- nenhum arquivo de runtime ou contexto duradouro do consumidor foi alterado
  sem pedido separado.

## Resultado esperado

Ao fim da instalacao, outra LLM deve conseguir auditar pelo disco:

- qual pacote Loki foi usado como origem;
- qual destino consumidor recebeu symlinks;
- qual perfil foi instalado;
- quais links foram criados, mantidos ou bloqueados;
- qual manifest registra a instalacao;
- quais validadores foram executados;
- quais gates humanos foram necessarios;
- qual rollback manual deve ser usado antes de trocar perfil ou remover Loki.

Depois da instalacao, o uso operacional do Loki no consumidor segue o
[Workflow de Execucao de Plano do Loki](loki-plan-execution-workflow.md) e o
[Workflow de Aprendizado do Loki](loki-learning-workflow.md).
