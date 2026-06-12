# Legend of Kyrandia — Book 1 Randomizer Data Plan (draft v1)

Source: Walkthrough King full playthrough + general game knowledge.
**Status:** first pass. Must be verified screen-by-screen against an actual
playthrough and the engine's room table / flag list before it's logic-complete.

## ID scheme (forward-compatible for Books 2 & 3)
Each book is its own AP world with its own integer ID space, offset by book:
- Book 1 base = 1_000_000
- Book 2 base = 2_000_000
- Book 3 base = 3_000_000

Within a book, category offsets:
| Offset | Category |
|--------|----------|
| +0000  | Inventory items |
| +0200  | Gems (item subclass, special — see native RNG note) |
| +0400  | Potions (item subclass) |
| +0600  | Amulet spells / powers |
| +0800  | NPCs / characters |
| +1000  | Zones / scenes (regions) |
| +1200  | Event / flag locations (non-pickup checks) |

So Book 1 healing spell = 1_000_600, etc.

---

## 1. Inventory items (collectables)
| ID | Item | Type | Notes |
|----|------|------|-------|
| 1000000 | Jewel (starting, Kallak's desk) | filler? | one of many loose gems |
| 1000001 | Note (Kallak's) | progression | given to Brynn |
| 1000002 | Saw | progression | given to Herman (bridge) |
| 1000003 | Apple | progression / **consumable** | needed later; eating it softlocks |
| 1000004 | Teardrop | progression | summons Merith at willow |
| 1000005 | Lavender rose | progression | → silver rose; also needed at grave |
| 1000006 | Silver rose | progression | from Brynn, used on altar → amulet |
| 1000007 | Purple rose | filler? | grabbed at temple altar |
| 1000008 | Marble | progression | used on altar |
| 1000009 | Amulet | **major progression** | spell carrier |
| 1000010 | Acorn | progression / consumable | dropped in hole (heal spell) |
| 1000011 | Walnut | progression / consumable | dropped in hole |
| 1000012 | Pinecone | progression / consumable | dropped in hole |
| 1000013 | Feather | progression | from healed bird → Darm |
| 1000014 | Magic scroll | **major progression** | fire protection; used many times |
| 1000015 | Tulip | progression / consumable | yellow potion; altar |
| 1000016 | Flute | progression | stops Malcolm at grotto |
| 1000017 | Knife (thrown back) | event item | combat beat |
| 1000018 | Rock x5 | filler | labyrinth |
| 1000019 | Gold coin | progression | wishing well → moonstone |
| 1000020 | Iron key | **major progression** | castle |
| 1000021 | Crystal ball | progression | fire puzzle |
| 1000022 | Flask (empty) x? | container | holds water/potions |
| 1000023 | Magic water | progression | for Zanthia |
| 1000024 | Blueberries | progression / consumable | blue potion |
| 1000025 | Rainbowstone | progression | from trunk (secret passage) |
| 1000026 | Orchid / exotic flower (red) | progression / consumable | red potion |
| 1000027 | Royal chalice | **major progression** | castle ending |
| 1000028 | Sceptre | **major progression** | castle ending |
| 1000029 | Crown | **major progression** | castle ending |
| 1000030 | Mallet | progression | music puzzle (Herman, upstairs) |
| 1000031 | Gold key | progression | from safe |
| 1000032 | Hidden key (catacombs) | progression | under stone |
| 1000033 | Books: Opal/Potions/Enchantment/Nature | event | library puzzle (reveals crown) |

> Consumables and the apple are the core **softlock** risks — see §8.

## 2. Gems / birthstones (special item subclass)
Used in the **birthstone altar puzzle**. The game **natively randomizes** the
middle two altar gems each new game, and scatters gems across nearly every
outdoor screen. This collides with AP logic and must be handled deliberately.
| ID | Gem | Notes |
|----|-----|-------|
| 1000200 | Sunstone (orange) | altar slot 1 (fixed) |
| 1000201 | Ruby (red) | altar slot 4 (fixed); also red potion |
| 1000202 | Peridot (green) | from dark-forest leaf (reliable) |
| 1000203 | Emerald (green) | counts as yellow in altar |
| 1000204 | Topaz (yellow) | random placement; yellow potion |
| 1000205 | Sapphire (blue) | blue potion |
| 1000206 | Amethyst (purple) | random altar candidate |
| 1000207 | Moonstone | from wishing well (coin) |
| 1000208 | Peridot/others (12 total scattered) | enumerate from playthrough |

## 3. Potions (item subclass, Zanthia act)
| ID | Potion | Recipe |
|----|--------|--------|
| 1000400 | Blue | blueberries + sapphire |
| 1000401 | Red (x2) | red flower + ruby |
| 1000402 | Yellow | tulip + topaz |
| 1000403 | Purple | blue + red (crystal towers) |
| 1000404 | Orange | yellow + red (crystal towers) |

## 4. Amulet spells / powers (major progression abilities)
Four stones earned through the game. These are the biggest logic gates.
| ID | Power | Earned by | Gates |
|----|-------|-----------|-------|
| 1000600 | Heal (stone 1) | acorn+walnut+pinecone in hole | bird, poison recovery |
| 1000601 | Wisp/teleport (purple, stone 2) | moonstone on cave altar | Chasm of Everfall, forest re-entry |
| 1000602 | Blue stone | (catacombs forcefield / chalice chase) | forcefields, floating chalice |
| 1000603 | Red stone | final stone at grave (lavender rose) | castle red stones, mirror ending |
| 1000604 | Yellow stone | (used on Herman upstairs) | confirm source in playthrough |

> Note: exact stone→color→source mapping needs verification; walkthrough
> references blue/red/yellow/purple powers but the earn-order isn't fully explicit.

## 5. NPCs / characters
| ID | NPC | Role |
|----|-----|------|
| 1000800 | Brandon | player |
| 1000801 | Kallak | grandfather (petrified, goal-adjacent) |
| 1000802 | Malcolm | antagonist (multiple beats) |
| 1000803 | Merith (willow spirit) | gating event |
| 1000804 | Herman | saw → bridge; later music puzzle |
| 1000805 | Brynn | note + rose → silver rose |
| 1000806 | Darm | quill/feather → scroll; birthstone info |
| 1000807 | Bench guy | hint (wounded bird) |
| 1000808 | Wounded bird | heal → feather |
| 1000809 | Zanthia | water/potions act |
| 1000810 | Pipsqueak/little guy | apple → chalice |
| 1000811 | Floaters (labyrinth) | altar / hint |

## 6. Zones / scenes (regions — for entrance shuffle)
High-level acts (the game is **largely linear with one-way transitions**):
| ID | Zone | Act |
|----|------|-----|
| 1001000 | Brandon's home (interior) | 1 |
| 1001001 | Starting forest (overworld screens) | 1 |
| 1001002 | Temple / altar area | 1 |
| 1001003 | Over-the-bridge forest (Darm) | 1 |
| 1001004 | Serpent's grotto (entrance) | 1→2 |
| 1001005 | The Labyrinth (cave maze) | 2 |
| 1001006 | Wishing well (exterior) | 2 |
| 1001007 | Volcanic river / iron key | 2 |
| 1001008 | Chasm of Everfall | 2→3 |
| 1001009 | Zanthia's home | 3 |
| 1001010 | Fountain / fire / crystal-ball area | 3 |
| 1001011 | Blueberry area | 3 |
| 1001012 | Secret passage / rainbowstone / orchids | 3 |
| 1001013 | Crystal towers | 3 |
| 1001014 | Floating chalice area | 3 |
| 1001015 | Grave island | 3→4 |
| 1001016 | Castle: foyer/kitchen/library | 4 |
| 1001017 | Castle: upstairs (Herman/music/safe) | 4 |
| 1001018 | Catacombs | 4 |
| 1001019 | Kyragem chamber (ending) | 4 |

> **Entrance-shuffle caveat:** acts are gated by one-way story transitions and
> two forced inventory wipes (§8). Full entrance shuffle is unlikely to be sane;
> intra-act / overworld-screen shuffle is the realistic scope. Decide per act.

---

## 7. What else you're missing (AP design categories)

**Locations vs items.** Above is *content*. The AP split is separate: a
*location* = a check the player can satisfy (pickup spot, NPC turn-in, puzzle
solve); an *item* = what gets placed there. The rose pickup is a *location*; the
rose itself becomes a shuffled *item*. You need an explicit location list — one
per pickup AND per non-pickup event (turn-ins, spell-earns, altar solves).

**Event / flag locations (non-pickup checks).** Earning a spell, completing the
birthstone altar, the music puzzle, healing the bird, etc. These are checks with
no inventory pickup — hook them at the flag-set, not inventory-add.

**Goal / completion condition.** Mirror/Kyragem ending after placing
crown+sceptre+chalice. This is your `completion_condition`.

**Two forced inventory wipes (structural — big deal).**
- Entering the labyrinth: "drop everything except the scroll."
- The royal foyer: placing crown/sceptre/chalice destroys remaining items.
These break naive AP item flow. You must either (a) treat each act as a logic
sub-graph with its own item subset, or (b) patch the engine so AP-relevant items
survive wipes. Design decision needed early.

**Native RNG (birthstones).** The vanilla game already shuffles gems. Either
suppress that in the fork so AP controls placement, or model it in logic. Don't
leave both running.

**Softlock traps / missables / instant-death.** Eating the apple, missing a
consumable, instant-death screens (Wikipedia confirms auto-game-overs). The
randomizer must guarantee completability — likely engine patches to make key
items non-consumable / re-obtainable. Collect the full death-screen list.

**Filler items.** Locations will outnumber progression items. Define filler
(spare rocks, loose jewels, money) and possibly traps (AP "trap" items) to pad
the pool to location count.

**Per-act item subsets.** Because of wipes + linearity, consider scoping shuffle
within acts first (much safer logic) before attempting cross-act shuffle.

---

## Open data to fill from a real playthrough
- Exact screen count + every gem spawn per screen
- Full death/softlock screen list
- Exact spell→source→color mapping
- Flask count and which empty containers exist where
- Which loose pickups are truly optional (filler) vs required
