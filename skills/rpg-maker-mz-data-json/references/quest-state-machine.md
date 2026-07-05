# Quest State Machine Guidance

Use this reference when implementing, migrating, or reviewing quests,
progression chains, route flags, objective gates, NPC dialogue stages, event
page conditions, or player-facing quest state in RPG Maker MZ data JSON.

## Default Rule

Prefer one named integer variable per quest as the primary progression state
machine. Avoid implementing a multi-step quest as a growing set of independent
switches when those switches represent mutually ordered quest stages.

Use switches for orthogonal booleans only, such as one-time local cleanup,
optional secrets, independent world flags, or event-local self switches. Do not
use several switches as a substitute for one ordered quest state.

## State Numbering

Use sparse values, usually stepping by 10:

```text
0  = not started
10 = first committed stage
20 = next major stage
30 = next major stage
90 = resolved, complete, or terminal state
```

The exact values belong to the project and task, but the spacing should leave
room for later inserts (`15`, `25`, etc.) without renumbering every event page,
conditional branch, validator, and save-dependent state.

## Event Design

- Name the variable clearly in `System.json`, for example
  `<Area>: <Quest Name> State`.
- Document the state table in the task or project docs before writing event
  pages.
- Gate event pages and NPC dialogue with variable thresholds or exact variable
  values, depending on whether later stages should inherit prior behavior.
- Advance the state only at committed milestones: item obtained, clue learned,
  objective accepted, route chosen, boss defeated, reward delivered, or quest
  resolved.
- Validate that every state assignment comes from the documented set, unless
  the task explicitly adds a new state.
- When migrating from switches, keep old switch names only if compatibility or
  save migration requires them; remove them from progression logic where
  possible.

## Validation

Static validation should report quest state separately from generic JSON parse:

- the state variable ID and name;
- the documented state table;
- all event commands that assign or compare the quest variable;
- page conditions that depend on the quest variable;
- absence of newly introduced quest-progression switch chains;
- any legacy switches intentionally retained for compatibility.

Runtime behavior remains Playtest or human-validation pending until the
player-facing quest flow, NPC dialogue, page activation, inventory changes, and
terminal state are exercised in game.
