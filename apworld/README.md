# apworld/

The Archipelago world ("apworld") for Legend of Kyrandia — Book 1 (roadmap Phase 2).
Pure Python; needs no C++ build. Generates valid AP seeds today (the forked game
client that connects to a server is a later phase).

## Layout
- `kyrandia/` — the world package (source).
  - `data.py` — **single source of truth**: items, locations, regions, edges.
    Mirrors `research/locations.json` + `research/logic.md`.
  - `items.py`, `locations.py` — `Item`/`Location` subclasses + name→id tables.
  - `options.py` — YAML options (goal, start_with_amulet, death_link).
  - `rules.py` — access-rule closures + completion condition.
  - `__init__.py` — the `World` class; create_regions/items, slot_data, **UT support**.
  - `archipelago.json` — apworld manifest.
  - `docs/` — player-facing setup + game docs.
- `kyrandia.apworld` — the built (zipped) world. Rebuild with
  `python pyscripts/build_apworld.py`.

## Test / use
1. `python pyscripts/build_apworld.py` → produces `apworld/kyrandia.apworld`.
2. Copy it into Archipelago's `custom_worlds/` (this machine:
   `C:\Program Files\Archipelago\custom_worlds\`).
3. Generate a seed (see `build/gen_test/players/*.yaml` for example YAMLs):
   `ArchipelagoGenerate.exe --player_files_path <dir> --outputpath <dir>`.

## Status / scope
**DRAFT v1, item-randomizer scope.** Logic is a first pass derived from the plan
doc + walkthrough knowledge — see `research/` for confidence tags and TODOs.
Verified to generate valid single- and multi-world seeds (38 checks, goal
reachable) against Archipelago 0.6.6. Universal Tracker is supported via
`interpret_slot_data` + `re_gen_passthrough`.
