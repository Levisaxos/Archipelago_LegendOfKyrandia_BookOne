"""Birthstone altar: the seed picks 4 required gems, the altar is gated on them,
and the gem set is reproducible. No Archipelago install needed (pure data/logic).
"""
import importlib.util
import random
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "apworld" / "kyrandia"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestBirthstones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = _load("kyradata", PKG / "data.py")
        cls.R = _load("kyrarules", PKG / "rulesdata.py")

    def test_birthstones_are_real_items(self):
        for gem in self.D.BIRTHSTONES:
            self.assertIn(gem, self.D.ITEM_TABLE, f"{gem} is not a defined item")
        self.assertEqual(len(self.D.BIRTHSTONES), len(set(self.D.BIRTHSTONES)),
                         "BIRTHSTONES has duplicates")
        self.assertGreaterEqual(len(self.D.BIRTHSTONES), self.D.BIRTHSTONE_SLOTS)

    def test_choice_is_distinct_subset_of_size_four(self):
        gems = self.D.choose_birthstones(random.Random(1234))
        self.assertEqual(len(gems), self.D.BIRTHSTONE_SLOTS)
        self.assertEqual(len(set(gems)), self.D.BIRTHSTONE_SLOTS, "gems not distinct")
        self.assertTrue(set(gems) <= set(self.D.BIRTHSTONES))

    def test_choice_is_reproducible_for_a_seed(self):
        a = self.D.choose_birthstones(random.Random(42))
        b = self.D.choose_birthstones(random.Random(42))
        self.assertEqual(a, b, "same seed must yield the same gems (UT determinism)")

    def test_altar_location_uses_the_dynamic_token(self):
        # data.py: the altar exists (Act 2, over the bridge) with empty static
        # requires (the gem gating is applied dynamically in rules.py).
        altar = "Marble Altar - Birthstone Puzzle (Flute)"
        data_locs = {name: req for (name, _r, _id, req) in self.D.LOCATIONS}
        self.assertIn(altar, data_locs, "altar location missing from data.py")
        self.assertEqual(data_locs[altar], [], "altar must have empty static requires")
        # rulesdata.py: the altar rule is the access gate + the birthstone_set token.
        self.assertEqual(
            self.R.location_rules["Over The Bridge"].get(altar),
            [["open_bridge", self.D.BIRTHSTONE_SET_TOKEN]],
            "altar rule must be [[open_bridge, birthstone_set]] in Over The Bridge",
        )
        self.assertIn(self.D.BIRTHSTONE_SET_TOKEN, self.R.DYNAMIC_TOKENS)

    def test_no_stale_over_bridge_flute(self):
        names = {name for (name, _r, _id, _q) in self.D.LOCATIONS}
        self.assertNotIn("Over Bridge - Flute", names,
                         "the old free flute pickup should be gone (now the altar)")


if __name__ == "__main__":
    unittest.main()
