---
excalidraw-plugin: parsed
tags: [excalidraw]
doc_id: loki-learning-workflow-diagram
version: 1.1.0
status: active
last_updated: 2026-08-01
scope: Visual projection of the current Loki learning workflow and Semantic Abstraction Gate
not_scope: Write authorization, candidate schema replacement, or normative expansion from the Map022 example
authority: docs/loki-learning-workflow.md and current loki-continuous-improvement contracts
canonical_source: docs/loki-learning-workflow.md
intended_llm_task: context-hydration
source_priority:
  - current loki-continuous-improvement contracts
  - docs/loki-learning-workflow.md
  - this visual projection
known_conflicts: []
replaced_by: null
---

==Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document.==

# Excalidraw Data

## Text Elements

Entrada aprovada
fontes ou plano completo ^ci-input

Inventário seguro
XML + namespace excluído ^ci-inventory

Digestão por batches
reconciliação global ^ci-reconciliation

Semantic Abstraction Gate
depois da descoberta, antes do candidate v2
instância/configuração → invariante
aplicabilidade + exclusões + contraexemplo + rationale
owner: orquestrador; discovery é evidência ^ci-gate

generalized
6 tipos elegíveis; medium/high
counterexample none-observed ou bounded
segue lifecycle normal ^ci-generalized

local-with-rationale
canon, decisão local, exceção, caso singular
ou fronteira material determinável
segue lifecycle normal sem ampliar alcance ^ci-local

blocked-ambiguous
evidência/scope insuficiente ou contraexemplo ambíguo
blocked-with-reason + blocker material
sem approval de promoção ^ci-blocked

Candidate v2 current-only
gate após source_lineage e antes de target/unit
statement = resulting_statement
gate canônico participa do intent_digest ^ci-candidate

Map022 — exemplo não normativo
mapa, crianças e coordenadas = evidência/configuração
invariante = mover eventos em cutscene
preserva destino, facing e estado terminal ^ci-map022

Ownership
digester extrai; reconciler confirma tipo/scope
librarian pesquisa equivalência; orquestrador forma gate
validator fecha schema/digests; humano aprova intent
Writer aplica; Auditor revisa; librarian prova recovery ^ci-ownership

Lifecycle terminal
approval vincula intent + gate exato
generalized/local → envelope, Writer, Auditor, recovery
blocked → blocked-with-reason sem promoção
completed ou completed-with-blockers ^ci-terminal

