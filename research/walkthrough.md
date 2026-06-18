# Legend of Kyrandia — Book 1 quest walkthrough & dependency chain — DRAFT v1

> ⚠️ **Partly superseded (2026-06-18).** Several facts below (flute source, ice vs
> fireberries, pegasus gate, red spell, apple use, region layout) were corrected
> against the GameFAQs guide — see **`walkthrough_findings.md`** for authoritative
> facts + the apworld punch-list. The check taxonomy here is still valid.

**Purpose.** A human-readable, step-by-step account of *what the player actually
does* to finish the game, and *which items each step needs and yields*. This is
the narrative counterpart to `logic.md` (which is the abstract region graph) and
the source we use to:

1. **justify every gate** in `apworld/kyrandia/data.py` (each edge / rule should
   trace back to a step here), and
2. **derive the check list** — every step below is a candidate Archipelago
   *location* (a "check") or a *hint*. See [Check taxonomy](#check-taxonomy).

**Status.** Assembled from walkthrough knowledge + `flags.md` instrumentation,
**not yet verified on a clean playthrough**. Each step carries a **confidence**;
open questions are called out inline and collected at the end. Where a flag id is
known it is cited from `flags.md` (e.g. `flag 45`). Treat low-confidence
mechanics as hypotheses to confirm, not facts.

**Convention for each step:**

> **Step name** — *what you do*
> - **Needs:** items/capabilities required to perform it (∅ = nothing)
> - **Yields:** item / capability / state unlocked
> - **Flag / conf:** flag id if known · confidence

---

## Act 1 — Brandon's Home & the Emerald Forest

The game opens with Brandon at his tree house; grandfather Kallak has been turned
to stone by Malcolm. Two parallel quest chains run through Act 1: the **Amulet
chain** (the spine of the whole game) and the **Bridge chain** (how you leave the
forest). They are independent — see the note under Herman.

### Amulet chain (the spine)

1. **Pick up Kallak's Note (home)** — search the tree house.
   - Needs: ∅
   - Yields: **Note**
   - Flag / conf: `flag 242` · High
2. **Talk to Brynn the Healer about Kallak** — she says there's a clue at home.
   - Needs: ∅ (this is what *points* you to the Note)
   - Yields: hint (clue-at-home)
   - Flag / conf: `flag 130` · High
3. **Show the Note to Brynn** — she decodes it; it names the **Amulet** and a
   **Lavender Rose**.
   - Needs: **Note**
   - Yields: hint (need Lavender Rose) + the lavender-rose request
   - Flag / conf: `flag 124` (shown) → `129` (decoded) → `125/126` (request) · Med
4. **Find the Lavender Rose** — it grows in the forest.
   - Needs: ∅
   - Yields: **Lavender rose**
   - Flag / conf: — · Med
5. **Give the Lavender Rose to Brynn** — she transforms it into a **Silver Rose**
   and tells you to "place this rose upon the silver altar."
   - Needs: **Note**, **Lavender rose**
   - Yields: **Silver rose**
   - Flag / conf: `flag 127/128` · Med
   - → data.py: `Brynn - Give Note & Rose (Silver Rose)` (requires Note + Lavender rose)
6. **Repair the temple altar with the Marble** — the silver altar in the temple
   is broken; the marble is the missing piece ("Perfect fit!").
   - Needs: **Marble** (see Marble/Merith sub-chain)
   - Yields: altar repaired (precondition for placing the rose)
   - Flag / conf: `flag 42` · High
7. **Place the Silver Rose on the altar → Amulet manifests → take it.**
   - Needs: **Silver rose** + repaired altar (**Marble**)
   - Yields: **Amulet** (the Royal Amulet — gates all four spell powers)
   - Flag / conf: `flag 45` (manifested) → `flag 7` (obtained) · High
   - → data.py: `Temple Altar - Birthstone Puzzle (Amulet)` (requires Silver rose + Marble)

### Birthstone gem altar (yields the Flute)

A 4-slot gem altar in the temple. Place the four required **birthstones** to get
the **magic Flute** (which is later needed to pass Malcolm at the grotto). Vanilla
randomizes which gems are needed (engine `_birthstoneGemTable`, slots 1 & 4 fixed
to Sunstone/Ruby, middle two random) and scatters gems across outdoor screens.

- **Solve the birthstone altar.**
  - Needs: the 4 required birthstone gems (which 4 = randomized)
  - Yields: **Flute**
  - → data.py: `Temple - Birthstone Altar (Flute)` (Emerald Forest)
  - **Randomizer:** AP picks all 4 required gems per seed (no fixed slots),
    promotes them to progression, and gates this check on holding them. An option
    (`birthstone_hints`) lets NPCs reveal the gems / their slots. Engine fork must
    suppress native RNG and read the set from slot_data. See `hazards.md` §4.

> **"Do we need to talk to Herman?"** — **No.** Herman is the *bridge* chain
> (below). The amulet needs Note → Brynn → Lavender rose → Silver rose → Marble →
> altar. Herman never enters it. (Open Q: confirm Brynn dialogue doesn't itself
> gate on having started the bridge quest — believed independent.)

### Marble / Merith sub-chain (feeds step 6)

How you obtain the Marble. Mechanics here are **moderate confidence** — the
teardrop ↔ willow ↔ Merith relationship needs a clean-run check.

- **Catch a teardrop at the weeping willow (Sorrow).**
  - Needs: ∅ · Yields: **Teardrop** · `flag 132/202` · Med
  - → data.py: `Willow - Teardrop Catch`
- **Heal the sick willow** (a *different*, half-dead willow, scene SICKWIL) —
  believed to use the teardrop. *Open Q: is this the same teardrop, and does
  healing it gate Merith?*
  - Needs: **Teardrop** (?) · Yields: willow healed · `flag 138` · Med
- **Summon / chase Merith the fairy** to recover the **Marble** — Merith leads a
  chase across forest screens; catching her drops the marble.
  - Needs: **Teardrop** (per data.py) · Yields: **Marble**
  - Flag / conf: chase flags `65`, `66–69`, `83` · Med
  - → data.py: `Merith - Summon at Willow` (requires Teardrop), `Temple Altar - Marble`
  - *Open Q: split — is "summon Merith" one check and "catch marble" another, or
    one combined location? Current data has both a Merith location and a Marble
    location.*

### Other forest pickups (mostly filler / spell-fuel)

- **Acorn, Walnut, Pinecone** — three nuts in the forest. Needed together for the
  Heal-power puzzle (Act 1b). · `∅` · Med
- **Apple** — edible (a **softlock** if eaten; see `hazards.md` §2). · ∅ · Med
- **Scattered birthstone gems** (Amethyst, Aquamarine, Emerald, Sapphire, Ruby,
  …) — scattered across outdoor screens; mostly filler, a few are recipe gems
  (progression: Ruby, Sapphire, Topaz). · ∅ · Med — *native gem RNG must be
  suppressed, see `hazards.md` §4.*
- **Purple Rose** — decorative pickup at the temple. · ∅ · Low

### Bridge chain (how you leave the forest)

8. **Find the Saw** in the forest.
   - Needs: ∅ · Yields: **Saw** · — · Med
   - → data.py: `Forest - Saw`
9. **Talk to Herman at the broken bridge** — he agrees to help ("I'll see what I
   can do"); the bridge quest starts.
   - Needs: ∅ · Yields: hint / quest-start · `flag 59` · High
10. **Give the Saw to Herman** — he repairs the bridge.
    - Needs: **Saw** · Yields: **bridge passable** (leave Emerald Forest)
    - Flag / conf: `flag 63` (saw given). **NB:** the actual passability is a
      *room-file swap* (`BROKEN`→`BRIDGE`, scene 7), **not** a flag — see the
      `flags.md` callout; the engine fork re-applies the swap. · High
    - → data.py edge `Emerald Forest → Over The Bridge` gated on **Saw**;
      location `Herman - Repair Bridge (Saw turn-in)`.

---

## Act 1b — Over the Bridge (to the grotto)

11. **Pick up the Gold Coin** (and gems) past the bridge. *(The Flute is not
    here — it comes from the birthstone altar back in the forest, see Act 1.)*
    - Needs: ∅ · Yields: **Gold coin** · — · Med
12. **Earn the Heal power** — at the "hole", offer the three nuts with the Amulet
    equipped. (Modeled as an event, not a networked item.)
    - Needs: **Amulet** + **Acorn** + **Walnut** + **Pinecone**
    - Yields: **Heal Spell** (capability)
    - Flag / conf: — · Med · → data.py event `Hole - Drop Nuts (Earn Heal Power)`
13. **Heal the wounded Bird → it gives a Feather.**
    - Needs: **Heal Spell** · Yields: **Feather** · — · Med
    - → data.py: `Bird - Heal & Get Feather` (requires Heal Spell)
14. **Give the Feather to Darm (the wizard) → Magic Scroll.**
    - Needs: **Feather** · Yields: **Magic scroll** · — · Med
    - → data.py: `Darm - Give Feather (Magic Scroll)`
15. **Play the Flute past Malcolm at the grotto** → enter the caves.
    - Needs: **Flute** · Yields: passage to **Caves Entrance**
    - Flag / conf: — · Med · → data.py edge gated on **Flute**;
      location `Grotto - Get Past Malcolm (Flute)`.
16. **(Optional) Drop the Gold Coin in the Wishing Well.**
    - Needs: **Gold coin** · Yields: a reward pickup · — · Low
    - *Open Q: what does the well give, and is it required for anything?*

---

## Act 2 — The Caves

17. **Pick up Fireberries** in the caves (a charge-ladder consumable — engine
    must grant the head ID; see `hazards.md` §2).
    - Needs: ∅ · Yields: **Fireberries** · — · Med
18. **Break / melt the ice** blocking the inner caves with the Fireberries.
    - Needs: **Fireberries** · Yields: passage to **Inner Caves**
    - Flag / conf: — · Med · → data.py edge gated on **Fireberries**;
      location `Caves - Break the Ice`.
19. **Use the Magic Scroll** to safely cross the lava and take the **Iron Key**
    (and a Crystal Ball).
    - Needs: **Magic scroll** · Yields: **Iron key**, **Crystal ball** · — · Med
    - → data.py: `Lava - Iron Key`, `Caves - Crystal Ball` (require Magic scroll)
20. **Earn the Wisp power** — place the Moonstone on the cave altar with the
    Amulet.
    - Needs: **Amulet** + **Moonstone** · Yields: **Wisp Spell** (capability)
    - Flag / conf: — · Med · → data.py event `Cave Altar - Place Moonstone`
21. **Cross the Chasm of Everfall** using the Wisp → reach Act 3.
    - Needs: **Wisp Spell** · Yields: passage to **Act3 Wilds**
    - Flag / conf: — · Med · → data.py edge gated on **Wisp Spell**.

> **Inventory wipe risk (Labyrinth entry):** vanilla forces "drop everything
> except the scroll" around here. The apworld assumes the engine neutralizes this
> (`hazards.md` §1). Verify exactly where it triggers.

---

## Act 3 — The Wilds (Zanthia & potion brewing)

22. **Reach Zanthia's area; collect Magic Water, Empty Flask, Blueberries,
    Orchid, Tulip**, plus the **Royal Chalice** (floating) and gems.
    - Needs: ∅ (within the region) · Yields: the above · — · Med
23. **Brew potions at Zanthia's cauldron** (each is its own check):
    - **Blue** = Blueberries + Sapphire + Empty flask
    - **Red** = Orchid + Ruby + Empty flask
    - **Yellow** = Tulip + Topaz + Empty flask
    - **Purple** = Blue potion + Red potion
    - **Orange** = Yellow potion + Red potion
    - Yields: the corresponding **potion** items · — · Med
    - → data.py `Zanthia - Brew …` locations. *Open Q: which potions are actually
      required downstream vs. flavor? Red is needed for the goal (below).*
24. **Fly to Grave Island on the pegasus** — currently modeled as a **free**
    transition (no engine pickup exists for it).
    - Needs: ∅ *(conservative — `logic.md`)* · Yields: **Grave Island**
    - *Open Q: is there a real gate (e.g. a potion, or healing the pegasus)?*

---

## Act 4 — Grave Island → Castle → Kyragem Chamber

25. **Grave Island: take the Fallen Star** (and a gem).
    - Needs: ∅ · Yields: **Fallen star** · — · Med
26. **Earn the Red power** — place the Lavender Rose on a grave.
    - Needs: **Amulet** + **Lavender rose** · Yields: **Red Spell** (capability)
    - Flag / conf: — · Med · → data.py event `Grave - Place Lavender Rose`
    - *Open Q: the Lavender rose was consumed making the Silver rose in Act 1 —
      need a second one, or is this a different rose? Consumable conflict; see
      `hazards.md` §2. Confirm.*
27. **Enter the Castle with the Iron Key.**
    - Needs: **Iron key** · Yields: **Castle** access
    - Flag / conf: — · Med · → data.py edge gated on **Iron key**.
28. **Castle interior** — solve the puzzles, each a check:
    - **Library book puzzle → Crown** (`Castle Library - Book Puzzle`)
    - **Open the safe → Gold Key** (`Castle Upstairs - Open Safe`)
    - **Music puzzle** (needs **Mallet**) (`Castle Upstairs - Music Puzzle`)
    - **Sceptre** (needs **Gold key**) (`Castle Upstairs - Sceptre`)
    - **Mallet**, **Mirror**, kitchen pickup — scattered castle items.
    - Yields: **Crown**, **Gold key**, **Sceptre**, **Mallet**, **Mirror** · Med
    - *Open Q: exact dependency order of safe/gold key/sceptre/music puzzle.*

> **Inventory wipe risk (Castle foyer):** placing Crown/Sceptre/Chalice is the
> vanilla second wipe. apworld assumes it's neutralized (`hazards.md` §1).

29. **Catacombs (side region, free from Castle)** — break the forcefield with the
    Amulet to earn the **Blue power**, which opens the **Hidden Key**.
    - Needs: **Amulet** → **Blue Spell**; then Blue Spell → Hidden Key
    - Yields: **Blue Spell** (event), **Hidden key**
    - → data.py event `Catacombs - Forcefield`, location `Catacombs - Hidden Key`
    - *Open Q: what does the Hidden Key actually open? Currently a dead-end
      reward; confirm it isn't required for the goal.*
30. **Enter the Kyragem Chamber** — present the regalia.
    - Needs: **Crown** + **Sceptre** + **Royal chalice**
    - Yields: **Kyragem Chamber** access
    - → data.py edge gated on Crown + Sceptre + Royal chalice.
31. **GOAL — Defeat Malcolm** — reflect his magic with the **Mirror** plus the
    **Red Spell** (the regalia got you in the room).
    - Needs: **Crown** + **Sceptre** + **Royal chalice** + **Mirror** + **Red Spell**
    - Yields: **Victory** (turn Malcolm to stone)
    - → data.py event `Kyragem Chamber - Defeat Malcolm (Turn to Stone)`;
      `completion_condition = state.has("Victory")`.

---

## Check taxonomy

Answering the original question — *"each item pickup is a check; each NPC chat is
a check or a hint; what else could be checks?"* Categories of Archipelago
**locations (checks)** in this game:

1. **Ground pickups** — click an item lying in a scene. The bulk of checks.
   Engine identity = `(sceneId, slot)` (see `ref-kyra-pickup-hooks`). *Includes
   scattered gems, nuts, flute, saw, fireberries, etc.*
2. **Scripted / animated catches** — e.g. the teardrop at the willow
   (`magicInMouseItem`). Not a simple ground click but still a "you get an item"
   check.
3. **NPC turn-ins / gifts** — give X to an NPC, receive Y. **Brynn** (rose),
   **Darm** (feather→scroll), **Herman** (saw→bridge), **Bird** (heal→feather).
   These are checks (the *reward slot* is what gets shuffled).
4. **Puzzle solves** — library book puzzle (Crown), music puzzle, safe, altar
   birthstone puzzle (Amulet). The puzzle's reward is the check.
5. **Crafting / brewing outputs** — Zanthia's 5 potions. Each brew is a check
   whose output item is shuffled.
6. **Environmental / state-change events** — break the ice, repair the bridge,
   repair the altar, cross the chasm. These are *gate* events; they can be
   modeled as **event locations** (id `None`) or as networked checks if they
   "hand you" something. Currently mostly modeled as edges + a turn-in location.
7. **Spell-earn events** — the four Amulet powers (Heal/Wisp/Red/Blue). Modeled
   as **event locations** granting capability items, not networked.
8. **The goal** — defeating Malcolm. An event location granting **Victory**.

**Hints (NOT checks):** dialogue that only points you somewhere and gives no
shuffleable reward — Brynn's "there's a clue at home", Herman's "I'll see what I
can do", Malcolm's taunts, Brandon's first-visit one-liners (the `flags.md`
"first visit" comment flags). These set flags but yield no item, so they are
candidate **AP hint** sources, not locations.

**Borderline / decisions to make:**
- An NPC chat that *advances state but gives no item* (e.g. "talk to Herman to
  start the bridge quest"): hint, not a check — unless we deliberately add it as a
  check for more checks-per-seed.
- A single quest with multiple sub-steps (Merith summon + marble catch): one
  check or two? Affects check count.
- Optional/dead-end rewards (Wishing Well, Hidden Key): keep as checks (free
  filler placement) as long as they're reachable.

---

## Open questions (to resolve via clean playthrough / Phase 1 instrumentation)

1. **Teardrop ↔ willow ↔ Merith:** does the teardrop heal the sick willow, and is
   that healing required before Merith/marble? Same teardrop or two?
2. **Lavender rose double-use:** Act 1 (→ silver rose) vs Act 4 grave (→ Red
   power) — same item consumed twice? Need two roses, or different flowers?
3. **Pegasus / Grave Island gate:** truly free, or is there a real requirement?
4. **Wishing Well & Hidden Key:** what do they give; required for anything?
5. **Castle internal order:** safe → gold key → sceptre → music puzzle exact deps.
6. **Which potions are required** downstream vs. pure flavor (Red is needed for
   the goal; the rest?).
7. **Inventory wipe trigger points** (Labyrinth entry, Castle foyer): exact scenes.
8. **Herman independence:** confirm the amulet chain has no hidden dependency on
   starting the bridge quest.
9. **Marble source:** is it solely the Merith chase, or also obtainable elsewhere?

When an item above is confirmed, update `flags.md` (confidence) and, if it changes
a gate, `apworld/kyrandia/data.py` (then regenerate `locations.json` via
`pyscripts/dump_research.py`).
