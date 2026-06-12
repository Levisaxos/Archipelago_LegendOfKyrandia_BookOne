from __future__ import annotations

from BaseClasses import Item, ItemClassification

from .data import ITEM_TABLE, PROGRESSION, USEFUL

GAME = "The Legend of Kyrandia - Book 1"

_CLASSIFICATION = {
    PROGRESSION: ItemClassification.progression,
    USEFUL: ItemClassification.useful,
    "filler": ItemClassification.filler,
}


class KyrandiaItem(Item):
    game = GAME


def classification_for(name: str) -> ItemClassification:
    return _CLASSIFICATION[ITEM_TABLE[name][1]]


# name -> AP id (networked items only; event items are id-None and excluded)
item_name_to_id: dict[str, int] = {name: data[0] for name, data in ITEM_TABLE.items()}
