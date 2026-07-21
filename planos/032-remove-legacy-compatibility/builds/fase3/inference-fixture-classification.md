---
title: "Classificação de fixtures de analytic inference"
task_id: task-3.1
status: completed
---

# Classificação de fixtures de analytic inference

## Método e limites

Foram classificados todos os oito JSONs em
`skills/lf-analytic-inference/references/fixtures/` pelo payload que exercitam,
pelos consumers executáveis e pelo destino previsto da task 3.2 — nunca pela
extensão `.json` nem por `schema_version: 1`. A busca de referências nominais
nos scripts, contratos e demais artefatos do pacote retornou zero consumers
automáticos para cada nome de fixture: eles são vetores manuais de validação.
Portanto, o consumer abaixo é o script/contrato que entende o shape e a
invocação observável que o comprova.

## Mapa completo

| Fixture | Classe | Consumer e evidência | Decisão |
| --- | --- | --- | --- |
| `catalog-empty.json` | legado removível | Sem consumer automático por nome. Seu shape de índice JSON v1 é aceito por `_legacy_catalog` durante `migration_dry_run`; não é input de `state_xml.py`. | **Excluir**. |
| `catalog-invalid.json` | legado removível | Sem consumer automático por nome. São vetores negativos para o shape legado que `_legacy_catalog`/`migration_dry_run` leem; `validate_catalog.py` não carrega este arquivo nem é alegado como consumer. | **Excluir**; task 3.2 acrescenta a negativa de layout/operação legado. |
| `catalog-limit.json` | legado removível | Sem consumer automático por nome. Blueprints de índice/records JSON v1 modelam `_legacy_catalog` e a verificação de ocupação; o limite atual continua no control plane XML v2, mas esta representação depende dos schemas JSON removidos na task 3.2. | **Excluir**. |
| `consumer-state-empty.json` | control plane atual | Declara `state_root` v2 e `live_serialization: canonical-xml-v2`; descreve bootstrap sem seed de produção. Consumer: `manage_consumer_state.py` bootstrap/inspect com a política atual. | **Reter**. |
| `consumer-state-isolation.json` | control plane atual | Materializa apenas `.loki/analytic-inference/v2/*.xml` a partir de valores lógicos JSON; cobre isolamento e lookup seletivo do consumer v2. | **Reter**. |
| `purge.json` | control plane atual | Cenários sintéticos de dry-run/JIT de purge com estado vivo XML v2 e control plane JSON canônico. Consumer: `manage_consumer_state.py purge-dry-run`. | **Reter**. |
| `replay.json` | control plane atual e rejeição retida | Casos de reconciliação de eventos, incluindo replay idêntico e conflito divergente. Consumer: `reconcile_events.py`; o conflito é a negativa atual. | **Reter**. |
| `state-xml-codec.json` | codec XML atual e rejeição retida | Vectores para `state_xml.py self-test`; documentos lógicos são codificados como XML v2 e `hostile_cases` devem falhar. Execução atual: 33/33. | **Reter**. |

## Conjuntos fechados para task 3.2

```text
delete_set:
  - skills/lf-analytic-inference/references/fixtures/catalog-empty.json
  - skills/lf-analytic-inference/references/fixtures/catalog-invalid.json
  - skills/lf-analytic-inference/references/fixtures/catalog-limit.json

retain_set:
  - skills/lf-analytic-inference/references/fixtures/consumer-state-empty.json
  - skills/lf-analytic-inference/references/fixtures/consumer-state-isolation.json
  - skills/lf-analytic-inference/references/fixtures/purge.json
  - skills/lf-analytic-inference/references/fixtures/replay.json
  - skills/lf-analytic-inference/references/fixtures/state-xml-codec.json
```

Não há conversão de fixture existente: a negativa necessária é nova e limitada
ao antigo `migration-dry-run`/layout `.loki/analytic-inference/v1/**`.

## Prova reprodutível do delete-set

O mapa nominal foi executado individualmente para os três nomes abaixo. Cada
comando retorna zero, provando que nenhum script descobre automaticamente o
arquivo pelo nome; não prova que o shape seja atual.

```sh
for name in catalog-empty.json catalog-invalid.json catalog-limit.json; do
  rg -l --fixed-strings "$name" . \
    --glob '!planos/**' \
    --glob "!skills/lf-analytic-inference/references/fixtures/$name"
done
```

O reader alcançável que esses vetores modelam está em
`manage_consumer_state.py`: `migration_dry_run` chama `_load_legacy_json` e
`_legacy_catalog` para `catalogs/<technology>/index.json`; `_legacy_catalog`
exige `CATALOG_KEYS`, `schema_version == 1` e locators `*.json`. A reprodução
direta, sem tratar fixture como input de `validate_catalog.py`, é:

```sh
python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, 'skills/lf-analytic-inference/scripts')
import manage_consumer_state as m
root = Path('skills/lf-analytic-inference/references/fixtures')
entry = {'technology': 'base', 'catalog_id': 'fixture-empty-catalog-v1',
         'aliases': [], 'locator': 'catalogs/base/index.json'}
print(m._legacy_catalog(json.loads((root / 'catalog-empty.json').read_text()), entry)['catalog_id'])
try:
    m._legacy_catalog(json.loads((root / 'catalog-invalid.json').read_text())['cases'][0]['input'], entry)
except m.StateError as exc:
    print(exc.diagnostic)
limit = json.loads((root / 'catalog-limit.json').read_text())
print(len(limit['cases']), sorted(limit['record_blueprints']))
PY
```

Resultado observado: `fixture-empty-catalog-v1`,
`LEGACY_CATALOG_IDENTITY`, e quatro casos com cinco record blueprints. Assim,
`catalog-empty` exercita a aceitação do reader legado; `catalog-invalid`
exercita sua rejeição; e `catalog-limit` fornece seus índices/records JSON v1.
Todos deixam de ter um reader alvo depois do corte, enquanto a negativa nova
testará a rejeição pública do layout/operação legado.

## Validação observada

- Mapa de referências nominais: `0` consumers automáticos para cada um dos
  oito nomes; o resultado não autoriza apagar os cinco retain sets porque seus
  formatos são consumidos pelos scripts atuais quando a fixture é passada.
- `python3 .../state_xml.py self-test --fixture .../state-xml-codec.json`:
  `status=valid`, `33/33`.
- `python3 .../reconcile_events.py` com o primeiro caso de `replay.json`:
  `status=valid`, sem mutação.
- `python3 .../validate_catalog.py --technology loki-framework --policy ...`:
  `status=valid`, `mutation_applied=false`.

Nenhum schema, script ou fixture foi alterado nesta task.
