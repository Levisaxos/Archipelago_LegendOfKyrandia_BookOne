"""Canonical data tables for the Legend of Kyrandia - Book 1 apworld.

Single source of truth for items, locations, regions and edges. The research
deliverable `research/locations.json` is GENERATED from this module
(pyscripts/dump_research.py) so the two never diverge.

DRAFT v2 (2026-06-11): a much broader first pass derived from the plan doc +
walkthrough knowledge, NOT yet verified against a live playthrough. Confidence
varies per entry — see research/locations.json + research/logic.md. The
authoritative location list will come from Phase 1 read-only instrumentation
(logging every (sceneId, slot) pickup + flag-set), which is build-blocked.

Logic model: "Model A" — region edges and turn-in/puzzle locations are gated on
the REAL game items the vanilla game uses at that transition (item randomizer).

INVARIANT: every item that appears in any `requires` list MUST be classified
PROGRESSION (or be an event item). Only progression/event items participate in
Archipelago's reachability sweep; a `useful`/`filler` item named in a rule could
never satisfy it. pyscripts/build_apworld-style validation enforces this.
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
    "Feather":       (1000013, PROGRESSION),
    "Magic scroll":  (1000014, PROGRESSION),
    "Tulip":         (1000015, PROGRESSION),
    "Flute":         (1000016, PROGRESSION),
    "Gold coin":     (1000019, PROGRESSION),
    "Iron key":      (1000020, PROGRESSION),
    "Empty flask":   (1000022, PROGRESSION),
    "Blueberries":   (1000024, PROGRESSION),
    "Orchid":        (1000026, PROGRESSION),
    "Royal chalice": (1000027, PROGRESSION),
    "Sceptre":       (1000028, PROGRESSION),
    "Crown":         (1000029, PROGRESSION),
    "Mallet":        (1000030, PROGRESSION),
    "Gold key":      (1000031, PROGRESSION),
    "Mirror":        (1000050, PROGRESSION),
    "Fireberries":   (1000051, PROGRESSION),
    "Ruby":          (1000201, PROGRESSION),
    "Topaz":         (1000204, PROGRESSION),
    "Sapphire":      (1000205, PROGRESSION),
    "Moonstone":     (1000207, PROGRESSION),
    "Blue potion":   (1000400, PROGRESSION),
    "Red potion":    (1000401, PROGRESSION),
    "Yellow potion": (1000402, PROGRESSION),

    # --- useful (real items worth shuffling, not named in any rule) ---
    "Jewel":         (1000000, USEFUL),
    "Apple":         (1000003, USEFUL),
    "Purple rose":   (1000007, USEFUL),
    "Crystal ball":  (1000021, USEFUL),
    "Magic water":   (1000023, USEFUL),
    "Rainbowstone":  (1000025, USEFUL),
    "Hidden key":    (1000032, USEFUL),
    "Fallen star":   (1000052, USEFUL),
    "Fish":          (1000053, USEFUL),
    "Mutton Leg":    (1000054, USEFUL),
    "Purple potion": (1000403, USEFUL),
    "Orange potion": (1000404, USEFUL),
    "Green potion":  (1000405, USEFUL),
    "Sunstone":      (1000200, USEFUL),
    "Peridot":       (1000202, USEFUL),
    "Emerald":       (1000203, USEFUL),
    "Amethyst":      (1000206, USEFUL),
    "Garnet":        (1000220, USEFUL),
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

# Event items (id None) — earned capabilities / goal, never networked. Created
# inline and placed locked on event locations. Engine-flag mapping is the fork's
# concern. Heal=1000600, Wisp=1000601 in the plan's amulet space (reference only).
EVENT_ITEMS = ("Heal Spell", "Wisp Spell", "Red Spell", "Blue Spell", "Victory")

# ---------------------------------------------------------------------------
# Regions
# ---------------------------------------------------------------------------
MENU = "Menu"
REGIONS = [
    "Brandons Home",
    "Emerald Forest",
    "Over The Bridge",
    "Caves Entrance",
    "Inner Caves",
    "Act3 Wilds",
    "Grave Island",
    "Castle",
    "Catacombs",
    "Kyragem Chamber",
]

# (from, to, [required item/event names]) — see research/logic.md
EDGES: list[tuple[str, str, list[str]]] = [
    (MENU,              "Brandons Home",   []),
    ("Brandons Home",   "Emerald Forest",  []),
    ("Emerald Forest",  "Over The Bridge", ["Saw"]),
    ("Over The Bridge", "Caves Entrance",  ["Flute"]),
    ("Caves Entrance",  "Inner Caves",     ["Fireberries"]),    # break the ice
    ("Inner Caves",     "Act3 Wilds",      ["Wisp Spell"]),     # cross the chasm
    ("Act3 Wilds",      "Grave Island",    []),                 # pegasus (free, TODO)
    ("Grave Island",    "Castle",          ["Iron key"]),
    ("Castle",          "Catacombs",       []),
    ("Castle",          "Kyragem Chamber", ["Crown", "Sceptre", "Royal chalice"]),
]

# ---------------------------------------------------------------------------
# Real (networked) locations. (name, region, ap_id, [required item names])
# ---------------------------------------------------------------------------
LOCATIONS: list[tuple[str, str, int, list[str]]] = [
    # --- Brandons Home (tree house) ---
    ("Brandon's Home - Kallak's Note",            "Brandons Home",   1010000, []),
    ("Brandon's Home - Desk Drawer",              "Brandons Home",   1010001, []),
    ("Brandon's Home - Garnet (tree house)",      "Brandons Home",   1010002, []),

    # --- Emerald Forest (Act 1) ---
    ("Willow - Teardrop Catch",                   "Emerald Forest",  1010010, []),
    ("Forest - Lavender Rose",                    "Emerald Forest",  1010011, []),
    ("Forest - Acorn",                            "Emerald Forest",  1010012, []),
    ("Forest - Walnut",                           "Emerald Forest",  1010013, []),
    ("Forest - Pinecone",                         "Emerald Forest",  1010014, []),
    ("Forest - Apple",                            "Emerald Forest",  1010015, []),
    ("Forest - Saw",                              "Emerald Forest",  1010016, []),
    ("Temple Altar - Marble",                     "Emerald Forest",  1010017, []),
    ("Temple Altar - Purple Rose",                "Emerald Forest",  1010018, []),
    ("Forest - Amethyst Gem",                     "Emerald Forest",  1010019, []),
    ("Forest - Aquamarine Gem",                   "Emerald Forest",  1010020, []),
    ("Forest - Emerald Gem",                      "Emerald Forest",  1010021, []),
    ("Forest - Sapphire Gem",                     "Emerald Forest",  1010022, []),
    ("Forest - Ruby Gem",                         "Emerald Forest",  1010023, []),
    ("Brynn - Give Note & Rose (Silver Rose)",    "Emerald Forest",  1010024, ["Note", "Lavender rose"]),
    ("Merith - Summon at Willow",                 "Emerald Forest",  1010025, ["Teardrop"]),
    ("Temple Altar - Birthstone Puzzle (Amulet)", "Emerald Forest",  1010026, ["Silver rose", "Marble"]),
    ("Herman - Repair Bridge (Saw turn-in)",      "Emerald Forest",  1010027, ["Saw"]),

    # --- Over The Bridge (Act 1b) ---
    ("Over Bridge - Flute",                       "Over The Bridge", 1010040, []),
    ("Over Bridge - Gold Coin",                   "Over The Bridge", 1010041, []),
    ("Over Bridge - Peridot Gem",                 "Over The Bridge", 1010042, []),
    ("Over Bridge - Diamond Gem",                 "Over The Bridge", 1010043, []),
    ("Over Bridge - Topaz Gem",                   "Over The Bridge", 1010044, []),
    ("Bird - Heal & Get Feather",                 "Over The Bridge", 1010045, ["Heal Spell"]),
    ("Darm - Give Feather (Magic Scroll)",        "Over The Bridge", 1010046, ["Feather"]),
    ("Grotto - Get Past Malcolm (Flute)",         "Over The Bridge", 1010047, ["Flute"]),

    # --- Caves Entrance (Act 2) ---
    ("Wishing Well - Drop Coin",                  "Caves Entrance",  1010060, ["Gold coin"]),
    ("Caves - Fireberries",                       "Caves Entrance",  1010061, []),
    ("Caves - Break the Ice",                     "Caves Entrance",  1010062, ["Fireberries"]),
    ("Caves - Onyx Gem",                          "Caves Entrance",  1010063, []),
    ("Caves - Opal Gem",                          "Caves Entrance",  1010064, []),
    ("Caves - Pearl Gem",                         "Caves Entrance",  1010065, []),

    # --- Inner Caves (Act 2, past the ice) ---
    ("Lava - Iron Key",                           "Inner Caves",     1010080, ["Magic scroll"]),
    ("Caves - Crystal Ball",                      "Inner Caves",     1010081, ["Magic scroll"]),
    ("Inner Caves - Loose Rock",                  "Inner Caves",     1010082, []),
    ("Inner Caves - Lodestone Gem",               "Inner Caves",     1010083, []),

    # --- Act3 Wilds (Zanthia / potions) ---
    ("Zanthia - Magic Water",                     "Act3 Wilds",      1010100, []),
    ("Zanthia - Empty Flask",                     "Act3 Wilds",      1010101, []),
    ("Blueberry Field - Blueberries",             "Act3 Wilds",      1010102, []),
    ("Secret Passage - Rainbowstone",             "Act3 Wilds",      1010103, []),
    ("Crystal Towers - Orchid",                   "Act3 Wilds",      1010104, []),
    ("Act3 - Tulip",                              "Act3 Wilds",      1010105, []),
    ("Floating Chalice - Royal Chalice",          "Act3 Wilds",      1010106, []),
    ("Act3 - Sunstone Gem",                       "Act3 Wilds",      1010107, []),
    ("Act3 - Garnet Gem",                         "Act3 Wilds",      1010108, []),
    ("Zanthia - Brew Blue Potion",                "Act3 Wilds",      1010109, ["Blueberries", "Sapphire", "Empty flask"]),
    ("Zanthia - Brew Red Potion",                 "Act3 Wilds",      1010110, ["Orchid", "Ruby", "Empty flask"]),
    ("Zanthia - Brew Yellow Potion",              "Act3 Wilds",      1010111, ["Tulip", "Topaz", "Empty flask"]),
    ("Zanthia - Brew Purple Potion",              "Act3 Wilds",      1010112, ["Blue potion", "Red potion"]),
    ("Zanthia - Brew Orange Potion",              "Act3 Wilds",      1010113, ["Yellow potion", "Red potion"]),

    # --- Grave Island (Act 4 entry) ---
    ("Grave Island - Fallen Star",                "Grave Island",    1010130, []),
    ("Grave Island - Diamond Gem",                "Grave Island",    1010131, []),

    # --- Castle (Act 4) ---
    ("Castle Library - Book Puzzle (Crown)",      "Castle",          1010140, []),
    ("Castle Upstairs - Open Safe (Gold Key)",    "Castle",          1010141, []),
    ("Castle Upstairs - Music Puzzle",            "Castle",          1010142, ["Mallet"]),
    ("Castle Upstairs - Sceptre",                 "Castle",          1010143, ["Gold key"]),
    ("Castle Kitchen - Pickup",                   "Castle",          1010144, []),
    ("Castle - Mallet",                           "Castle",          1010145, []),
    ("Castle - Mirror",                           "Castle",          1010146, []),

    # --- Catacombs (Act 4, side) ---
    ("Catacombs - Hidden Key",                    "Catacombs",       1010160, ["Blue Spell"]),
    ("Catacombs - Aquamarine Gem",                "Catacombs",       1010161, []),
]

# Event locations: (name, region, granted_event_item, [required item names]).
# id is None (not networked). "Victory" drives the completion condition.
EVENT_LOCATIONS: list[tuple[str, str, str, list[str]]] = [
    ("Hole - Drop Nuts (Earn Heal Power)",     "Emerald Forest",  "Heal Spell", ["Amulet", "Acorn", "Walnut", "Pinecone"]),
    ("Cave Altar - Place Moonstone (Earn Wisp Power)", "Inner Caves", "Wisp Spell", ["Amulet", "Moonstone"]),
    ("Grave - Place Lavender Rose (Earn Red Power)",   "Grave Island", "Red Spell",  ["Amulet", "Lavender rose"]),
    ("Catacombs - Forcefield (Earn Blue Power)",       "Catacombs",   "Blue Spell", ["Amulet"]),
    ("Kyragem Chamber - Defeat Malcolm (Turn to Stone)", "Kyragem Chamber", "Victory", ["Crown", "Sceptre", "Royal chalice", "Mirror", "Red Spell"]),
]

# Convenience views
ITEM_NAME_TO_ID = {name: data[0] for name, data in ITEM_TABLE.items()}
LOCATION_NAME_TO_ID = {name: loc_id for (name, _region, loc_id, _req) in LOCATIONS}
