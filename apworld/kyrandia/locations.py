from __future__ import annotations

from BaseClasses import Location

from .data import LOCATIONS

GAME = "The Legend of Kyrandia - Book 1"


class KyrandiaLocation(Location):
    game = GAME


# name -> AP id (real networked locations only; event locations are id-None)
location_name_to_id: dict[str, int] = {
    name: loc_id for (name, _region, loc_id, _req) in LOCATIONS
}
