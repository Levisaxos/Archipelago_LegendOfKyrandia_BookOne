from __future__ import annotations

from typing import Any, Dict, List

from BaseClasses import Item, ItemClassification, Region, Tutorial

from worlds.AutoWorld import WebWorld, World

from . import data as D
from .items import KyrandiaItem, item_name_to_id, classification_for
from .locations import KyrandiaLocation, location_name_to_id
from .options import KyrandiaOptions, LOGIC_OPTION_KEYS
from .rules import set_rules, _entrance_name

GAME = "The Legend of Kyrandia - Book 1"


class KyrandiaWeb(WebWorld):
    theme = "dirt"
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up the Legend of Kyrandia Book 1 randomizer.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Project contributors"],
        )
    ]


class KyrandiaWorld(World):
    """The Legend of Kyrandia - Book 1: a point-and-click adventure. This world
    shuffles the identity of every pickup, turn-in and puzzle reward into an
    Archipelago multiworld. DRAFT v1 logic — item randomizer scope."""

    game = GAME
    web = KyrandiaWeb()
    options_dataclass = KyrandiaOptions
    options: KyrandiaOptions
    topology_present = True

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    # The seed's four required birthstone gems (slot order). Set in generate_early.
    birthstone_gems: List[str]

    # ------------------------------------------------------------------ items
    def create_item(self, name: str) -> KyrandiaItem:
        cls = classification_for(name)
        # The seed's chosen birthstones gate the altar, so they must advance logic.
        if name in getattr(self, "birthstone_gems", ()):
            cls = ItemClassification.progression
        return KyrandiaItem(name, cls, D.ITEM_NAME_TO_ID[name], self.player)

    def create_event_item(self, name: str) -> KyrandiaItem:
        return KyrandiaItem(name, ItemClassification.progression, None, self.player)

    def get_filler_item_name(self) -> str:
        return D.FILLER_NAME

    # ------------------------------------------------------------- generation
    def generate_early(self) -> None:
        # Universal Tracker re-gen passthrough: when UT triggers a fresh
        # generation, the slot_data dict lands under multiworld.re_gen_passthrough.
        # Restore resolved option values so UT logic matches the server world.
        re_gen = getattr(self.multiworld, "re_gen_passthrough", {})
        passthrough = re_gen.get(self.game) if isinstance(re_gen, dict) else None
        if passthrough:
            for key in LOGIC_OPTION_KEYS:
                if key in passthrough:
                    opt = getattr(self.options, key, None)
                    if opt is not None:
                        opt.value = passthrough[key]

        # Birthstone altar: pick the seed's 4 required gems. On a UT re-gen,
        # restore the exact set from slot_data so tracker logic matches; otherwise
        # roll them from the world's seeded RNG (reproducible for a given seed).
        restored = passthrough.get("birthstone_gems") if passthrough else None
        if restored:
            self.birthstone_gems = list(restored)
        else:
            self.birthstone_gems = D.choose_birthstones(self.random)

    def create_regions(self) -> None:
        player = self.player
        mw = self.multiworld

        # Build Menu + all regions.
        regions: Dict[str, Region] = {}
        menu = Region(D.MENU, player, mw)
        regions[D.MENU] = menu
        mw.regions.append(menu)
        for name in D.REGIONS:
            region = Region(name, player, mw)
            regions[name] = region
            mw.regions.append(region)

        # Real locations.
        for name, region_name, loc_id, _requires in D.LOCATIONS:
            region = regions[region_name]
            loc = KyrandiaLocation(player, name, loc_id, region)
            region.locations.append(loc)

        # Event locations (locked event items, id None).
        for name, region_name, grant, _requires in D.EVENT_LOCATIONS:
            region = regions[region_name]
            loc = KyrandiaLocation(player, name, None, region)
            loc.place_locked_item(self.create_event_item(grant))
            region.locations.append(loc)

        # Edges (rules attached later in set_rules).
        for frm, to, _requires in D.EDGES:
            regions[frm].connect(regions[to], _entrance_name(frm, to))

    def create_items(self) -> None:
        pool: List[Item] = []

        precollect_amulet = bool(self.options.start_with_amulet.value)
        if precollect_amulet:
            self.multiworld.push_precollected(self.create_item("Amulet"))

        for name, (_ap_id, cls) in D.ITEM_TABLE.items():
            if cls == D.FILLER:
                continue  # all filler is added as padding below (FILLER_POOL)
            if name == "Amulet" and precollect_amulet:
                continue  # already precollected
            pool.append(self.create_item(name))

        # Pad with filler (cycled for variety) so the pool exactly fills the
        # real (non-event) locations.
        target = len(D.LOCATIONS)
        if len(pool) > target:
            raise Exception(
                f"{self.player_name}: Kyrandia defined item pool ({len(pool)}) "
                f"exceeds location count ({target})."
            )
        i = 0
        while len(pool) < target:
            pool.append(self.create_item(D.FILLER_POOL[i % len(D.FILLER_POOL)]))
            i += 1

        self.multiworld.itempool += pool

    def set_rules(self) -> None:
        set_rules(self)

    # ------------------------------------------------------------ slot / UT
    @staticmethod
    def interpret_slot_data(slot_data: dict) -> dict:
        """Universal Tracker hook. Returning the slot_data dict tells UT to
        re-run generation with it accessible via multiworld.re_gen_passthrough,
        so the tracker's logic matches the server world without re-rolling."""
        return slot_data

    def fill_slot_data(self) -> Dict[str, Any]:
        return {
            "goal": self.options.goal.value,
            "start_with_amulet": int(self.options.start_with_amulet.value),
            "death_link": bool(self.options.death_link.value),
            # Birthstone altar: the seed's required gems in slot order (1-4). The
            # engine fork sets `_birthstoneGemTable` from this (suppressing native
            # RNG) and NPCs reveal it per birthstone_hints.
            "birthstone_gems": list(self.birthstone_gems),
            "birthstone_hints": self.options.birthstone_hints.value,
            # Crosswalk hint for the (future) ScummVM client: AP item id -> engine id.
            # The client translates received AP items into engine item grants.
            "logic_version": 1,
        }
