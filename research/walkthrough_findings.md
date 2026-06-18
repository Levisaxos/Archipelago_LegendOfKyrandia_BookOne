# Kyrandia Book 1 — authoritative walkthrough findings (corrections to the model)

Source: Mike8787's GameFAQs guide (2002), cross-read 2026-06-18. This is the
**authoritative** quest chain; where it conflicts with the earlier memory-based
`walkthrough.md` / `data.py` DRAFT, **this wins.** A "✗ MODEL" tag marks a place
our current apworld is wrong and needs fixing.

## Potion recipes & effects (CONFIRMED)

Brew in Zanthia's pot (plant + gem, both required):
- **Red** = Orchid + (Garnet **or** Ruby)   ← either gem works
- **Blue** = Blueberries + Sapphire
- **Yellow** = Tulip + Topaz

Combine at the Crystals of Alchemy:
- **Orange** = Red + Yellow → **drink = turn into Pegasus** (fly to castle island)
- **Purple** = Blue + Red → **drink = shrink small** (enter the faun's home)
- **Green** = Yellow + Blue → **poison, uncurable death** (avoid; a check only if "making" it counts)

You need **2 Red + 1 Blue + 1 Yellow** (to make 1 Orange + 1 Purple).

### ✗ MODEL — Flasks are UNLIMITED, not a gate
Flasks come from Zanthia's cabin and **you get another every time you re-enter the
cabin** ("re-enter repeatedly to get more flasks"). So flask count is **not a real
constraint** — drop the "need 2 flasks / count-based logic" idea entirely. The
empty flask is freely available once you reach Zanthia (Act 3). Model brews as
gated on the *ingredients* + being in Act 3, not on flask count.

## Corrected area / gate structure

### Act 1 — Emerald Forest (Brandon's home + Brynn's temple)
- Start items incl. **Garnet, Saw, Apple, Letter** (note).
- **Amulet chain:** Letter→Brynn→(Lavender) Rose→**Silver Rose**; **Teardrop**→fit
  in dead willow (revives it, attracts **Merith**); chase Merith→**Purple Marble**
  (the altar's missing "purple orb"); place Marble + **Silver Rose** on **Brynn's
  temple altar** → **Amulet** (the 4 amulet stones, not an inventory item).
- **Bridge:** lend **Saw** to Herman → he fixes the bridge (keeps the saw — you
  never get it back). Walking the rope = **death**.

### ✗ MODEL — Act 2 (over the bridge): Darm's area, birthstone altar, flute, ice
- **Heal/Cure spell (1st):** drop **Walnut+Acorn+Pinecone** in the **Deadwood
  Forest hole** → Cure spell. *(This hole is in Act 2 near Darm, NOT Emerald
  Forest as our model has it.)*
- Cure the **Cardinal** → **Quill** → give Darm → **Scroll of Winter** (= our
  "Magic scroll"). *(The bird gives a QUILL, not a feather.)*
- **Birthstone / "Marble" altar (→ FLUTE):** down-and-left from **Darm's Shop**
  (Act 2, over the bridge — **NOT** Emerald Forest). Place the right gems
  (Sunstone first, Ruby often last, middle two random) → **Magic Flute**.
  *(Our altar is mis-regioned to Emerald Forest — move it to the Act-2 / Over-The-
  Bridge area. Gems are collected across Act 1 + Act 2.)*
- **Malcolm at the cave:** return his thrown daggers (timing or you die by ice),
  he ices the cave entrance.
- ✗ MODEL — **Flute breaks the ICE** over the cave entrance → enter the cavern.
  *(Our model: Flute "past Malcolm at grotto" + Fireberries "break ice". Both
  wrong: Flute breaks the ice; there is no separate grotto gate.)*

### ✗ MODEL — Act 2 cont. — the Labyrinth (the "caves")
- ✗ MODEL — **Fireberries LIGHT the dark labyrinth** (drop to light a room; last
  ~3 screen-moves, then stay lit). They are a **traversal** mechanic, NOT an
  ice-breaker. Needed to cross the labyrinth at all.
- Collect **5 Rocks** + a **Gold Coin** (in the "Moonlight Bay Cave").
- Throw **5 Rocks** on a balance → lifts a gate (escape the trap room).
- **Wisp spell (2nd):** **Coin → Magic Well → Moonstone**; Moonstone → Will-O-Wisp
  pedestal → **Wisp** (float over gaps, self-light, cross the chasm).
  *(So the "wishing well" gives the Moonstone; coin is the input.)*
- **Iron Key:** Wisp to a lava room → **Scroll of Winter freezes the lava** →
  cross → **Iron Key**. *(Iron Key needs **Wisp + Scroll**, not just the scroll.)*
- **Chasm:** turn into **Wisp to fly across** → exit to Act 3. *(Wisp gate ✓.)*

### Act 3 — Zanthia's (potions)
- **Crystal Ball:** **Scroll of Winter** on a flame → Crystal Ball.
- **Blue spell (3rd):** attach Crystal Ball to fix the **fountain** → fill flask
  with **fountain water** → **drink it** → Blue spell. *(NOT a catacombs forcefield.
  Blue = spell-nullification: kills levitation + force shields.)* Also give some
  fountain water to Zanthia (quest step).
- Get **Blueberries**, a **Red Orchid** (beach), brew the potions (above).
- **Royal Chalice:** it floats → **Blue spell** nullifies levitation → faun grabs
  it → **drink Purple potion** (shrink) → enter faun's home → **give him the
  Apple** → he returns the Chalice. *(THE APPLE'S USE. Apple = progression, Act 3.)*
- Grab **another Orchid** (for the grave / red spell).
- **Pegasus flight:** ✗ MODEL — **drink Orange Potion → become Pegasus → fly to
  the castle island.** *(NOT free. And it's a point of no return — can't go back.)*

### Act 4 — Grave Island → Castle → Kyra-Gem
- **Red spell (4th) = INVISIBILITY:** place **Orchid** on the parents' **grave** →
  mother's ghost → Red gem. *(✗ MODEL: our model says Lavender Rose; it's the
  ORCHID, and the power is invisibility.)*
- **Castle gate:** ✗ MODEL — use **Invisibility (Red) + Iron Key** to unlock the
  gate. *(Not iron key alone.)*
- **Crown:** library — pull books spelling **O-P-E-N** → fireplace reverses → Crown.
- **Gold Key #1:** behind the fireplace, blocked by a **force shield** → **Blue
  spell** destroys it → key under an irregular floor tile. *(This is our mythical
  "catacombs hidden key" — it's in the CASTLE, gated on Blue spell.)*
- **Scepter:** the kitchen **poker**.
- **Gold Key #2:** upstairs music room — green Herman blocks it → **Cure (Heal)
  spell** sleeps him → play bells **4,1,2,3** with the hammer/mallet → key.
- **Open inner doors** with the **two Gold Keys** → regalia room.
- **Regalia order:** place **Scepter–Crown–Chalice** on pillows → Kyra-Gem opens.
- **Final fight:** ✗ MODEL — turn **Invisible (Red)** and stand by the **Mirror**
  (room scenery, NOT an inventory item) → Malcolm's petrify ball reflects → win.
  *(Our model requires a "Mirror" item — likely wrong; the mirror is a fixed
  feature of the chamber. Verify before keeping "Mirror" as a needed item.)*

## The 4 amulet spells (source → use)

| Spell | Earned by | Used for |
|---|---|---|
| **Heal/Cure** | Nuts (walnut+acorn+pinecone) in the Deadwood hole (Act 2) | cure Cardinal→Quill; sleep green Herman (castle) |
| **Wisp** | Moonstone in the Will-O-Wisp pedestal (labyrinth) | traverse labyrinth, cross chasm, fetch Iron Key |
| **Blue** | Drink fountain water (Act 3, after fixing fountain w/ crystal ball) | nullify chalice levitation; destroy castle force shield (Key #1) |
| **Red (Invisibility)** | Orchid on the parents' grave (Grave Island) | unlock castle gate (w/ Iron Key); reflect Malcolm at the mirror |

## Item corrections / clarifications

- **Apple** → give to the faun for the **Chalice** (Act 3). **Progression**, 1 needed.
- **Scroll of Winter** (= "Magic scroll") → used **multiple times**: freeze lava
  (Iron Key), put out flame (Crystal Ball). Reusable. *(Supports "unlimited".)*
- **Flute** → breaks the cave ice once, then **never used again**. Source = the
  birthstone altar (Act 2).
- **Fireberries** → **light** the labyrinth (traversal), not ice-breaking.
- **Gold Coin** → into the **Magic Well** → **Moonstone**.
- **Mirror** → appears to be **chamber scenery**, not a carried item (verify).
- **Two Gold Keys** (fireplace + bells), distinct from the **Iron Key** (castle gate).
- **Useless/filler** (confirmed no use): **Hourglass**, **Fish** (edible), **Hairpin**.

## Softlocks / deaths / missables

- **Green potion** = uncurable poison death (don't drink).
- **Rope** across the broken bridge = death.
- **Castle island = point of no return** (Pegasus flight is one-way; forgetting an
  item before flying = unwinnable).
- **Malcolm dagger timing** + various dark-room deaths = instant death (reload).
- **Apple-vs-cave-entrance misclick** near the labyrinth exit can re-enter & kill.
- **Copy-protection password cues** (from the physical guidebook) fire at a couple
  of section transitions — not logic, but the engine fork should auto-pass them.

## Punch list — what to fix in the apworld (next session)

1. Drop flask-count logic; flasks are unlimited (Act 3).
2. Move the **birthstone altar (→Flute)** to the **Act-2 / Over-The-Bridge** region.
3. **Flute** gates **cave entry** (breaks ice); **Fireberries** gate **labyrinth
   traversal**, not an ice-break.
4. **Iron Key** = Wisp + Scroll (in the labyrinth), not "Magic scroll" alone.
5. **Pegasus → Grave Island** = **Orange Potion** (not free).
6. **Apple** = progression; gates the **Chalice** (Blue spell + Purple potion + Apple).
7. **Red spell** = **Orchid on grave** (not Lavender rose); = invisibility.
8. **Castle gate** = Iron Key + Red(invisibility). **Force-shield key** = Blue spell.
9. Delete the **Catacombs** region; its forcefield/hidden-key are **castle** content.
10. Re-check **Mirror** (scenery vs item) and the **two Gold Keys** vs Iron Key.
11. **Heal hole / Cardinal / Darm** are **Act 2** (over the bridge), not Emerald Forest.
12. **Blue spell** = fountain water (Act 3), not a catacombs event.
