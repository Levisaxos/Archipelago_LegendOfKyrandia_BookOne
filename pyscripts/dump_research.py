"""Generate research/locations.json from the apworld's data.py.

data.py is the single source of truth; this keeps the research deliverable in
sync. Run from anywhere; paths resolve relative to the repo root.
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA_PY = os.path.join(REPO, "apworld", "kyrandia", "data.py")
OUT = os.path.join(REPO, "research", "locations.json")


def _load_data():
    spec = importlib.util.spec_from_file_location("kyradata", DATA_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(D) -> dict:
    prog = [n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.PROGRESSION]
    useful = [n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.USEFUL]
    filler = [n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.FILLER]
    return {
        "_meta": {
            "game": "The Legend of Kyrandia - Book 1",
            "generated_from": "apworld/kyrandia/data.py (do not edit by hand; run pyscripts/dump_research.py)",
            "status": "DRAFT v2 (2026-06-11). First-pass location/region/logic from the plan doc + walkthrough knowledge; NOT verified against a live playthrough. The authoritative list will come from Phase 1 read-only instrumentation (logging every (sceneId, slot) pickup + flag-set).",
            "logic_model": "Model A (vanilla item gates): region edges and turn-in/puzzle locations are gated on the real game items vanilla uses at that transition. V1 scope = item randomizer.",
            "goal": "Defeat Malcolm (turn to stone): recover Crown+Sceptre+Royal chalice, obtain the Mirror and the Red amulet power, then confront Malcolm.",
            "naming": "Each location name embeds its vanilla item / action (e.g. 'Forest - Saw', 'Brynn - Give Note & Rose (Silver Rose)').",
            "event_items": "Heal/Wisp/Red/Blue Spells and Victory are id-None EVENT items placed locked on event locations (earned capabilities / goal), not networked pool items.",
            "counts": {
                "regions": len(D.REGIONS) + 1,
                "real_locations": len(D.LOCATIONS),
                "event_locations": len(D.EVENT_LOCATIONS),
                "progression_items": len(prog),
                "useful_items": len(useful),
                "filler_item_types": len(filler),
            },
            "open_todos": [
                "Verify every region/edge/requirement against a real playthrough.",
                "Confirm the lavender-rose-at-grave double-use (one rose or two?). Engine must not consume logic-critical items.",
                "Pegasus -> Grave Island is free (no engine pickup). Catacombs is a free side-region; Blue power gates only the hidden key.",
                "Forced inventory wipes (labyrinth entry, castle foyer) assumed neutralized by the engine fork.",
                "No early-region check is gated on a late-region item (avoids vanilla one-way backtracking)."
            ],
        },
        "regions": [D.MENU] + list(D.REGIONS),
        "edges": [
            {"from": f, "to": t, "requires": req}
            for (f, t, req) in D.EDGES
        ],
        "locations": [
            {"id": loc_id, "name": name, "region": region, "requires": req}
            for (name, region, loc_id, req) in D.LOCATIONS
        ],
        "event_locations": [
            {"name": name, "region": region, "grants": grant, "requires": req}
            for (name, region, grant, req) in D.EVENT_LOCATIONS
        ],
        "item_pool": {
            "progression": sorted(prog),
            "useful": sorted(useful),
            "filler": sorted(filler),
        },
    }


if __name__ == "__main__":
    D = _load_data()
    data = build(D)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    c = data["_meta"]["counts"]
    print(f"wrote {OUT}")
    print(f"  regions={c['regions']} real_locations={c['real_locations']} "
          f"event_locations={c['event_locations']} progression={c['progression_items']} "
          f"useful={c['useful_items']} filler_types={c['filler_item_types']}")
