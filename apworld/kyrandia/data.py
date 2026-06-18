"""Canonical data tables for the Legend of Kyrandia - Book 1 apworld.

Single source of truth for items, locations, regions and edges. The research
deliverable `research/locations.json` is GENERATED from this module
(pyscripts/dump_research.py) so the two never diverge.

DRAFT v3 (2026-06-18): rebuilt against the authoritative GameFAQs walkthrough
(see research/walkthrough_findings.md). Corrects the v2 structure — the flute
altar is in Act 2, the flute breaks the cave ice, fireberries light the
labyrinth, the pegasus is gated on the Orange potion, the apple buys the Chalice,
the Red spell comes from the orchid on the grave, the Blue spell from fountain
water, there is no Catacombs region, and the Mirror is chamber scenery.

Logic model: "Model A" — region edges and turn-in/puzzle locations are gated on
the REAL game items the vanilla game uses at that transition (item randomizer).

INVARIANT: every item that appears in any `requires` list MUST be classified
PROGRESSION (or be an event item). Only progression/event items participate in
Archipelago's reachability sweep; a `useful`/`filler` item named in a rule could
never satisfy it.
"""
from __future__ import annotations

PROGRESSION = "progression"
USEFUL = "useful"
FILLER = "filler"

# ---------------------------------------------------------------------------
# Items: name -> (ap_id, classification). IDs reuse research/kyra1_items.json
# `ap_id` where the engine item is mapped; new ids fill gaps. Filler 1,000,9xx.
# ---------------------------------------------------------------------------
ITEM_TABLE: dict[str, tuple[int, str]] = {
    # --- progression (named in some `requires`) ---
    "Note":          (1000001, PROGRESSION),
    "Saw":           (1000002, PROGRESSION),
    "Teardrop":      (1000004, PROGRESSION),
    "Lavender rose": (1000005, PROGRESSION),
    "Silver rose":   (1000006, PROGRESSION),
    "Marble":        (1000008, PROGRESSION),
    "Amulet":        (1000009, PROGRESSION),
    "Acorn":         (1000010, PROGRESSION),
    "Walnut":        (1000011, PROGRESSION),
    "Pinecone":      (1000012, PROGRESSION),
    "Feather":       (1000013, PROGRESSION),   # the cardinal's quill
    "Magic scroll":  (1000014, PROGRESSION),   # Scroll of Winter (reusable)
    "Tulip":         (1000015, PROGRESSION),
    "Flute":         (1000016, PROGRESSION),   # breaks the cave ice
    "Gold coin":     (1000019, PROGRESSION),   # -> well -> moonstone
    "Iron key":      (1000020, PROGRESSION),
    "Crystal ball":  (1000021, PROGRESSION),   # fixes the fountain -> blue spell
    "Apple":         (1000003, PROGRESSION),   # buys the Royal Chalice from the faun
    "Blueberries":   (1000024, PROGRESSION),
    "Orchid":        (1000026, PROGRESSION),   # red potion + on grave -> red spell
    "Royal chalice": (1000027, PROGRESSION),
    "Sceptre":       (1000028, PROGRESSION),
    "Crown":         (1000029, PROGRESSION),
    "Mallet":        (1000030, PROGRESSION),   # bell puzzle
    "Gold key":      (1000031, PROGRESSION),   # castle inner door (fireplace)
    "Hidden key":    (1000032, PROGRESSION),   # castle inner door (bells)
    "Fireberries":   (1000051, PROGRESSION),   # light the dark labyrinth
    "Ruby":          (1000201, PROGRESSION),   # red potion gem
    "Topaz":         (1000204, PROGRESSION),   # yellow potion gem
    "Sapphire":      (1000205, PROGRESSION),   # blue potion gem
    "Moonstone":     (1000207, PROGRESSION),   # -> wisp spell
    "Blue potion":   (1000400, PROGRESSION),
    "Red potion":    (1000401, PROGRESSION),
    "Yellow potion": (1000402, PROGRESSION),
    "Purple potion": (1000403, PROGRESSION),   # shrink -> enter faun's home
    "Orange potion": (1000404, PROGRESSION),   # pegasus -> Grave Island

    # --- useful (real items worth shuffling, not named in any rule) ---
    "Jewel":         (1000000, USEFUL),
    "Purple rose":   (1000007, USEFUL),
    "Empty flask":   (1000022, USEFUL),   # unlimited from Zanthia's cabin; not a gate
    "Magic water":   (1000023, USEFUL),
    "Rainbowstone":  (1000025, USEFUL),
    "Mirror":        (1000050, USEFUL),   # appears to be chamber scenery, not required
    "Fallen star":   (1000052, USEFUL),
    "Fish":          (1000053, USEFUL),
    "Mutton Leg":    (1000054, USEFUL),
    "Green potion":  (1000405, USEFUL),   # poison; making it is an optional check
    "Sunstone":      (1000200, USEFUL),
    "Peridot":       (1000202, USEFUL),
    "Emerald":       (1000203, USEFUL),
    "Amethyst":      (1000206, USEFUL),
    "Garnet":        (1000220, USEFUL),   # alt red-potion gem; birthstone candidate
    "Aquamarine":    (1000221, USEFUL),
    "Diamond":       (1000222, USEFUL),
    "Pearl":         (1000223, USEFUL),
    "Opal":          (1000224, USEFUL),
    "Onyx":          (1000225, USEFUL),
    "Lodestone":     (1000226, USEFUL),

    # --- filler (variety pad; get_filler_item_name returns "Loose Gem") ---
    "Loose Gem":     (1000990, FILLER),
    "Heavy Rock":    (1000018, FILLER),
    "Bone":          (1000060, FILLER),
    "Fish Bone":     (1000061, FILLER),
    "Mushroom":      (1000062, FILLER),
    "Shamrock":      (1000063, FILLER),
    "Ankh":          (1000064, FILLER),
    "Egg":           (1000065, FILLER),
}

