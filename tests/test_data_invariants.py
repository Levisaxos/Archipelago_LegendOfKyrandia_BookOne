"""Static invariants of the apworld data — no Archipelago install needed."""
import unittest

from _helpers import load_data


class TestDataInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = load_data()

    def test_unique_item_ids(self):
        ids = [v[0] for v in self.D.ITEM_TABLE.values()]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        self.assertEqual(dupes, [], f"duplicate item ids: {dupes}")

    def test_unique_location_ids(self):
        ids = [loc_id for (_n, _r, loc_id, _q) in self.D.LOCATIONS]
        self.assertEqual(len(ids), len(set(ids)), "duplicate location ids")

    def test_regions_valid(self):
        regions = {self.D.MENU, *self.D.REGIONS}
        for frm, to, _ in self.D.EDGES:
            self.assertIn(frm, regions)
            self.assertIn(to, regions)
        for name, region, _id, _q in self.D.LOCATIONS:
            self.assertIn(region, regions, f"{name} in unknown region {region}")
        for name, region, _g, _q in self.D.EVENT_LOCATIONS:
            self.assertIn(region, regions, f"{name} in unknown region {region}")

    def test_required_items_are_progression_or_event(self):
        """Reachability invariant: only progression/event items advance the
        sweep, so any item named in a rule must be one of those."""
        D = self.D
        prog = {n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.PROGRESSION}
        events = set(D.EVENT_ITEMS)
        allowed = prog | events
        known = set(D.ITEM_TABLE) | events

        def check(req, where):
            for it in req:
                self.assertIn(it, known, f"{where}: requires unknown item '{it}'")
                self.assertIn(it, allowed,
                              f"{where}: requires non-progression item '{it}'")

        for frm, to, req in D.EDGES:
            check(req, f"edge {frm}->{to}")
        for name, _r, _id, req in D.LOCATIONS:
            check(req, f"loc {name}")
        for name, _r, grant, req in D.EVENT_LOCATIONS:
            check(req, f"event {name}")
            self.assertIn(grant, events, f"event {name} grants non-event {grant}")

    def test_pool_balances_to_location_count(self):
        D = self.D
        prog = [n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.PROGRESSION]
        useful = [n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.USEFUL]
        base = len(prog) + len(useful)
        self.assertLessEqual(base, len(D.LOCATIONS),
                             "fixed items exceed location count (pool can't balance)")

    def test_all_regions_reachable_with_full_item_set(self):
        """With every progression+event item, the graph must connect Menu to
        all regions — otherwise some region is permanently dead."""
        D = self.D
        prog = {n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.PROGRESSION}
        have = prog | set(D.EVENT_ITEMS)
        edges = {}
        for frm, to, req in D.EDGES:
            edges.setdefault(frm, []).append((to, req))
        reached, changed = {D.MENU}, True
        while changed:
            changed = False
            for frm in list(reached):
                for to, req in edges.get(frm, []):
                    if to not in reached and all(x in have for x in req):
                        reached.add(to)
                        changed = True
        missing = ({D.MENU, *D.REGIONS}) - reached
        self.assertEqual(missing, set(), f"unreachable regions: {missing}")


if __name__ == "__main__":
    unittest.main()
