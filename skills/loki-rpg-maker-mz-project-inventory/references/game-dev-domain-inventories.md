# Game-Dev Domain Inventories For RPG Maker MZ

Use this reference only when the focus area calls for a game-dev lens. These
are optional inventory prompts, not required report sections and not editorial
or design decisions.

## Product, MVP, And Acceptance

When product docs, pitch docs, jam scope, release readiness, or product owner
handoff is in scope, capture:

- audience, value proposition, core fantasy, and player promise;
- MVP boundary, stretch/out-of-scope claims, and default engine leakage;
- player-success signals: role, goal, stakes, feedback, progression, emotional
  or motivational intent;
- requirement traceability: durable source, runtime surface, implementation
  owner, acceptance criterion, validator, human gate, and status;
- risk register: probability, impact, evidence, mitigation, validator, and
  unresolved decision.

Classify acceptance as statically checkable, script/parser checkable, or human
Playtest only. Product coherence, player comprehension, and product safety are
not validated by static inventory.

## Gameplay And Runtime QA

For gameplay-focused inventories, map the loop as static evidence:

- player decision;
- implemented action path;
- input affordance;
- feedback surface;
- progression update;
- fail/result state;
- retry, re-entry, or continuation path;
- save/load implications.

For Common Events and plugins, flag semantic outcomes and embedded design logic:
success, failure, timeout, default branch, transfer, result screen, retry,
thresholds, formulas, randomization, victory/failure checks, timers, input
routing, and progression gates.

Runtime QA readiness should identify the smallest Playtest path covering boot,
focus feature, input, audio/visual feedback, result/retry, and save/load.
Static inventory does not validate feel, timing, clarity, input reliability,
plugin command effects, Common Event execution, balance, or save/load
compatibility.

## Level Design

When level flow is in scope, classify inspected maps by role:

- exploration, hub, arena, VN scene, transition, staging, test, ending, or
  unknown.

For selected maps, capture:

- size and viewport relationship;
- player start and incoming transfers;
- outgoing transfers and destination validity;
- expected critical path and optional paths;
- gates by switches, variables, self-switches, items, events, or plugins;
- encounter surface: random encounters, battle processing, troops/regions,
  hostile events, QTEs, timers, minigames, or scripted pressure;
- pacing beats, fallback paths, and static softlock risks.

Treat autorun, parallel events, input locks, erase-event flows, automatic
transfers, and destination coordinates as softlock-risk surfaces until
validated.

## Narrative, Branching, And Sensitive Content

When the focus area is narrative or content-facing, inventory:

- canon sources, exploratory notes, inferred intent, and runtime evidence as
  separate evidence classes;
- story-state registry: narrative switches/variables, expected ranges or
  states, owner surfaces, reset/persistence behavior, and unknown mappings;
- route manifest: scene/choice identifier, expected state mutation, destination
  map/event, ending/outcome, and evidence source;
- branch coverage matrix: branch, required pre-state, observable result, save
  fixture, and status as static-only, pending Playtest, or validated;
- unreachable-content audit: duplicated, orphaned, contradictory, or never
  satisfied choices, labels, transfers, pages, comments, and route predicates;
- sensitive-content surfaces: warnings, support-resource surfaces, method-detail
  risk, hope/support framing, and required human/specialist review.

Do not treat static route structure as proof of narrative comprehension, pacing,
emotional impact, localization quality, sensitive-content safety, or reachable
endings.

## Quest And Content

When focus includes quests, progression, player objectives, VN/content flows, or
endings, capture:

- quest chain: stage, map/event, entry condition, state changes, exit/transfer,
  fail/retry, reward/payoff, and missing evidence;
- NPC/content roles and required interactions;
- objective clarity and whether an explicit quest log/objective is implemented,
  absent, or a design decision to confirm;
- narrative state: switches, variables, self-switches, page conditions,
  score/relationship/final flags, save/load relevance, and doc-runtime drift;
- content anomalies: unusually large dialogue/event-command volume, repeated
  choices, deep branching, missing reconvergence, orphan branches, or unclear
  reachability.

Pacing, comprehension, emotional effect, branch reachability, and localization
quality require human Playtest evidence.

## Dialogue, Text, And Localization

When dialogue, localization, warnings, choices, VN scenes, or player-facing text
are in scope, treat text as an inventory surface, not an editorial task.

Capture:

- text-bearing event commands: Show Text, continuation text, Show Choices,
  choice branches, scrolling text, and comments when they affect review;
- map/event location, command-code counts, choice groups, branch density,
  speaker metadata, faces, window position/background, and text codes;
- plugin-rendered text, picture-rendered text, HUD/result labels, warnings, and
  support-resource surfaces;
- language evidence by surface: System locale, terms, database text, dialogue,
  choices, plugin UI, picture text, and docs;
- glossary drift for proper names, feature terms, route labels, variables
  referenced by narrative docs, and player-facing labels.

