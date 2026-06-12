"""Generate the engine-ID <-> AP-ID item crosswalk for Kyrandia Book 1.

Engine list = k1ItemNames extracted from scummvm.exe (matches debugger `give`, 0-106).
AP ids = kyrandia_book1_randomizer_plan.md (AP-internal space, book-1 base 1,000,000).
Output = kyra1_items.json with top-level "items".
"""
import json
import re
from pathlib import Path

# Paths resolve relative to the repo root (this script lives in pyscripts/).
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "research" / "kyra1_item_ids.txt"
OUT = ROOT / "research" / "kyra1_items.json"

# --- authoritative engine list from the file extracted from scummvm.exe ---
engine = {}
for line in open(SRC, encoding="utf-8"):
    if line.lstrip().startswith("#"):
        continue
    m = re.match(r"\s*(\d+)\s+(.+?)\s*$", line)
    if m:
        engine[int(m.group(1))] = m.group(2)

# --- charge / state ladders ---
# Repeated same-name engine ids are NOT interchangeable copies: the engine encodes
# a consumable's remaining charges/uses as separate, decrementing item ids.
# The HEAD id (full charges) carries the AP mapping; the rest are runtime states.
# The AP translation layer must: (outgoing) treat ANY member id as "this item" on
# pickup, and (incoming) grant the HEAD (full) id. kind: how sure we are it's charges.
STATE_GROUPS = [
    {"ids": list(range(29, 34)), "kind": "charges-confirmed",
     "note": "Fireberries charge ladder (29 = most berries/charges ... 33 = least); each "
             "use plucks a berry and decrements. Engine 28 'Everglowing Fireberries' is the "
             "separate infinite source. Exact per-id charge counts to confirm."},
    {"ids": list(range(80, 90)), "kind": "charges-likely",
     "note": "Scroll uses-remaining ladder (10 states); plan notes the scroll is used many "
             "times. Confirm decrement direction and exact use counts."},
    {"ids": list(range(90, 95)), "kind": "unverified",
     "note": "Parchment scrap (5 states); likely a state ladder. Verify."},
    {"ids": [60, 61], "kind": "unverified",
     "note": "Red Potion: 2 entries; could be 2 instances (plan 'Red x2') or full/used states. Verify."},
    {"ids": [62, 63], "kind": "unverified", "note": "Blue Potion: 2 entries; instances-vs-states unverified."},
    {"ids": [64, 65], "kind": "unverified", "note": "Yellow Potion: 2 entries; instances-vs-states unverified."},
    {"ids": [70, 71], "kind": "unverified", "note": "Fresh Water: 2 entries; instances-vs-states unverified."},
    {"ids": [72, 73], "kind": "unverified", "note": "Salt Water: 2 entries; instances-vs-states unverified."},
    {"ids": [74, 75], "kind": "unverified", "note": "Mineral Water: 2 entries; instances-vs-states unverified."},
    {"ids": [76, 77], "kind": "unverified", "note": "Magical Water: 2 entries; instances-vs-states unverified."},
    {"ids": [78, 79], "kind": "unverified", "note": "Empty Flask: 2 entries; instances-vs-states unverified."},
]
HEAD = {}        # head id -> group dict
STATE_OF = {}    # non-head id -> (head_id, state_index, group dict)
for g in STATE_GROUPS:
    ids = g["ids"]
    HEAD[ids[0]] = g
    for idx, d in enumerate(ids):
        if idx:
            STATE_OF[d] = (ids[0], idx, g)

INGAME_VERIFIED = {1, 4, 10, 50}  # user tested live via `give`