FILLER_NAME = "Loose Gem"
# Filler identities used to pad the pool (cycled for variety).
FILLER_POOL = ["Loose Gem", "Heavy Rock", "Bone", "Fish Bone", "Mushroom", "Shamrock", "Ankh", "Egg"]

# ---------------------------------------------------------------------------
# Birthstone altar (Act 2, near Darm). Vanilla: a 4-slot gem altar (engine
# `_birthstoneGemTable`, gem ids 0-11 = the 12 calendar birthstones) whose reward
# is the magic Flute. Vanilla fixes slots 1 & 4 and randomizes the middle two.
#
# Randomizer: AP picks ALL 4 required gems per seed (no fixed slots); those 4 are
# promoted to PROGRESSION for the seed and the altar location is gated on holding
# them (the rulesdata `birthstone_set` token, resolved in rules.py). List order ==
# slot position (1..4) for the engine table and NPC hints.
# ---------------------------------------------------------------------------
BIRTHSTONES = [
    "Garnet", "Amethyst", "Aquamarine", "Diamond", "Emerald", "Pearl",
    "Ruby", "Peridot", "Sapphire", "Opal", "Topaz", "Onyx",
]
BIRTHSTONE_SLOTS = 4
# Token used in rulesdata for the altar; resolved to the chosen gems at runtime.
BIRTHSTONE_SET_TOKEN = "birthstone_set"


def choose_birthstones(rng) -> list[str]:
    """Pick the seed's BIRTHSTONE_SLOTS required gems (distinct, ordered by slot).
    `rng` is the world's seeded Random so the choice is reproducible (incl. UT)."""
    return rng.sample(BIRTHSTONES, BIRTHSTONE_SLOTS)

# Event items (id None) — earned capabilities / goal, never networked.
EVENT_ITEMS = ("Heal Spell", "Wisp Spell", "Blue Spell", "Red Spell", "Victory")

# ---------------------------------------------------------------------------
# Regions (forward-only act chain; see research/walkthrough_findings.md)
# ---------------------------------------------------------------------------
MENU = "Menu"
REGIONS = [
    "Brandons Home",
    "Emerald Forest",
    "Over The Bridge",   # Act 2a: Darm, heal hole, birthstone altar -> flute
    "Labyrinth",         # Act 2b: the cavern (entered by breaking the ice)
    "Act3 Wilds",        # Act 3: Zanthia, fountain, potions
    "Grave Island",      # Act 4a
    "Castle",            # Act 4b
    "Kyragem Chamber",
]

