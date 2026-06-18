"""Per-check access rules for the Legend of Kyrandia - Book 1 apworld.

Human-readable requirement table: every networked location and every event
location, with the items / capabilities needed to reach it. Companion to
`data.py` (items, ids, regions) and `research/walkthrough_findings.md` (the
authoritative quest chain that justifies each requirement).

------------------------------------------------------------------------------
RULE LANGUAGE  (OR-of-ANDs, same shape as the Ori worlds)
------------------------------------------------------------------------------
A rule is ``list[list[str | tuple[str, int]]]``:

    [ ["A", "B"], ["C"] ]   means   (A AND B)  OR  (C)

    * outer list  = alternatives  (OR)
    * inner list  = one clause    (AND)
    * token       = an item / event-item name, a GATE macro, a runtime token,
                    or a ``(name, count)`` tuple for "hold N of an item"
    * "Free"      = the always-satisfiable sentinel

Each rule is SELF-CONTAINED: it embeds its act-access requirement via a GATE
macro, so the full from-scratch requirement is the rule itself. data.py's region
list is just grouping; every region is reachable for "Free" and the logic lives
on the locations.
"""
from __future__ import annotations

FREE = "Free"

# ---------------------------------------------------------------------------
# GATE MACROS — the act-access chain (cumulative; each references the prior gate
# plus the item the vanilla one-way transition uses). See data.EDGES and
# research/walkthrough_findings.md.
# ---------------------------------------------------------------------------
GATES: dict[str, list[list[str]]] = {
    # Act 1 -> Act 2a : Herman fixes the bridge once you bring the Saw.
    "open_bridge":     [["Saw"]],
    # Act 2a -> Act 2b : the Flute shatters the ice over the cave mouth.
    "enter_labyrinth": [["open_bridge", "Flute"]],
    # Act 2b -> Act 3 : turn into a Wisp to float across the chasm.
    "reach_act3":      [["enter_labyrinth", "Wisp Spell"]],
    # Act 3 -> Act 4a : drink the Orange potion to become a pegasus (one-way).
    "reach_grave":     [["reach_act3", "Orange potion"]],
    # Grave Island -> Castle : invisibility (Red) + the Iron Key open the gate.
    "enter_castle":    [["reach_grave", "Iron key", "Red Spell"]],
    # Castle -> Kyra-Gem chamber : two inner-door keys + the royal regalia.
    "enter_kyragem":   [["enter_castle", "Crown", "Sceptre", "Royal chalice", "Gold key", "Hidden key"]],
}

# Runtime tokens — substituted per-seed by rules.py, not expandable statically.
# `birthstone_set` -> the seed's 4 chosen birthstones (data.choose_birthstones).
DYNAMIC_TOKENS = ("birthstone_set",)

