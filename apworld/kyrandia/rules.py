from __future__ import annotations

from typing import Callable, Dict, List, TYPE_CHECKING

from .rulesdata import FREE, GATES, location_rules, event_rules, GOAL_EVENT

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from . import KyrandiaWorld


def _entrance_name(frm: str, to: str) -> str:
    return f"{frm} -> {to}"


# ---------------------------------------------------------------------------
# Gate expansion.  A rulesdata rule is OR-of-ANDs over items / event items /
# GATE macros / runtime tokens.  We expand it into a list of item-only
# alternatives (each a frozenset of item names); the access predicate is then
# "hold all items of ANY alternative".  GATE macros expand recursively (the
# act-access chain is linear and acyclic).  `dyn` maps per-seed runtime tokens
# (e.g. "birthstone_set") to their resolved alternatives.
# ---------------------------------------------------------------------------
Alt = Dict[str, int]  # one alternative: item name -> min count required


def _merge(a: Alt, b: Alt) -> Alt:
    # AND two requirement sets: items are persistent, so the need is the MAX
    # count across mentions (holding 2 flasks satisfies both "need 1" and "need 2").
    out = dict(a)
    for name, cnt in b.items():
        out[name] = max(out.get(name, 0), cnt)
    return out


def _expand_token(tok, dyn: Dict[str, List[Alt]]) -> List[Alt]:
    if tok == FREE:
        return [{}]
    if isinstance(tok, tuple):       # (name, count)
        name, cnt = tok
        return [{name: cnt}]
    if tok in dyn:
        return dyn[tok]
    if tok in GATES:
        return _expand_rule(GATES[tok], dyn)
    return [{tok: 1}]                # leaf: a real or event item, count 1


def _expand_clause(clause: List, dyn: Dict[str, List[Alt]]) -> List[Alt]:
    alts: List[Alt] = [{}]
    for tok in clause:
        subs = _expand_token(tok, dyn)
        alts = [_merge(a, s) for s in subs for a in alts]
    return alts


def _expand_rule(rule: List[List], dyn: Dict[str, List[Alt]]) -> List[Alt]:
    out: List[Alt] = []
    for clause in rule:
        out.extend(_expand_clause(clause, dyn))
    # Dedup identical alternatives (keep it simple; rules rarely have many ORs).
    seen, uniq = set(), []
    for a in out:
        key = tuple(sorted(a.items()))
        if key not in seen:
            seen.add(key)
            uniq.append(a)
    return uniq


def _predicate(rule: List[List], player: int,
               dyn: Dict[str, List[Alt]]) -> Callable[["CollectionState"], bool] | None:
    """Compile a rulesdata rule into a CollectionState predicate, or None when
    the rule is always satisfiable (a "Free" alternative)."""
    alts = _expand_rule(rule, dyn)
    if any(len(a) == 0 for a in alts):
        return None  # Free
    compiled = [tuple(a.items()) for a in alts]  # list of ((name, count), ...)
    if len(compiled) == 1:
        items = compiled[0]
        if len(items) == 1:
            name, cnt = items[0]
            return lambda state: state.has(name, player, cnt)
        return lambda state: all(state.has(n, player, c) for n, c in items)
    return lambda state: any(all(state.has(n, player, c) for n, c in alt) for alt in compiled)


def set_rules(world: "KyrandiaWorld") -> None:
    player = world.player
    mw = world.multiworld

    # Per-seed runtime token resolution: the birthstone altar requires the four
    # gems the world chose this seed (promoted to progression in create_items).
    dyn: Dict[str, List[Alt]] = {
        "birthstone_set": [{gem: 1 for gem in world.birthstone_gems}],
    }

    # Region edges are free groupings; ALL logic lives on the self-contained
    # location rules (their GATE tokens fold in act access), so we set no
    # entrance rules. rulesdata.py is the single source of truth for access.
    for locs in (location_rules.values()):
        for name, rule in locs.items():
            pred = _predicate(rule, player, dyn)
            if pred is not None:
                mw.get_location(name, player).access_rule = pred

    for locs in (event_rules.values()):
        for name, rule in locs.items():
            pred = _predicate(rule, player, dyn)
            if pred is not None:
                mw.get_location(name, player).access_rule = pred

    # Completion: hold the Victory event (locked on the Kyragem event location).
    mw.completion_condition[player] = lambda state: state.has(GOAL_EVENT, player)
