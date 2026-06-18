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

## 2. Consumables / missables — the "renewable consumable" mechanic

Items the player can **consume or waste**, permanently losing a needed item:
- **Apple (38) → Apple Core (39):** eating the apple destroys it. Canonical softlock.
- **Nuts (acorn/walnut/pinecone), flowers (rose/tulip/orchid), blueberries:**
  consumed by the puzzles/recipes that use them.
- **Potions:** the combination web consumes primaries (see below).
- **Charge ladders** (repeated same-name engine IDs): **Fireberries 29–33**
  (confirmed decrementing charges — *separate topic, TBD*); **Scroll 80–89**
  (10 entries — believed **unlimited / effectively persistent** per user; verify
  in a future playthrough); **Parchment 90–94**; potions/waters paired.

### Decision — renewable consumables (chosen direction, 2026-06-18)

**Vanilla precedent (the machinery already exists):** placing a *wrong* (non-required)
gem on the birthstone altar makes it **poof and re-drop at a random scene in Act 1b**
— the game already has "consume here → respawn elsewhere" logic. We **generalize
this existing mechanic** to other consumables rather than inventing it.

Rather than make logic-critical items merely "non-consumable", the **engine fork
respawns a consumed consumable at a random REACHABLE scene** so the player can
re-collect it (a refinement over vanilla, which drops to Act 1b regardless of
whether it's reachable yet). This covers **potions, nuts, flowers, blueberries,
apple**. Effect: every such item is effectively renewable, so:

> **Apple is the odd one out:** eating it yields **Apple Core (39)**, not nothing.
> So its renewal can't be a plain respawn — the fork must convert the core back to
> an apple (or hand a fresh apple to a reachable scene) so the apple is never
> permanently lost. (Apple is currently `useful` in data.py and gates nothing;
> if a playthrough shows it IS needed for a puzzle, promote it + add the check.)

- **Logic (apworld):** model each consumable as a **single persistent progression
  unit** (`state.has(name)` ⇒ count 1 is enough). The current rules already do
  this — the respawn mechanic is what makes that modeling *correct*. No duplicate
  items needed. Spells (Heal/Wisp/Red/Blue) remain permanent capability events.
- **Engine (Phase 3, build-blocked):** on consume of a tracked consumable, drop it
  back into a random reachable scene instead of destroying it; for the Scroll,
  confirm it's unlimited (if not, hand the head ID / never deplete).

### Potion combination web (why "do we need 2?" → no, with respawn)

Primaries brewed from ingredients: **Blue** = Blueberries+Sapphire+Empty flask;
**Red** = Orchid+Ruby+Empty flask; **Yellow** = Tulip+Topaz+Empty flask.
Secondaries combined at the crystals: **Purple** = Blue+Red; **Orange** =
Yellow+Red; **Green** = Blue+Yellow (lethal if drunk; making it is a valid check);
**Potion of Rainbows** (engine id 69) = recipe TBD.

Each primary is consumed **twice** (Blue→Purple+Green, Red→Purple+Orange,
Yellow→Orange+Green). Without renewal you'd need 2 of each primary for full
accessibility of all secondary brew checks; **with respawn, 1 of each suffices**.
Modeled in apworld: `Zanthia - Brew {Blue,Red,Yellow,Purple,Orange,Green}` checks;
Potion-of-Rainbows not yet added (unknown recipe).

**Open sub-questions (verify in playthrough):**
- **Empty flask count:** combining needs two filled potions held at once → do you
  need **2 flasks**, or does a flask return empty after a potion is used? (User's
  alt option was "just add 2 empty flasks".) Current logic assumes 1 flask is enough.
- **Gems in brewing (likely fine):** the plan doc's item table marks only the
  flowers/nuts/berries (apple, nuts, tulip, blueberries, orchid) as *consumable* —
  **gems are NOT listed**, i.e. they're catalysts, not consumed. So Ruby serving
  both Red-potion AND the birthstone altar is fine (and AP rules never consume an
  item anyway: one Ruby satisfies both). Left OUT of the respawn list by design;
  just **confirm in playthrough** that brewing doesn't physically take the gem.
- **Which potions are goal-required** vs. pure side checks (Red feeds two combos; is
  any secondary needed downstream?).
- **Potion of Rainbows** recipe + whether to add it as a check.

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

The altar's vanilla **reward is the magic Flute** (core progression — gates the
caves). So the gems and the altar ARE logic-relevant.

**Decision (updated 2026-06-18 — now modeled, not deferred):**
- **Logic (apworld):** AP picks **all 4** required birthstones per seed (no fixed
  slots) via `data.choose_birthstones`, promotes them to **progression**, and
  gates the `Temple - Birthstone Altar (Flute)` location on holding them
  (rulesdata `birthstone_set` token, resolved in rules.py). The chosen gems +
  slot order go in slot_data (`birthstone_gems`); option `birthstone_hints`
  (none / gems / gems_and_slots) controls NPC reveals. The other scattered gems
  remain useful/filler. (NB: the Amulet altar is a SEPARATE mechanic — gated on
  Silver rose + Marble — don't conflate it with the birthstone altar.)
  - **Wrong-gem return (vanilla, helps us):** placing a non-required gem on the
    altar poofs it and re-drops it at a random Act 1b scene, so the player never
    loses a gem by trying it. This is the engine machinery we generalize for
    renewable consumables (see §2), and it means gems stay effectively persistent
    for logic regardless of altar experimentation.
- **Engine (Phase 3):** suppress native birthstone RNG (`o1_setBirthstoneGem` /
  `_birthstoneGemTable`) and instead set the table from slot_data `birthstone_gems`
  so the engine puzzle demands exactly AP's chosen set; render the NPC hints per
  `birthstone_hints`. Don't run both RNGs.

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
| Consumables/charges | each consumable is one persistent unit | **respawn consumed item at a random reachable scene** (potions/apple/nuts/flowers/blueberries); Scroll likely unlimited |
| Native gem RNG | AP picks all 4 birthstones; altar gives the Flute, gated on those 4 gems | suppress native RNG; set `_birthstoneGemTable` from slot_data `birthstone_gems`; render hints |
| One-way transitions | forward-only directed graph, ordered deps | (Phase 6 only) add return edges |
| Instant death | not modeled (reload recovers) | enumerate; optional hardening later |