# ---------------------------------------------------------------------------
# LOCATION RULES — region -> location -> OR-of-ANDs. Names match data.py exactly.
# ---------------------------------------------------------------------------
location_rules: dict[str, dict[str, list[list]]] = {

    "Brandons Home": {
        "Brandon's Home - Kallak's Note":            [[FREE]],
        "Brandon's Home - Desk Drawer":              [[FREE]],
        "Brandon's Home - Garnet":                   [[FREE]],
        "Brandon's Home - Apple":                    [[FREE]],
    },

    "Emerald Forest": {
        "Willow - Teardrop Catch":                   [[FREE]],
        "Forest - Lavender Rose":                    [[FREE]],
        "Forest - Saw":                              [[FREE]],
        "Forest - Tulip":                            [[FREE]],
        "Forest - Amethyst Gem":                     [[FREE]],
        "Forest - Aquamarine Gem":                   [[FREE]],
        "Forest - Emerald Gem":                      [[FREE]],
        "Forest - Sapphire Gem":                     [[FREE]],
        "Forest - Ruby Gem":                         [[FREE]],
        "Forest - Opal Gem":                         [[FREE]],
        "Temple - Purple Rose":                      [[FREE]],
        "Brynn - Give Note & Rose (Silver Rose)":    [["Note", "Lavender rose"]],
        "Merith - Catch the Marble":                 [["Teardrop"]],
        "Temple Altar - Rose & Marble (Amulet)":     [["Silver rose", "Marble"]],
        "Herman - Repair Bridge (Saw turn-in)":      [["Saw"]],
    },

    "Over The Bridge": {
        "Darm's Wood - Acorn":                       [["open_bridge"]],
        "Darm's Wood - Walnut":                      [["open_bridge"]],
        "Darm's Wood - Pinecone":                    [["open_bridge"]],
        "Darm's Wood - Peridot Gem":                 [["open_bridge"]],
        "Darm's Wood - Diamond Gem":                 [["open_bridge"]],
        "Darm's Wood - Topaz Gem":                   [["open_bridge"]],
        "Darm's Wood - Onyx Gem":                    [["open_bridge"]],
        "Cardinal - Heal & Get Quill":               [["open_bridge", "Heal Spell"]],
        "Darm - Give Quill (Scroll of Winter)":      [["open_bridge", "Feather"]],
        "Marble Altar - Birthstone Puzzle (Flute)":  [["open_bridge", "birthstone_set"]],
        "Magic Well - Drop Coin (Moonstone)":        [["open_bridge", "Gold coin"]],
    },

    "Labyrinth": {
        "Labyrinth - Fireberries":                   [["enter_labyrinth"]],
        "Labyrinth - Loose Rock":                    [["enter_labyrinth", "Fireberries"]],
        "Labyrinth - Gold Coin":                     [["enter_labyrinth", "Fireberries"]],
        "Labyrinth - Lodestone Gem":                 [["enter_labyrinth", "Fireberries"]],
        "Labyrinth - Iron Key (Freeze the Lava)":    [["enter_labyrinth", "Fireberries", "Wisp Spell", "Magic scroll"]],
    },

    "Act3 Wilds": {
        "Zanthia - Crystal Ball (Scroll on Flame)":  [["reach_act3", "Magic scroll"]],
        "Zanthia - Magic Water":                     [["reach_act3"]],
        "Zanthia - Empty Flask":                     [["reach_act3"]],
        "Blueberry Field - Blueberries":             [["reach_act3"]],
        "Beach - Orchid":                            [["reach_act3"]],
        "Beach - Pearl Gem":                         [["reach_act3"]],
        "Secret Passage - Rainbowstone":             [["reach_act3"]],
        "Act3 - Sunstone Gem":                       [["reach_act3"]],
        "Zanthia - Brew Blue Potion":                [["reach_act3", "Blueberries", "Sapphire"]],
        "Zanthia - Brew Red Potion":                 [["reach_act3", "Orchid", "Ruby"]],
        "Zanthia - Brew Yellow Potion":              [["reach_act3", "Tulip", "Topaz"]],
        "Zanthia - Brew Orange Potion":              [["reach_act3", "Red potion", "Yellow potion"]],
        "Zanthia - Brew Purple Potion":              [["reach_act3", "Blue potion", "Red potion"]],
        "Zanthia - Brew Green Potion":               [["reach_act3", "Blue potion", "Yellow potion"]],
        "Faun - Give Apple (Royal Chalice)":         [["reach_act3", "Blue Spell", "Purple potion", "Apple"]],
    },

    "Grave Island": {
        "Grave Island - Fallen Star":                [["reach_grave"]],
        "Grave Island - Diamond Gem":                [["reach_grave"]],
    },

    "Castle": {
        "Castle Library - Book Puzzle (Crown)":      [["enter_castle"]],
        "Castle Kitchen - Poker (Sceptre)":          [["enter_castle"]],
        "Castle - Fireplace Key (Blue Spell)":       [["enter_castle", "Blue Spell"]],
        "Castle - Music Room Mallet (Heal Herman)":  [["enter_castle", "Heal Spell"]],
        "Castle - Bell Puzzle Key":                  [["enter_castle", "Heal Spell", "Mallet"]],
        "Castle - Mirror":                           [["enter_castle"]],
        "Castle - Aquamarine Gem":                   [["enter_castle"]],
    },
}

# ---------------------------------------------------------------------------
# EVENT RULES — region -> event location -> OR-of-ANDs. Grant the event item
# named in data.EVENT_LOCATIONS (the four amulet powers + Victory).
# ---------------------------------------------------------------------------
event_rules: dict[str, dict[str, list[list]]] = {
    "Over The Bridge": {
        "Deadwood Hole - Drop Nuts (Earn Heal Power)":       [["open_bridge", "Amulet", "Acorn", "Walnut", "Pinecone"]],
    },
    "Labyrinth": {
        "Wisp Pedestal - Place Moonstone (Earn Wisp Power)": [["enter_labyrinth", "Amulet", "Moonstone", "Fireberries"]],
    },
    "Act3 Wilds": {
        "Fountain - Drink Water (Earn Blue Power)":          [["reach_act3", "Amulet", "Crystal ball"]],
    },
    "Grave Island": {
        "Grave - Place Orchid (Earn Red Power)":             [["reach_grave", "Amulet", "Orchid"]],
    },
    "Kyragem Chamber": {
        # enter_kyragem already folds in the regalia + both keys; the final blow
        # needs invisibility (Red) + the chamber mirror (scenery, not an item).
        "Kyragem Chamber - Defeat Malcolm (Mirror)":         [["enter_kyragem", "Red Spell"]],
    },
}

# Completion: state.has("Victory"), granted by the Kyragem event above.
GOAL_EVENT = "Victory"
