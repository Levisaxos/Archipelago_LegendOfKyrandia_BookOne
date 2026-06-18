"""Consistency: rulesdata.py (the access-rule source consumed by rules.py) must
expand 1:1 to data.py (the regions/edges/requires source used by the independent
beatability sweep). If the two ever diverge, generation logic and the test sweep
would silently validate different worlds. No Archipelago install needed.
"""
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "apworld" / "kyrandia"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestRulesdataConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = _load("kyradata", PKG / "data.py")
        cls.R = _load("kyrarules", PKG / "rulesdata.py")

    # --- expand a rulesdata rule (OR-of-ANDs over gates/items) to item-only alts ---
    def _expand_token(self, tok):
        if tok == self.R.FREE:
            return [frozenset()]
        if tok in self.R.DYNAMIC_TOKENS:
            # Per-seed runtime tokens (e.g. birthstone_set) carry no static items;
            # data.py keeps their location's requires empty (gating is applied in
            # rules.py), so treat them as Free for the structural comparison.
            return [frozenset()]
        if tok in self.R.GATES:
            return self._expand_rule(self.R.GATES[tok])
        return [frozenset((tok,))]

    def _expand_clause(self, clause):
        alts = [frozenset()]
        for tok in clause:
            alts = [a | s for s in self._expand_token(tok) for a in alts]
        return alts

    def _expand_rule(self, rule):
        out = []
        for clause in rule:
            out.extend(self._expand_clause(clause))
        return out

    # --- data.py expected: items to reach a region (linear edge chain) + extras ---
    def _region_items(self, region):
        parent = {to: (frm, set(req)) for (frm, to, req) in self.D.EDGES}
        items, cur = set(), region
        while cur in parent:
            frm, req = parent[cur]
            items |= req
            cur = frm
        return items

    def _all_rules(self):
        rules = {}
        for reg, d in self.R.location_rules.items():
            rules.setdefault(reg, {}).update(d)
        for reg, d in self.R.event_rules.items():
            rules.setdefault(reg, {}).update(d)
        return rules

    def _data_locations(self):
        locs = {name: (reg, set(req)) for (name, reg, _id, req) in self.D.LOCATIONS}
        for (name, reg, _grant, req) in self.D.EVENT_LOCATIONS:
            locs[name] = (reg, set(req))
        return locs

    def test_every_data_location_has_matching_rule(self):
        rules = self._all_rules()
        for name, (region, req) in self._data_locations().items():
            rule = rules.get(region, {}).get(name)
            self.assertIsNotNone(rule, f"rulesdata missing rule for [{region}] {name}")
            expected = self._region_items(region) | set(req)
            alts = self._expand_rule(rule)
            self.assertTrue(
                any(a == expected for a in alts),
                f"[{region}] {name}: rule expands to {[sorted(a) for a in alts]}, "
                f"expected {sorted(expected)}",
            )

    def test_no_rule_without_a_data_location(self):
        data_names = set(self._data_locations())
        for region, d in self._all_rules().items():
            for name in d:
                self.assertIn(
                    name, data_names,
                    f"rulesdata has rule for unknown location [{region}] {name}",
                )

    def test_gate_chain_is_acyclic(self):
        # Expanding every gate must terminate (no cycles) and yield only items.
        for gate in self.R.GATES:
            alts = self._expand_rule([[gate]])  # raises RecursionError on a cycle
            self.assertTrue(alts, f"gate {gate} expands to nothing")

    def test_goal_event_exists(self):
        grants = {grant for (_n, _r, grant, _q) in self.D.EVENT_LOCATIONS}
        self.assertIn(self.R.GOAL_EVENT, grants,
                      f"GOAL_EVENT {self.R.GOAL_EVENT!r} is not granted by any event")


if __name__ == "__main__":
    unittest.main()
