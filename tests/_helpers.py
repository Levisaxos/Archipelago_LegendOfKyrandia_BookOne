"""Shared test helpers: load the apworld data, generate seeds, parse spoilers,
and run an INDEPENDENT logic sweep to prove a placement is beatable.

The sweep does not trust Archipelago's own playthrough — it re-derives
reachability from data.py (regions/edges/requires) against the spoiler's
item placements. That makes the beatability assertion a genuine check of our
logic model, not a tautology.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA_PY = REPO / "apworld" / "kyrandia" / "data.py"


# --------------------------------------------------------------------------- data
def load_data():
    spec = importlib.util.spec_from_file_location("kyradata", DATA_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------- AP discovery
def find_ap_root() -> Path | None:
    """Locate an Archipelago install (ArchipelagoGenerate.exe). Honors $AP_ROOT."""
    candidates = []
    env = os.environ.get("AP_ROOT")
    if env:
        candidates.append(Path(env))
    candidates += [
        Path(r"C:\Program Files\Archipelago"),
        Path(r"C:\Program Files (x86)\Archipelago"),
        Path(r"C:\Archipelago"),
    ]
    for c in candidates:
        if (c / "ArchipelagoGenerate.exe").exists():
            return c
    return None


def build_and_install_apworld(ap_root: Path) -> None:
    """Rebuild apworld/kyrandia.apworld from source and copy into custom_worlds
    so generation tests exercise the CURRENT source. Raises on failure."""
    import shutil
    import sys

    sys.path.insert(0, str(REPO / "pyscripts"))
    try:
        import build_apworld  # noqa: WPS433 (local import by design)

        out = build_apworld.build()
    finally:
        sys.path.pop(0)
    dst = ap_root / "custom_worlds" / "kyrandia.apworld"
    shutil.copyfile(out, dst)


# ------------------------------------------------------------------- generation
def generate_seed(ap_root: Path, players_dir: Path, out_dir: Path, seed: int,
                  timeout: int = 180) -> str:
    """Run ArchipelagoGenerate and return the spoiler text.

    stdin is DEVNULL so the frozen exe's "Press enter to close" error prompt
    can never hang the test; stdout/stderr are captured.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    exe = ap_root / "ArchipelagoGenerate.exe"
    proc = subprocess.run(
        [str(exe),
         "--player_files_path", str(players_dir),
         "--outputpath", str(out_dir),
         "--seed", str(seed)],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"generation failed (exit {proc.returncode}).\n"
            f"--- stderr ---\n{proc.stderr[-2000:]}\n"
            f"--- stdout tail ---\n{proc.stdout[-1000:]}"
        )
    zips = sorted(out_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        raise RuntimeError(f"no output archive produced. stdout tail:\n{proc.stdout[-1000:]}")
    with zipfile.ZipFile(zips[-1]) as z:
        spoiler_name = next(n for n in z.namelist() if n.endswith("_Spoiler.txt"))
        return z.read(spoiler_name).decode("utf-8")


def write_yaml(players_dir: Path, name: str, *, goal: str = "defeat_malcolm",
               start_with_amulet: bool = False) -> None:
    players_dir.mkdir(parents=True, exist_ok=True)
    (players_dir / f"{name}.yaml").write_text(
        "name: %s\n"
        "description: Kyrandia beatability test\n"
        "game: The Legend of Kyrandia - Book 1\n"
        "requires:\n"
        "  version: 0.6.4\n"
        "The Legend of Kyrandia - Book 1:\n"
        "  goal: %s\n"
        "  start_with_amulet: %s\n"
        "  death_link: false\n"
        % (name, goal, "true" if start_with_amulet else "false"),
        encoding="utf-8",
    )


# ---------------------------------------------------------------- spoiler parsing
def parse_placements(spoiler: str, known_locations: set[str]) -> dict[str, str]:
    """Parse the spoiler 'Locations:' block into {location_name: item_name}.

    Single-world spoilers carry no '(Player)' tag. We only keep lines whose key
    is a known real location, so option/header 'Key: Value' lines are ignored.
    """
    placements: dict[str, str] = {}
    in_locations = False
    for line in spoiler.splitlines():
        if line.strip() == "Locations:":
            in_locations = True
            continue
        if in_locations and line.strip() == "Playthrough:":
            break
        if not in_locations or ": " not in line:
            continue
        loc, item = line.strip().split(": ", 1)
        if loc in known_locations:
            placements[loc] = item
    return placements


def parse_start_inventory(spoiler: str) -> set[str]:
    """Precollected items (e.g. start_with_amulet). Listed after the options
    block as bare 'Item Name' lines under no header; we instead read them from
    the 'Start Inventory:' line if present (comma list)."""
    items: set[str] = set()
    for line in spoiler.splitlines():
        if line.startswith("Start Inventory:"):
            rest = line.split(":", 1)[1].strip()
            if rest:
                items.update(p.strip() for p in rest.split(",") if p.strip())
            break
    return items


# -------------------------------------------------------------- the logic sweep
def sweep_beatable(D, placements: dict[str, str], precollected=()):
    """Independent maximal-sweep reachability over data.py.

    Returns (beatable, reachable_real_locations, collected_items). A seed is
    beatable iff the 'Victory' event item is collectable: starting from the
    precollected set, repeatedly collect every reachable+satisfied location's
    item (and every reachable+satisfied event location's granted event item)
    until fixpoint, recomputing region reachability each round.
    """
    items: set[str] = set(precollected)
    edges: dict[str, list[tuple[str, list[str]]]] = {}
    for frm, to, req in D.EDGES:
        edges.setdefault(frm, []).append((to, req))

    def reachable_regions() -> set[str]:
        reached = {D.MENU}
        changed = True
        while changed:
            changed = False
            for frm in list(reached):
                for to, req in edges.get(frm, []):
                    if to not in reached and all(x in items for x in req):
                        reached.add(to)
                        changed = True
        return reached

    real = [(name, region, req) for (name, region, _id, req) in D.LOCATIONS]
    events = [(name, region, grant, req) for (name, region, grant, req) in D.EVENT_LOCATIONS]

    changed = True
    while changed:
        changed = False
        rr = reachable_regions()
        for name, region, req in real:
            if region in rr and all(x in items for x in req):
                it = placements.get(name)
                if it and it not in items:
                    items.add(it)
                    changed = True
        for name, region, grant, req in events:
            if region in rr and all(x in items for x in req):
                if grant not in items:
                    items.add(grant)
                    changed = True

    rr = reachable_regions()
    reachable_real = {
        name for (name, region, req) in real
        if region in rr and all(x in items for x in req)
    }
    return ("Victory" in items), reachable_real, items