%%
## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {"id":"ci-input-box-v2","type":"rectangle","x":0,"y":40,"width":250,"height":100,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"#e7f5ff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3001,"version":1,"versionNonce":4001,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-input-text-v2","type":"text","x":22,"y":65,"width":206,"height":50,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3002,"version":1,"versionNonce":4002,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Entrada aprovada\nfontes ou plano completo","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Entrada aprovada\nfontes ou plano completo","lineHeight":1.25,"baseline":45},
    {"id":"ci-inventory-box-v2","type":"rectangle","x":330,"y":40,"width":250,"height":100,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"#fff4e6","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3003,"version":1,"versionNonce":4003,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-inventory-text-v2","type":"text","x":352,"y":65,"width":206,"height":50,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3004,"version":1,"versionNonce":4004,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Inventário seguro\nXML + namespace excluído","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Inventário seguro\nXML + namespace excluído","lineHeight":1.25,"baseline":45},
    {"id":"ci-reconciliation-box-v2","type":"rectangle","x":660,"y":40,"width":300,"height":100,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"#f3f0ff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3005,"version":1,"versionNonce":4005,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-reconciliation-text-v2","type":"text","x":680,"y":65,"width":260,"height":50,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3006,"version":1,"versionNonce":4006,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Digestão por batches\nreconciliação global","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Digestão por batches\nreconciliação global","lineHeight":1.25,"baseline":45},
    {"id":"ci-gate-box-v2","type":"rectangle","x":290,"y":220,"width":460,"height":170,"angle":0,"strokeColor":"#7c2d12","backgroundColor":"#fff3bf","fillStyle":"solid","strokeWidth":3,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3007,"version":1,"versionNonce":4007,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-gate-text-v2","type":"text","x":315,"y":245,"width":410,"height":120,"angle":0,"strokeColor":"#7c2d12","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3008,"version":1,"versionNonce":4008,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Semantic Abstraction Gate\ndepois da descoberta, antes do candidate v2\ninstância/configuração → invariante\naplicabilidade + exclusões + contraexemplo + rationale\nowner: orquestrador; discovery é evidência","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Semantic Abstraction Gate\ndepois da descoberta, antes do candidate v2\ninstância/configuração → invariante\naplicabilidade + exclusões + contraexemplo + rationale\nowner: orquestrador; discovery é evidência","lineHeight":1.25,"baseline":115},
    {"id":"ci-generalized-box-v2","type":"rectangle","x":0,"y":500,"width":310,"height":150,"angle":0,"strokeColor":"#2b8a3e","backgroundColor":"#d3f9d8","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3009,"version":1,"versionNonce":4009,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-generalized-text-v2","type":"text","x":20,"y":525,"width":270,"height":100,"angle":0,"strokeColor":"#2b8a3e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3010,"version":1,"versionNonce":4010,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"generalized\n6 tipos elegíveis; medium/high\ncounterexample none-observed ou bounded\nsegue lifecycle normal","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"generalized\n6 tipos elegíveis; medium/high\ncounterexample none-observed ou bounded\nsegue lifecycle normal","lineHeight":1.25,"baseline":95},
    {"id":"ci-local-box-v2","type":"rectangle","x":370,"y":500,"width":310,"height":150,"angle":0,"strokeColor":"#1864ab","backgroundColor":"#d0ebff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3011,"version":1,"versionNonce":4011,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-local-text-v2","type":"text","x":390,"y":515,"width":270,"height":120,"angle":0,"strokeColor":"#1864ab","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3012,"version":1,"versionNonce":4012,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"local-with-rationale\ncanon, decisão local, exceção, caso singular\nou fronteira material determinável\nsegue lifecycle normal sem ampliar alcance","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"local-with-rationale\ncanon, decisão local, exceção, caso singular\nou fronteira material determinável\nsegue lifecycle normal sem ampliar alcance","lineHeight":1.25,"baseline":115},
    {"id":"ci-blocked-box-v2","type":"rectangle","x":740,"y":500,"width":310,"height":150,"angle":0,"strokeColor":"#c92a2a","backgroundColor":"#ffe3e3","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3013,"version":1,"versionNonce":4013,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-blocked-text-v2","type":"text","x":760,"y":515,"width":270,"height":120,"angle":0,"strokeColor":"#c92a2a","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3014,"version":1,"versionNonce":4014,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"blocked-ambiguous\nevidência/scope insuficiente ou contraexemplo ambíguo\nblocked-with-reason + blocker material\nsem approval de promoção","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"blocked-ambiguous\nevidência/scope insuficiente ou contraexemplo ambíguo\nblocked-with-reason + blocker material\nsem approval de promoção","lineHeight":1.25,"baseline":115},
    {"id":"ci-candidate-box-v2","type":"rectangle","x":370,"y":740,"width":310,"height":150,"angle":0,"strokeColor":"#5f3dc4","backgroundColor":"#e5dbff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3015,"version":1,"versionNonce":4015,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-candidate-text-v2","type":"text","x":390,"y":755,"width":270,"height":120,"angle":0,"strokeColor":"#5f3dc4","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3016,"version":1,"versionNonce":4016,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Candidate v2 current-only\ngate após source_lineage e antes de target/unit\nstatement = resulting_statement\ngate canônico participa do intent_digest","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Candidate v2 current-only\ngate após source_lineage e antes de target/unit\nstatement = resulting_statement\ngate canônico participa do intent_digest","lineHeight":1.25,"baseline":115},
    {"id":"ci-map022-box-v2","type":"rectangle","x":0,"y":980,"width":330,"height":170,"angle":0,"strokeColor":"#495057","backgroundColor":"#f1f3f5","fillStyle":"solid","strokeWidth":2,"strokeStyle":"dashed","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3017,"version":1,"versionNonce":4017,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-map022-text-v2","type":"text","x":20,"y":995,"width":290,"height":140,"angle":0,"strokeColor":"#495057","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3018,"version":1,"versionNonce":4018,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Map022 — exemplo não normativo\nmapa, crianças e coordenadas = evidência/configuração\ninvariante = mover eventos em cutscene\npreserva destino, facing e estado terminal","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Map022 — exemplo não normativo\nmapa, crianças e coordenadas = evidência/configuração\ninvariante = mover eventos em cutscene\npreserva destino, facing e estado terminal","lineHeight":1.25,"baseline":135},
    {"id":"ci-ownership-box-v2","type":"rectangle","x":370,"y":980,"width":380,"height":190,"angle":0,"strokeColor":"#0b7285","backgroundColor":"#c5f6fa","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3019,"version":1,"versionNonce":4019,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-ownership-text-v2","type":"text","x":390,"y":995,"width":340,"height":160,"angle":0,"strokeColor":"#0b7285","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3020,"version":1,"versionNonce":4020,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Ownership\ndigester extrai; reconciler confirma tipo/scope\nlibrarian pesquisa equivalência; orquestrador forma gate\nvalidator fecha schema/digests; humano aprova intent\nWriter aplica; Auditor revisa; librarian prova recovery","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Ownership\ndigester extrai; reconciler confirma tipo/scope\nlibrarian pesquisa equivalência; orquestrador forma gate\nvalidator fecha schema/digests; humano aprova intent\nWriter aplica; Auditor revisa; librarian prova recovery","lineHeight":1.25,"baseline":155},
    {"id":"ci-terminal-box-v2","type":"rectangle","x":790,"y":980,"width":350,"height":190,"angle":0,"strokeColor":"#2f9e44","backgroundColor":"#ebfbee","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":3021,"version":1,"versionNonce":4021,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false},
    {"id":"ci-terminal-text-v2","type":"text","x":810,"y":995,"width":310,"height":160,"angle":0,"strokeColor":"#2f9e44","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3022,"version":1,"versionNonce":4022,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"text":"Lifecycle terminal\napproval vincula intent + gate exato\ngeneralized/local → envelope, Writer, Auditor, recovery\nblocked → blocked-with-reason sem promoção\ncompleted ou completed-with-blockers","fontSize":16,"fontFamily":5,"textAlign":"center","verticalAlign":"middle","containerId":null,"originalText":"Lifecycle terminal\napproval vincula intent + gate exato\ngeneralized/local → envelope, Writer, Auditor, recovery\nblocked → blocked-with-reason sem promoção\ncompleted ou completed-with-blockers","lineHeight":1.25,"baseline":155},
    {"id":"ci-arrow-input-inventory-v2","type":"arrow","x":250,"y":90,"width":80,"height":0,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3101,"version":1,"versionNonce":4101,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[80,0]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-inventory-reconciliation-v2","type":"arrow","x":580,"y":90,"width":80,"height":0,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3102,"version":1,"versionNonce":4102,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[80,0]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-reconciliation-gate-v2","type":"arrow","x":810,"y":140,"width":110,"height":80,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3103,"version":1,"versionNonce":4103,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[-110,80]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-gate-generalized-v2","type":"arrow","x":470,"y":390,"width":315,"height":110,"angle":0,"strokeColor":"#2b8a3e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3104,"version":1,"versionNonce":4104,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[-315,110]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-gate-local-v2","type":"arrow","x":520,"y":390,"width":5,"height":110,"angle":0,"strokeColor":"#1864ab","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3105,"version":1,"versionNonce":4105,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[5,110]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-gate-blocked-v2","type":"arrow","x":570,"y":390,"width":325,"height":110,"angle":0,"strokeColor":"#c92a2a","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3106,"version":1,"versionNonce":4106,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[325,110]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-generalized-candidate-v2","type":"arrow","x":155,"y":650,"width":370,"height":90,"angle":0,"strokeColor":"#2b8a3e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3107,"version":1,"versionNonce":4107,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[370,90]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-local-candidate-v2","type":"arrow","x":525,"y":650,"width":0,"height":90,"angle":0,"strokeColor":"#1864ab","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3108,"version":1,"versionNonce":4108,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[0,90]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-blocked-candidate-v2","type":"arrow","x":895,"y":650,"width":370,"height":90,"angle":0,"strokeColor":"#c92a2a","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3109,"version":1,"versionNonce":4109,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[-370,90]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-candidate-terminal-v2","type":"arrow","x":590,"y":890,"width":375,"height":90,"angle":0,"strokeColor":"#2f9e44","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3110,"version":1,"versionNonce":4110,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[375,90]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"},
    {"id":"ci-arrow-candidate-ownership-v2","type":"arrow","x":525,"y":890,"width":35,"height":90,"angle":0,"strokeColor":"#0b7285","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"dashed","roughness":1,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":2},"seed":3112,"version":1,"versionNonce":4112,"isDeleted":false,"boundElements":null,"updated":1,"link":null,"locked":false,"points":[[0,0],[35,90]],"lastCommittedPoint":null,"startBinding":null,"endBinding":null,"startArrowhead":null,"endArrowhead":"arrow"}
  ],
  "appState": {"gridSize":20,"viewBackgroundColor":"#ffffff"},
  "files": {}
}
```
%%

# Current-only flow

```text
complete input -> safe inventory -> batch digestion -> global reconciliation -> root-specific discovery -> Semantic Abstraction Gate -> candidate v2 -> exact approval/write/audit/recovery -> truthful independence
```