Static inventory may identify volume, structure, and risk; readability, tone,
LQA, sensitive-content handling, and actual UI fit require human preview or
Playtest.

## UX/UI, VN Controls, And Accessibility

When UI or player-facing feedback is in scope, inventory text, picture, input,
menu, save/load, and accessibility surfaces as first-class ownership evidence.

Capture:

- system terms, HUD/result labels, picture text payloads, image-based labels,
  fonts, resolution/UI area, window opacity, button/HUD coordinates, and
  lock/hover/pressed/disabled states;
- picture-based buttons: picture ID, asset path, label source, Common Event
  target, lock/disabled behavior, transition cleanup, and queued-event risk;
- VN-like controls: backlog/history, skip, auto mode, text speed, quick
  save/load, speaker clarity, nameplate clarity, and bust/dialog overlap;
- save/load UX smoke matrix for relevant states: title/continue, before choice,
  during message, timed interaction, result screen, after failure, after
  success, and after map transfer;
- accessibility static pass: contrast, non-text contrast, touch target size,
  color-only/audio-only dependence, flashes/shake/motion, timing adjustability,
  remapping, and font legibility at target scale.

Readability, composition, timing, input feel, touch behavior, contrast, and
save/load restoration require human validation.

## Audio

When audio is in scope, inventory by RPG Maker channel:

- `BGM`;
- `BGS`;
- `ME`;
- `SE`.

Extract audio references from `System.json`, map autoplay settings, Common
Events, map events, move routes, `Animations.json` sound timings, plugin
commands, plugin parameters, and custom plugin code.

Classify each cue as music, ambience, SFX, UI sound, ME, voice, accessibility
cue, or debug/instrumentation. A minimal cue sheet may include cue ID, trigger,
channel, file, intent, priority, fallback visual/textual cue, and validation.

Mark a gap when gameplay-critical information is conveyed only through sound and
no visual/textual fallback is visible. File presence does not validate playback,
mix, timing, loop quality, browser autoplay, captions, mono/stereo behavior,
volume balance, or player comprehension.

## Scene Presentation

When focus involves scene presentation, pictures, VN-style busts, HUD, overlays,
transitions, or staged audio cues, map presentation ownership separately from
gameplay ownership.

Capture:

- Picture ID reservations;
- layer stack;
- fullscreen/background dimensions;
- bust or character slots;
- expression/state evidence;
- transition waits, tint, shake, fade, and cleanup points;
- input-lock assumptions;
- BGM/BGS/ME/SE caller, timing, volume/pitch parameters, interruptions, fades,
  and missing cue-sheet evidence.

Static picture/audio/event inventory does not validate readability, pacing,
synchronization, focus, audio mix, input feel, or cleanup.

## Technical Art And Assets

When visual or runtime assets are in scope, capture dimensions, extension,
reference source, likely runtime role, static risk flags, and plugin ownership.
Do not rely on folder counts alone.

Use static categories such as:

- `static_passed`;
- `static_risk`;
- `runtime_pending`;
- `blocked_by_missing_evidence`.

Check scene-level texture cost for large or scene-critical images when memory or
preload behavior is relevant. Treat plugin-owned pictures, text pictures,
button pictures, busts, preload lists, and custom plugin commands as possible
asset owners.

Static existence does not validate playback, scale, blend, embedded texture or
model integrity, cache behavior, or performance.

## Balance And Economy

When balance, economy, progression, difficulty, rewards, shops, encounters, or
minigame scoring are in scope, distinguish configured Database content from
reachable runtime economy.

Inspect relevant database files:

- `Actors`, `Classes`, `Skills`, `Items`, `Weapons`, `Armors`, `Enemies`,
  `Troops`, `States`, and `System` settings affecting currency, party, EXP, TP,
  start state, or progression.

Do not treat prices, EXP, gold, drops, formulas, or thresholds as active until
map events, Common Events, troop events, encounters, shops, plugin commands, or
custom plugin code prove reachability.

Capture a source/sink map:

- resource sources, costs, rewards, losses, resets, repeatable loops,
  unreachable rewards, missing sinks, and likely exploit surfaces.

Static modeling can support hypotheses about difficulty or pacing. Success
rate, readability, timing pressure, fairness, feedback, and retry friction
require Playtest or another approved human validation gate.

## Sensitive Content

For games involving self-harm, suicide, severe violence, minors, grief, abuse,
or similar high-risk content, inventory surfaces and gates without prescribing
project-specific narrative policy.

Capture:

- where the content appears in docs, text, images, audio, routes, endings, or
  mechanics;
- content warnings, opt-in/out flow, support resources, tone/hope/support
  framing, and method-detail risk;
- required human, domain-sensitive, legal, or platform review gates.

Static inventory can identify content-risk surfaces. It cannot declare content
safe, ethical, compliant, or appropriate for an audience.