# --- AP mapping keyed by ENGINE id: (ap_id, ap_name, confidence, note) ---
M = {
    0:  (None, None, "unmapped", "Gem. Candidate for plan 1000000 starting jewel or scattered-gem pool."),
    1:  (1000206, "Amethyst", "verified", "Live give-tested."),
    2:  (None, None, "unmapped", "Gem; not yet in AP plan (scattered-gem pool)."),
    3:  (None, None, "unmapped", "Gem; not yet in AP plan (scattered-gem pool)."),
    4:  (1000203, "Emerald", "verified", "Live give-tested."),
    5:  (None, None, "unmapped", "Gem (Pearl); not in AP plan."),
    6:  (1000201, "Ruby", "name-exact", "Predicted by birthstone-index pattern; verify with give 6."),
    7:  (1000202, "Peridot", "name-exact", "Plan 1000202."),
    8:  (1000205, "Sapphire", "name-exact", "Plan 1000205."),
    9:  (None, None, "unmapped", "Gem (Opal); not in AP plan."),
    10: (1000204, "Topaz", "verified", "Live give-tested."),
    11: (None, None, "unmapped", "Gem (Onyx); not in AP plan."),
    12: (1000200, "Sunstone", "name-exact", "Plan 1000200 (altar slot 1)."),
    13: (1000207, "Moonstone", "name-exact", "Plan 1000207 (wishing well)."),
    14: (1000025, "Rainbowstone", "name-exact", "Plan 1000025."),
    15: (None, None, "unmapped", "Gem (Lodestone); not in AP plan."),
    16: (1000005, "Lavender rose", "semantic", "Engine 'Rose'; plan lavender->silver rose chain. Engine may recolor one Rose object."),
    17: (1000015, "Tulip", "name-exact", "Plan 1000015 (yellow potion)."),
    18: (1000026, "Orchid", "semantic", "Engine 'Orchid' = plan red exotic flower (red potion)."),
    19: (1000006, "Silver rose", "name-exact", "Plan 1000006."),
    20: (None, None, "unmapped", "Silver Statuette; not in AP plan."),
    21: (None, None, "unmapped", "Silver Coin; not in AP plan (plan has Gold coin only)."),
    22: (1000019, "Gold coin", "name-exact", "Plan 1000019 (wishing well -> moonstone)."),
    23: (None, None, "unmapped", "Gold Ring; not in AP plan."),
    24: (1000027, "Royal chalice", "name-exact", "Plan 1000027 (castle ending)."),
    25: (1000012, "Pinecone", "name-exact", "Plan 1000012 (dropped in hole)."),
    26: (1000010, "Acorn", "name-exact", "Plan 1000010 (dropped in hole)."),
    27: (1000011, "Walnut", "name-exact", "Plan 1000011 (dropped in hole)."),
    28: (None, None, "unmapped", "Everglowing Fireberries (distinct from plain Fireberries)."),
    29: (None, None, "unmapped", "Fireberries (primary of 29-33). Fire-protection consumable."),
    34: (None, None, "unmapped", "Fish; not in AP plan."),
    35: (None, None, "unmapped", "Fish Bone; not in AP plan."),
    36: (None, None, "unmapped", "Mutton Leg; not in AP plan."),
    37: (None, None, "unmapped", "Bone; not in AP plan."),
    38: (1000003, "Apple", "name-exact", "Plan 1000003. SOFTLOCK risk: eating -> Apple Core (39)."),
    39: (None, None, "unmapped", "Apple Core (consumed apple state)."),
    40: (1000024, "Blueberries", "name-exact", "Plan 1000024 (blue potion)."),
    41: (None, None, "unmapped", "Mushroom; not in AP plan."),
    42: (1000001, "Note", "name-exact", "Plan 1000001 (Kallak note -> Brynn)."),
    43: (1000008, "Marble", "name-exact", "Plan 1000008 (altar)."),
    44: (1000002, "Saw", "name-exact", "Plan 1000002 (-> Herman, bridge)."),
    45: (None, None, "unmapped", "Ankh; not in AP plan."),
    46: (1000013, "Feather", "name-exact", "Plan 1000013 (healed bird -> Darm)."),
    47: (None, None, "unmapped", "Egg; not in AP plan."),
    48: (1000202, "Peridot (leaf source?)", "tentative", "Engine 'Leaf'; plan notes peridot from dark-forest leaf. May be source object, not the gem. Verify."),
    49: (None, None, "unmapped", "Shamrock; not in AP plan."),
    50: (None, None, "unmapped", "Fallen Star (live give-tested = 50). Not in AP plan; candidate filler/check."),
    51: (1000021, "Crystal ball", "name-exact", "Plan 1000021 (fire puzzle)."),
    52: (1000004, "Teardrop", "name-exact", "Plan 1000004 (summons Merith at willow). Test target; verify with give 52."),
    53: (None, None, "unmapped", "Mirror; relates to mirror/Kyragem ending. Likely event, not pickup."),
    54: (None, None, "unmapped", "Ice Shard; not in AP plan."),
    55: (1000016, "Flute", "name-exact", "Plan 1000016 (stops Malcolm at grotto)."),
    56: (None, None, "unmapped", "Hourglass; not in AP plan."),
    57: (1000020, "Iron key", "name-exact", "Plan 1000020 (castle)."),
    58: (None, None, "tentative", "Jade Key. Plan has Iron/Gold/Hidden; Jade unassigned. Verify which is catacombs hidden key."),
    59: (1000032, "Hidden key (catacombs)", "tentative", "Engine 'Obsidion Key'; tentatively catacombs hidden key. Verify vs Jade Key (58)."),
    60: (1000401, "Red potion", "semantic", "Plan 1000401 'Red (x2)' matches engine duplicate 60/61."),
    62: (1000400, "Blue potion", "semantic", "Plan 1000400."),
    64: (1000402, "Yellow potion", "semantic", "Plan 1000402."),
    66: (None, None, "unmapped", "Green Potion; not in AP plan."),
    67: (1000404, "Orange potion", "semantic", "Plan 1000404."),
    68: (1000403, "Purple potion", "semantic", "Plan 1000403."),
    69: (None, None, "unmapped", "Potion of Rainbows; not in AP plan."),
    70: (None, None, "unmapped", "Fresh Water (primary 70/71)."),
    72: (None, None, "unmapped", "Salt Water (primary 72/73)."),
    74: (None, None, "unmapped", "Mineral Water (primary 74/75)."),
    76: (1000023, "Magic water", "semantic", "Engine 'Magical Water' (primary 76/77); plan 1000023 (for Zanthia)."),
    78: (1000022, "Empty flask", "name-exact", "Plan 1000022 (primary 78/79, container)."),
    80: (1000014, "Magic scroll", "semantic", "Engine 'Scroll' (primary 80-89, 10 instances); plan 1000014 fire-protection."),
    90: (None, None, "unmapped", "Parchment scrap (primary 90-94). Possibly plan library 'books' 1000033."),
    95: (1000603, "Red stone (amulet)", "tentative", "Engine 'Red Magestone'; likely amulet spell-stone (plan 1000603). Verify."),
    96: (None, None, "tentative", "Orange Magestone; amulet spell-stone family. Verify color->power."),
    97: (1000604, "Yellow stone (amulet)", "tentative", "Engine 'Yellow Magestone'; likely amulet spell-stone (plan 1000604). Verify."),
    98: (None, None, "tentative", "Green Magestone; amulet spell-stone family. Possibly Heal (plan 1000600). Verify."),
    99: (None, None, "tentative", "Blue-Green Magestone; amulet spell-stone family. Verify."),
    100: (1000602, "Blue stone (amulet)", "tentative", "Engine 'Blue Magestone'; likely amulet spell-stone (plan 1000602). Verify."),
    101: (1000601, "Wisp/teleport (amulet)", "tentative", "Engine 'Purple Magestone'; likely amulet wisp/teleport stone (plan 1000601). Verify."),
    102: (1000018, "Rock", "semantic", "Engine 'Heavy rock'; plan 1000018 'Rock x5' (labyrinth filler)."),
    103: (1000029, "Crown", "name-exact", "Engine 'Royal Crown'; plan 1000029."),
    104: (1000028, "Sceptre", "name-exact", "Engine 'Royal Sceptre'; plan 1000028."),
    105: (1000031, "Gold key", "name-exact", "Plan 1000031 (from safe)."),
    106: (None, None, "unmapped", "Engine sentinel 'Unknown item' (kItemNone display). Not a real pickup."),
}


