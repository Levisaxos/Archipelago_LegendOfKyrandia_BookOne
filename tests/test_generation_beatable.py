"""End-to-end beatability tests.

Generate real seeds with ArchipelagoGenerate, then prove each is winnable by an
INDEPENDENT logic sweep over data.py against the spoiler's item placements.
Skipped automatically if no Archipelago install is found (set $AP_ROOT to point
at one).
"""
import tempfile
import unittest
from pathlib import Path

from _helpers import (
    build_and_install_apworld,
    find_ap_root,
    generate_seed,
    load_data,
    parse_placements,
    parse_start_inventory,
    sweep_beatable,
    write_yaml,
)

SEEDS = [1, 7, 42, 999, 31337]


class TestGenerationBeatable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ap_root = find_ap_root()
        if cls.ap_root is None:
            raise unittest.SkipTest("No Archipelago install found (set $AP_ROOT).")
        try:
            build_and_install_apworld(cls.ap_root)
        except PermissionError as exc:
            raise unittest.SkipTest(f"Cannot install apworld into custom_worlds: {exc}")
        cls.D = load_data()
        cls.known_locs = {name for (name, _r, _id, _q) in cls.D.LOCATIONS}
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.players = cls.tmp / "players"
        write_yaml(cls.players, "KyraTest")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "_tmp"):
            cls._tmp.cleanup()

    def _generate(self, seed: int) -> dict[str, str]:
        out = self.tmp / f"out_{seed}"
        spoiler = generate_seed(self.ap_root, self.players, out, seed)
        return spoiler

    def test_seeds_are_beatable(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                spoiler = self._generate(seed)
                placements = parse_placements(spoiler, self.known_locs)

                # Every networked location must be placed (full fill).
                self.assertEqual(
                    len(placements), len(self.D.LOCATIONS),
                    f"seed {seed}: parsed {len(placements)} placements, "
                    f"expected {len(self.D.LOCATIONS)}",
                )

                precollected = parse_start_inventory(spoiler)
                beatable, reachable, collected = sweep_beatable(
                    self.D, placements, precollected
                )

                # Independent proof the goal is collectable.
                self.assertTrue(
                    beatable,
                    f"seed {seed}: Victory NOT reachable by independent sweep. "
                    f"Collected {len(collected)} items, "
                    f"reached {len(reachable)}/{len(self.D.LOCATIONS)} locations.",
                )

                # Full accessibility: every location reachable at fixpoint.
                unreached = self.known_locs - reachable
                self.assertEqual(
                    unreached, set(),
                    f"seed {seed}: {len(unreached)} locations unreachable: "
                    f"{sorted(unreached)[:5]}...",
                )

                # Sanity: AP's own playthrough also ends in the goal event.
                self.assertIn(
                    "Defeat Malcolm (Mirror): Victory", spoiler,
                    f"seed {seed}: AP playthrough did not record the Victory event",
                )


if __name__ == "__main__":
    unittest.main()
