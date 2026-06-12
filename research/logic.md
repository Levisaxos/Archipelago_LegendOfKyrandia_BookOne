# Legend of Kyrandia — Book 1 logic (region graph + access rules) — DRAFT v2

**Status:** broad first pass (2026-06-11). Derived from `kyrandia_book1_randomizer_plan.md`
+ walkthrough knowledge. The machine-readable form is `research/locations.json`
(generated from `apworld/kyrandia/data.py`, the single source of truth); the
apworld is built from the same data. **Not yet verified against a live
playthrough** — confidence varies per entry.

**Scale:** 11 regions, **64 networked locations** + 5 event locations.

## Logic model — "Model A" (vanilla item gates)

V1 is an **item randomizer**: shuffle *what each pickup gives*, keep the vanilla
world structure. Region edges and turn-in/puzzle locations are gated on the
**real game items** the vanilla game uses at that transition. A *location* (a
pickup, a turn-in, a puzzle solve, a flag event) holds a **shuffled** item; the
vanilla association survives only as metadata embedded in the location's name.

**Reachability invariant:** any item named in a rule MUST be a progression (or
event) item — only those participate in Archipelago's reachability sweep. A
`useful`/`filler` item in a rule could never satisfy it. Enforced by validation.

## Region graph

```
Menu → Brandons Home → Emerald Forest ──(Saw)──→ Over The Bridge
                                                      │
                                                  (Flute)
                                                      ▼
                                                Caves Entrance ──(Fireberries: break ice)──→ Inner Caves
                                                                                                 │
                                                                                          (Wisp Spell: cross chasm)
                                                                                                 ▼
                                                                                            Act3 Wilds
                                                                                                 │
                                                                                       (free, pegasus)
                                                                                                 ▼
                                                                                           Grave Island
                                                                                                 │
                                                                                            (Iron key)
                                                                                                 ▼
                                                                          Catacombs ←(free)─ Castle ─(Crown+Sceptre+Royal chalice)→ Kyragem Chamber
```

Edges (authoritative list: `locations.json` → `edges`):

| From → To | Gate | Vanilla basis |
|---|---|---|
| Menu → Brandons Home | — | game start |
| Brandons Home → Emerald Forest | — | front door |
| Emerald Forest → Over The Bridge | **Saw** | Herman repairs the bridge |
| Over The Bridge → Caves Entrance | **Flute** | flute past Malcolm at the grotto |
| Caves Entrance → Inner Caves | **Fireberries** | melt/break the ice blocking the cave |
| Inner Caves → Act3 Wilds | **Wisp Spell** | teleport across the Chasm of Everfall |
| Act3 Wilds → Grave Island | — *(free, TODO)* | pegasus flight (no engine pickup) |
| Grave Island → Castle | **Iron key** | castle entry |
| Castle → Catacombs | — *(free)* | side region |
| Castle → Kyragem Chamber | **Crown + Sceptre + Royal chalice** | the royal regalia |

## Amulet powers as event items

Four powers are **earned capabilities**, modeled as event items (id None) placed
locked on event locations, not in the multiworld pool. Each needs the **Amulet**.

| Event location | Region | Requires | Grants | Gates |
|---|---|---|---|---|
| Hole - Drop Nuts | Emerald Forest | Amulet + Acorn + Walnut + Pinecone | **Heal Spell** | Bird → Feather |
| Cave Altar - Place Moonstone | Inner Caves | Amulet + Moonstone | **Wisp Spell** | Chasm → Act 3 |
| Grave - Place Lavender Rose | Grave Island | Amulet + Lavender rose | **Red Spell** | the goal (Malcolm) |
| Catacombs - Forcefield | Catacombs | Amulet | **Blue Spell** | Hidden Key (side) |

## Goal — defeat Malcolm (turn to stone)

Event **Kyragem Chamber - Defeat Malcolm (Turn to Stone)** grants **Victory**.
Requires **Crown + Sceptre + Royal chalice + Mirror + Red Spell** — recover the
regalia, obtain the mirror, earn the red amulet power, then reflect Malcolm's
magic back at him. `completion_condition = state.has("Victory")`.

## Notable nested chains (the depth that makes it interesting)

- **Heal chain (critical):** Amulet+nuts → Heal Spell → heal Bird (Feather) →
  Darm (Magic scroll) → Lava (Iron key) → enter Castle.
- **Wisp chain (critical):** Gold coin → Wishing Well; Amulet+Moonstone →
  Wisp Spell → cross chasm to Act 3.
- **Ice chain (critical):** Fireberries → break the ice → Inner Caves.
- **Potion brewing (side checks):** Brew Blue = Blueberries+Sapphire+Empty flask;
  Red = Orchid+Ruby+Empty flask; Yellow = Tulip+Topaz+Empty flask; Purple =
  Blue+Red potion; Orange = Yellow+Red potion. (Specific gems are progression.)

## Deliberately conservative for V1 (keeps seeds fillable)

- **Grave Island** access (pegasus) is free — no engine pickup exists for it.
- **Catacombs** is a free side region; Blue Spell gates only the hidden key.
- **No early-region check is gated on a late-region item**, so the forward-only
  (one-way) vanilla transitions never strand a check behind impossible
  backtracking. Tighten with real data from Phase 1 instrumentation.
- Assumes the engine fork **neutralizes the two inventory wipes** (see `hazards.md`).