# (from, to, [required item/event names]) — single-edge gate. Linear chain.
EDGES: list[tuple[str, str, list[str]]] = [
    (MENU,              "Brandons Home",   []),
    ("Brandons Home",   "Emerald Forest",  []),
    ("Emerald Forest",  "Over The Bridge", ["Saw"]),                 # Herman fixes the bridge
    ("Over The Bridge", "Labyrinth",       ["Flute"]),               # flute breaks the ice
    ("Labyrinth",       "Act3 Wilds",      ["Wisp Spell"]),          # wisp across the chasm
    ("Act3 Wilds",      "Grave Island",    ["Orange potion"]),       # drink orange -> pegasus
    ("Grave Island",    "Castle",          ["Iron key", "Red Spell"]),  # invisible + iron key
    ("Castle",          "Kyragem Chamber", ["Crown", "Sceptre", "Royal chalice", "Gold key", "Hidden key"]),
]

# ---------------------------------------------------------------------------
# Real (networked) locations. (name, region, ap_id, [required item names])
# ---------------------------------------------------------------------------
LOCATIONS: list[tuple[str, str, int, list[str]]] = [
    # --- Brandons Home (Act 1 start) ---
    ("Brandon's Home - Kallak's Note",            "Brandons Home",   1010000, []),
    ("Brandon's Home - Desk Drawer",              "Brandons Home",   1010001, []),
    ("Brandon's Home - Garnet",                   "Brandons Home",   1010002, []),
    ("Brandon's Home - Apple",                    "Brandons Home",   1010003, []),

    # --- Emerald Forest (Act 1: amulet chain + bridge) ---
    ("Willow - Teardrop Catch",                   "Emerald Forest",  1010010, []),
    ("Forest - Lavender Rose",                    "Emerald Forest",  1010011, []),
    ("Forest - Saw",                              "Emerald Forest",  1010012, []),
    ("Forest - Tulip",                            "Emerald Forest",  1010013, []),
    ("Forest - Amethyst Gem",                     "Emerald Forest",  1010014, []),
    ("Forest - Aquamarine Gem",                   "Emerald Forest",  1010015, []),
    ("Forest - Emerald Gem",                      "Emerald Forest",  1010016, []),
    ("Forest - Sapphire Gem",                     "Emerald Forest",  1010017, []),
    ("Forest - Ruby Gem",                         "Emerald Forest",  1010018, []),
    ("Forest - Opal Gem",                         "Emerald Forest",  1010019, []),
    ("Temple - Purple Rose",                      "Emerald Forest",  1010020, []),
    ("Brynn - Give Note & Rose (Silver Rose)",    "Emerald Forest",  1010021, ["Note", "Lavender rose"]),
    ("Merith - Catch the Marble",                 "Emerald Forest",  1010022, ["Teardrop"]),
    ("Temple Altar - Rose & Marble (Amulet)",     "Emerald Forest",  1010023, ["Silver rose", "Marble"]),
    ("Herman - Repair Bridge (Saw turn-in)",      "Emerald Forest",  1010024, ["Saw"]),

    # --- Over The Bridge (Act 2a: Darm, heal hole, birthstone altar, well) ---
    ("Darm's Wood - Acorn",                       "Over The Bridge", 1010040, []),
    ("Darm's Wood - Walnut",                      "Over The Bridge", 1010041, []),
    ("Darm's Wood - Pinecone",                    "Over The Bridge", 1010042, []),
    ("Darm's Wood - Peridot Gem",                 "Over The Bridge", 1010043, []),
    ("Darm's Wood - Diamond Gem",                 "Over The Bridge", 1010044, []),
    ("Darm's Wood - Topaz Gem",                   "Over The Bridge", 1010045, []),
    ("Darm's Wood - Onyx Gem",                    "Over The Bridge", 1010046, []),
    ("Cardinal - Heal & Get Quill",               "Over The Bridge", 1010047, ["Heal Spell"]),
    ("Darm - Give Quill (Scroll of Winter)",      "Over The Bridge", 1010048, ["Feather"]),
    # Birthstone gem altar (vanilla reward = Flute). Gated on the seed's 4 chosen
    # birthstones; applied dynamically in rules.py (static requires stays empty).
    ("Marble Altar - Birthstone Puzzle (Flute)",  "Over The Bridge", 1010049, []),
    ("Magic Well - Drop Coin (Moonstone)",        "Over The Bridge", 1010050, ["Gold coin"]),

    # --- Labyrinth (Act 2b: entered by breaking the ice; fireberries to traverse) ---
    ("Labyrinth - Fireberries",                   "Labyrinth",       1010060, []),
    ("Labyrinth - Loose Rock",                    "Labyrinth",       1010061, ["Fireberries"]),
    ("Labyrinth - Gold Coin",                     "Labyrinth",       1010062, ["Fireberries"]),
    ("Labyrinth - Lodestone Gem",                 "Labyrinth",       1010063, ["Fireberries"]),
    ("Labyrinth - Iron Key (Freeze the Lava)",    "Labyrinth",       1010064, ["Fireberries", "Wisp Spell", "Magic scroll"]),

    # --- Act3 Wilds (Zanthia / potions) ---
    ("Zanthia - Crystal Ball (Scroll on Flame)",  "Act3 Wilds",      1010100, ["Magic scroll"]),
    ("Zanthia - Magic Water",                     "Act3 Wilds",      1010101, []),
    ("Zanthia - Empty Flask",                     "Act3 Wilds",      1010102, []),
    ("Blueberry Field - Blueberries",             "Act3 Wilds",      1010103, []),
    ("Beach - Orchid",                            "Act3 Wilds",      1010104, []),
    ("Beach - Pearl Gem",                         "Act3 Wilds",      1010105, []),
    ("Secret Passage - Rainbowstone",             "Act3 Wilds",      1010106, []),
    ("Act3 - Sunstone Gem",                       "Act3 Wilds",      1010107, []),
    ("Zanthia - Brew Blue Potion",                "Act3 Wilds",      1010108, ["Blueberries", "Sapphire"]),
    ("Zanthia - Brew Red Potion",                 "Act3 Wilds",      1010109, ["Orchid", "Ruby"]),
    ("Zanthia - Brew Yellow Potion",              "Act3 Wilds",      1010110, ["Tulip", "Topaz"]),
    ("Zanthia - Brew Orange Potion",              "Act3 Wilds",      1010111, ["Red potion", "Yellow potion"]),
    ("Zanthia - Brew Purple Potion",              "Act3 Wilds",      1010112, ["Blue potion", "Red potion"]),
    # Green = Blue + Yellow. Poison if DRUNK, but making it is a valid check.
    ("Zanthia - Brew Green Potion",               "Act3 Wilds",      1010113, ["Blue potion", "Yellow potion"]),
    ("Faun - Give Apple (Royal Chalice)",         "Act3 Wilds",      1010114, ["Blue Spell", "Purple potion", "Apple"]),

    # --- Grave Island (Act 4a: via Orange Potion / pegasus) ---
    ("Grave Island - Fallen Star",                "Grave Island",    1010130, []),
    ("Grave Island - Diamond Gem",                "Grave Island",    1010131, []),

    # --- Castle (Act 4b: via Iron key + invisibility) ---
    ("Castle Library - Book Puzzle (Crown)",      "Castle",          1010140, []),
    ("Castle Kitchen - Poker (Sceptre)",          "Castle",          1010141, []),
    ("Castle - Fireplace Key (Blue Spell)",       "Castle",          1010142, ["Blue Spell"]),
    ("Castle - Music Room Mallet (Heal Herman)",  "Castle",          1010143, ["Heal Spell"]),
    ("Castle - Bell Puzzle Key",                  "Castle",          1010144, ["Heal Spell", "Mallet"]),
    ("Castle - Mirror",                           "Castle",          1010145, []),
    ("Castle - Aquamarine Gem",                   "Castle",          1010146, []),
]

# Event locations: (name, region, granted_event_item, [required item names]).
# id is None (not networked). "Victory" drives the completion condition.
EVENT_LOCATIONS: list[tuple[str, str, str, list[str]]] = [
    ("Deadwood Hole - Drop Nuts (Earn Heal Power)",      "Over The Bridge", "Heal Spell", ["Amulet", "Acorn", "Walnut", "Pinecone"]),
    ("Wisp Pedestal - Place Moonstone (Earn Wisp Power)", "Labyrinth",      "Wisp Spell", ["Amulet", "Moonstone", "Fireberries"]),
    ("Fountain - Drink Water (Earn Blue Power)",         "Act3 Wilds",      "Blue Spell", ["Amulet", "Crystal ball"]),
    ("Grave - Place Orchid (Earn Red Power)",            "Grave Island",    "Red Spell",  ["Amulet", "Orchid"]),
    ("Kyragem Chamber - Defeat Malcolm (Mirror)",        "Kyragem Chamber", "Victory",    ["Red Spell"]),
]

# Convenience views
ITEM_NAME_TO_ID = {name: data[0] for name, data in ITEM_TABLE.items()}
LOCATION_NAME_TO_ID = {name: loc_id for (name, _region, loc_id, _req) in LOCATIONS}