def cat(i):
    if 0 <= i <= 15: return "gem"
    if 16 <= i <= 19: return "flower"
    if 20 <= i <= 24: return "valuable"
    if 25 <= i <= 27: return "tree-drop"
    if 28 <= i <= 33: return "fireberries"
    if 34 <= i <= 41: return "food/nature"
    if 42 <= i <= 49: return "quest-misc"
    if 50 <= i <= 56: return "special"
    if 57 <= i <= 59: return "key"
    if 60 <= i <= 69: return "potion"
    if 70 <= i <= 77: return "water"
    if i in (78, 79): return "container"
    if 80 <= i <= 89: return "scroll"
    if 90 <= i <= 94: return "parchment"
    if 95 <= i <= 101: return "magestone"
    if i == 102: return "filler"
    if 103 <= i <= 105: return "regalia/key"
    return "sentinel"


items = []
for i in range(0, 107):
    # Non-head state of a charge ladder: no AP mapping of its own; points at the head.
    if i in STATE_OF:
        head, idx, g = STATE_OF[i]
        items.append({
            "engine_id": i, "engine_name": engine[i], "category": cat(i),
            "ap_id": None, "ap_name": None, "confidence": "state",
            "charge_ladder": {"role": "state", "primary": head, "index": idx,
                              "members": g["ids"], "kind": g["kind"]},
            "ingame_verified": i in INGAME_VERIFIED,
            "notes": "Charge/use state %d of engine id %d ('%s'). %s" % (idx, head, engine[head], g["note"]),
        })
        continue
    ap_id = ap_name = None
    conf = "unmapped"
    note = ""
    if i in M:
        ap_id, ap_name, conf, note = M[i]
    ladder = None
    if i in HEAD:
        g = HEAD[i]
        ladder = {"role": "primary", "primary": i, "members": g["ids"], "kind": g["kind"]}
        note = (note + " " if note else "") + g["note"]
    items.append({
        "engine_id": i, "engine_name": engine[i], "category": cat(i),
        "ap_id": ap_id, "ap_name": ap_name, "confidence": conf,
        "charge_ladder": ladder, "ingame_verified": i in INGAME_VERIFIED,
        "notes": note,
    })

