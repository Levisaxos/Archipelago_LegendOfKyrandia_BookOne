# Legend of Kyrandia — Book 1 hazards (softlocks / wipes / missables) — DRAFT v1

**Status:** first pass (2026-06-11) from `kyrandia_book1_randomizer_plan.md` §7–8
+ general game knowledge. The full death-screen and wipe-trigger list needs the
read-only engine instrumentation (roadmap Phase 1, blocked on Phase 0 build).
These are the structural reasons a naive item shuffle can become **unwinnable**,
and how the apworld logic + the engine fork must account for them.

## 1. Forced inventory wipes (structural — the big one)

Vanilla forces the player to drop their inventory twice:
- **Labyrinth entry** ("drop everything except the scroll").
- **Castle foyer** (placing crown/sceptre/chalice destroys the remaining items).

Why it breaks an item rando: received AP items live in the same inventory. A wipe
would **destroy items the player has already collected**, stranding progression
that AP's logic assumes is still held → unwinnable seed.

**Decisions:**
- **Logic (apworld, now):** assume the engine fork **neutralizes both wipes**
  (roadmap Phase 3, "Neutralize wipes"). The region graph therefore treats items
  as persistent across act boundaries. This is recorded in `locations.json`
  `_meta.open_todos`.
- **Engine (Phase 3):** remove the two wipes, OR make AP-relevant items survive
  them. The handoff leans "remove the wipes". If wipes are *not* removed, the
  fallback is per-act logic sub-graphs (each act only uses items obtainable within
  it) — much more restrictive and not what V1 models.

## 2. Consumables / missables

Items the player can **consume or waste**, permanently losing a needed item:
- **Apple (38) → Apple Core (39):** eating the apple destroys it. Plan flags it
  as the canonical softlock.
- **Charge ladders** (Fireberries 29–33, Scroll 80–89, potions/waters): each use
  decrements; running out can strand a fire-protection requirement.
- **Nuts (acorn/walnut/pinecone), tulip, blueberries, magic water:** consumed by
  the puzzles/recipes that use them.

**Decisions:**
- **Engine (Phase 3):** make AP-progression items **non-consumable or
  re-obtainable** (on grant, always hand the *head* charge-ladder ID; suppress the
  consume transition for logic-critical items).
- **Logic (apworld):** treat each progression item as a single persistent unit —
  do **not** rely on multiple uses of one consumable. The Heal/Wisp spells are
  modeled as permanent capabilities (event items), not as repeated consumable use.

## 3. Instant-death / game-over screens

Wikipedia + walkthroughs confirm screens that auto-kill (e.g. wrong moves in the
lava/labyrinth, certain Malcolm beats). These don't strand items but can make a
seed feel unfair and can interrupt check delivery.

**Decision:** **collect the full list** during the Phase 1 playthrough/
instrumentation. For V1 logic they're not gates (death is recoverable via reload),
but they inform optional "avoid placing required checks past an unavoidable death"
hardening later.

## 4. Native gem RNG (birthstone altar)

Vanilla **randomizes the middle two altar gems** each new game and scatters gems
across outdoor screens. If left running alongside AP placement, the two RNGs
collide and gem-based logic becomes nondeterministic.

**Decision:**
- **Engine (Phase 3):** suppress native birthstone RNG (`o1_setBirthstoneGem` /
  `_birthstoneGemTable`) so AP controls gem identity/placement. Don't run both.
- **Logic (apworld):** the Amulet is earned at the altar location gated on
  Silver rose + Marble; individual scattered gems are filler-class and not relied
  on as gates in V1.

## 5. One-way transitions

The acts are joined by **one-way story transitions** (grotto entry, chasm
crossing, pegasus flight, foyer). In V1 (no entrance shuffle) the region graph is
directed and the player only moves forward, which is fine for an item rando *as
long as* every item needed in an earlier act is obtainable before the one-way
transition that leaves it. The dependency chain in `logic.md` is ordered so this
holds. Making transitions two-way is **Phase 6** (entrance shuffle) and requires
the engine to add return edges + un-losable return keys.

## Summary: what the apworld assumes vs. what the engine must deliver

| Hazard | apworld assumption (now) | Engine fork must deliver (Phase 3) |
|---|---|---|
| Inventory wipes | items persist across acts | remove both wipes (or protect AP items) |
| Consumables/charges | each progression item is one persistent unit | non-consumable / re-obtainable; grant head ID |
| Native gem RNG | gems are filler, altar gated on rose+marble | suppress native birthstone RNG |
| One-way transitions | forward-only directed graph, ordered deps | (Phase 6 only) add return edges |
| Instant death | not modeled (reload recovers) | enumerate; optional hardening later |
