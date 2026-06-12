from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING

from .data import EDGES, LOCATIONS, EVENT_LOCATIONS

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from . import KyrandiaWorld


def _entrance_name(frm: str, to: str) -> str:
    return f"{frm} -> {to}"


def _rule_for(requires: List[str], player: int) -> Callable[["CollectionState"], bool] | None:
    """Return a CollectionState predicate requiring all named items, or None
    when there is no requirement (no rule needed)."""
    if not requires:
        return None
    names = tuple(requires)
    if len(names) == 1:
        name = names[0]
        return lambda state: state.has(name, player)
    return lambda state: state.has_all(names, player)


def set_rules(world: "KyrandiaWorld") -> None:
    player = world.player
    multiworld = world.multiworld

    # --- region edges ---
    for frm, to, requires in EDGES:
        rule = _rule_for(requires, player)
        if rule is None:
            continue
        entrance = multiworld.get_entrance(_entrance_name(frm, to), player)
        entrance.access_rule = rule

    # --- real location access rules ---
    for name, _region, _loc_id, requires in LOCATIONS:
        rule = _rule_for(requires, player)
        if rule is None:
            continue
        multiworld.get_location(name, player).access_rule = rule

    # --- event location access rules ---
    for name, _region, _grant, requires in EVENT_LOCATIONS:
        rule = _rule_for(requires, player)
        if rule is None:
            continue
        multiworld.get_location(name, player).access_rule = rule

    # --- completion: hold the Victory event (placed on the Kyragem event loc) ---
    multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