ap_unmapped = [
    {"ap_id": 1000000, "ap_name": "Jewel (starting, Kallak's desk)", "reason": "Generic loose gem; maps to one of engine gem ids 0-15 (which TBD by playthrough)."},
    {"ap_id": 1000007, "ap_name": "Purple rose", "reason": "No distinct engine entry; likely recolor/state of Rose(16) or conflated with Orchid(18). Verify."},
    {"ap_id": 1000009, "ap_name": "Amulet", "reason": "Special UI artifact / spell carrier, not in the k1ItemNames pickup table."},
    {"ap_id": 1000017, "ap_name": "Knife (thrown back)", "reason": "Combat-beat event item; no entry in item-name table."},
    {"ap_id": 1000030, "ap_name": "Mallet", "reason": "Music-puzzle item; no matching entry. Verify (may be scene object)."},
    {"ap_id": 1000033, "ap_name": "Books (Opal/Potions/Enchantment/Nature)", "reason": "Library puzzle objects; possibly Parchment scrap(90-94) or pure scene objects."},
]

out = {
    "_meta": {
        "game": "The Legend of Kyrandia - Book 1",
        "engine": "ScummVM 2.0.0 (KyraEngine_LoK), GOG CD/DOS English",
        "engine_item_source": "k1ItemNames table extracted from scummvm.exe; ids match debugger give (0-106).",
        "ap_id_source": "kyrandia_book1_randomizer_plan.md (AP-internal id space, book-1 base 1,000,000).",
        "ingame_verified_engine_ids": sorted(INGAME_VERIFIED),
        "confidence_legend": {
            "verified": "engine id confirmed live via give",
            "name-exact": "engine name == AP concept",
            "semantic": "same concept, different wording",
            "tentative": "best-guess mapping, needs playthrough verification",
            "state": "a charge/use state of a ladder; AP mapping lives on the ladder head",
            "unmapped": "engine item has no AP id assigned yet",
        },
        "charge_ladders": "Repeated same-name engine ids are decrementing charge/use states of ONE logical item, not interchangeable copies (confirmed for Fireberries: 29=most charges ... 33=least). See each item's 'charge_ladder' field. The HEAD id holds the AP mapping. Translation layer: outgoing = treat ANY member id as the item on pickup; incoming = grant the HEAD (full) id.",
        "notes": "engine_id is the 'from' side of the AP translation layer; ap_id is the 'to' side.",
    },
    "items": items,
    "ap_items_without_engine_id": ap_unmapped,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

mapped = sum(1 for x in items if x["ap_id"] is not None)
states = sum(1 for x in items if x["confidence"] == "state")
unm = sum(1 for x in items if x["confidence"] == "unmapped")
tent = sum(1 for x in items if x["confidence"] == "tentative")
heads = sum(1 for x in items if x.get("charge_ladder") and x["charge_ladder"]["role"] == "primary")
print("Wrote kyra1_items.json: %d engine entries" % len(items))
print("  mapped to AP id: %d | tentative: %d | ladder-states: %d | unmapped: %d" % (mapped, tent, states, unm))
print("  charge ladders: %d (heads) | AP items with no engine entry: %d" % (heads, len(ap_unmapped)))
