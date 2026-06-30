# RPG Maker MZ Project Inventory Checklist Router

Use this router to keep inventory work small, local, and focused. Load only the
reference needed by the active agent's task.

## Always Start Here

1. Declare inventory mode:
   - `minimal signature`: prove the project is RPG Maker MZ and identify main
     surfaces.
   - `focused ownership`: map the implementation surfaces for one feature,
     flow, domain, bug, or handoff.
   - `full project inventory`: inspect broad project ownership only when the
     user or approved plan explicitly asks for it.
2. Preserve the active agent's output format. Do not create a separate inventory
   report format unless the active workflow already asks for one.
3. Mark sources not read and why: out of scope, budget, unavailable, unsafe,
   too large, vendor/black-box, requires editor/runtime access, or requires
   human Playtest.
4. Classify evidence level:
   - `parse-valid`: a structured parser accepted the file.
   - `editor-structural`: the data shape matches expected RPG Maker editor
     structure.
   - `engine-semantic`: local engine source was inspected for relevant meaning.
   - `static-risk`: local static evidence suggests risk but not failure.
   - `runtime-pending`: behavior requires Playtest or human validation.
   - `runtime-validated`: human/runtime evidence exists in the active task.

## Reference Routing

- Read `core-inventory-checklist.md` for:
  - RPG Maker MZ signature;
  - routing docs and durable docs location;
  - System IDs, Common Events, maps, plugin order, plugin commands;
  - local engine source checks;
  - asset references, save/load ownership, pipeline scripts;
  - doc-runtime drift, static validators, evidence status, and escalation.
- Also read `game-dev-domain-inventories.md` when `focus_area` involves:
  - product/MVP, player promise, acceptance, or sensitive content;
  - gameplay loop, input, feedback, fail/result/retry, or runtime QA;
  - level design, map flow, gates, encounters, or softlock risk;
  - narrative, branching, quests, dialogue, localization, endings, or route QA;
  - UX/UI, accessibility, buttons, VN controls, save/load UX;
  - audio, scene presentation, technical art/assets, balance/economy, or
    deployment-facing content validation.

## Completion Rule

For a focused inventory, `complete` means the required ownership boundaries for
that focus were mapped or intentionally marked out of scope. Unknown required
docs, switches, variables, Common Events, maps, plugin commands, plugin files,
assets, save/load state, validators, or human gates make the inventory
`partial`.

Use `blocked` only when the next evidence requires unavailable tooling,
runtime/editor access, user decision, Playtest, or a forbidden write.

## Escalation Packet

When recommending `loki:tech-analysis`, include the smallest useful packet:

- concrete focus;
- source files and surfaces already inspected;
- important sources not read;
- unresolved ownership boundary or decision;
- validation gate static inventory cannot satisfy;
- minimum next question or Playtest path.
