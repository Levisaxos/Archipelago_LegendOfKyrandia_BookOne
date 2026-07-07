"""Add logic-gated AP check tabs to the PopTracker pack from the apworld's rulesdata.

The apworld keeps all access logic in apworld/kyrandia/rulesdata.py as OR-of-ANDs rules
with recursive GATE macros (open_bridge -> Saw, enter_labyrinth -> +Flute, ...) and a
per-seed `birthstone_set` token. PopTracker access rules are natively OR-of-ANDs, so we
expand each rule (exactly like rules.py) and emit it as `access_rules`.

Per region we render a check-list image (one row per check) and add it as a map tab; the
location dots colour green when in logic. Spell event-items map onto the amulet pips
(amulet_heal/wisp/red/blue); the birthstone token maps onto a manual `birthstones` toggle.

Non-destructive: APPENDS check maps/locations/tabs to the existing pack and refreshes the
autotracking LOCATION_MAPPING. Re-runnable (removes its own prior output first).
RUN ORDER: after build_scene_grid.py + build_amulet_sprites.py (it appends to their files).

Usage:  python pyscripts/build_check_logic.py
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APW = os.path.join(ROOT, "apworld", "kyrandia")
PACK = os.path.join(ROOT, "poptracker", "legend_of_kyrandia")
MAPS_DIR = os.path.join(PACK, "assets", "maps")

SPELL_CODE = {"Heal Spell": "amulet_heal", "Wisp Spell": "amulet_wisp",
              "Red Spell": "amulet_red", "Blue Spell": "amulet_blue"}
BIRTHSTONE_CODE = "birthstones"

ROW_H, IMG_W, DOT_X = 26, 380, 14


# ---------------------------------------------------------------- rule expansion
def load_rulesdata():
    spec = importlib.util.spec_from_file_location("rd", os.path.join(APW, "rulesdata.py"))
    rd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rd)
    return rd


def make_expander(rd):
    FREE, GATES = rd.FREE, rd.GATES
    dyn = {"birthstone_set": [{BIRTHSTONE_CODE: 1}]}

    def merge(a, b):
        o = dict(a)
        for n, c in b.items():
            o[n] = max(o.get(n, 0), c)
        return o

    def tok(t):
        if t == FREE:
            return [{}]
        if isinstance(t, tuple):
            return [{t[0]: t[1]}]
        if t in dyn:
            return dyn[t]
        if t in GATES:
            return rule(GATES[t])
        return [{t: 1}]

    def clause(cl):
        alts = [{}]
        for t in cl:
            subs = tok(t)
            alts = [merge(a, s) for s in subs for a in alts]
        return alts

    def rule(r):
        out = []
        for cl in r:
            out += clause(cl)
        seen, uniq = set(), []
        for a in out:
            k = tuple(sorted(a.items()))
            if k not in seen:
                seen.add(k)
                uniq.append(a)
        return uniq

    return rule


def access_rules_for(expanded, name2code):
    """OR-of-ANDs item dicts -> PopTracker access_rules list, or None when Free."""
    if any(len(a) == 0 for a in expanded):
        return None  # always reachable
    clauses = []
    for alt in expanded:
        codes = sorted(name2code[n] for n in alt)  # count>1 not representable on toggles
        clauses.append(",".join(codes))
    return clauses


# ---------------------------------------------------------------- pack data
def data_py_locations():
    """AST-parse data.py LOCATIONS -> name -> (region, ap_id)."""
    tree = ast.parse(open(os.path.join(APW, "data.py"), encoding="utf-8").read())
    for node in tree.body:
        tgt = node.target if isinstance(node, ast.AnnAssign) else \
            (node.targets[0] if isinstance(node, ast.Assign) else None)
        if isinstance(tgt, ast.Name) and tgt.id == "LOCATIONS":
            out = {}
            for name, region, ap_id, _req in ast.literal_eval(node.value):
                out[name] = (region, ap_id)
            return out
    raise RuntimeError("LOCATIONS not found in data.py")


def name_to_code():
    items = json.load(open(os.path.join(PACK, "items", "items.json"), encoding="utf-8"))
    m = {it["name"]: it["codes"] for it in items}
    m.update(SPELL_CODE)
    m[BIRTHSTONE_CODE] = BIRTHSTONE_CODE
    return m


def _font(sz):
    for p in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def render_checklist(slug, checks):
    """checks: list of (name, in_logic_default_unused). Draw one row per check."""
    h = len(checks) * ROW_H + 8
    img = Image.new("RGB", (IMG_W, h), (24, 24, 30))
    d = ImageDraw.Draw(img)
    font = _font(13)
    for i, name in enumerate(checks):
        y = 4 + i * ROW_H
        if i % 2:
            d.rectangle([0, y, IMG_W, y + ROW_H - 1], fill=(30, 30, 38))
        d.text((32, y + 6), name, fill=(218, 222, 230), font=font)
    img.save(os.path.join(MAPS_DIR, f"checks_{slug}.png"))
    return h


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def main():
    rd = load_rulesdata()
    expand = make_expander(rd)
    n2c = name_to_code()
    loc_meta = data_py_locations()

    maps_path = os.path.join(PACK, "maps", "maps.json")
    locs_path = os.path.join(PACK, "locations", "locations.json")
    trk_path = os.path.join(PACK, "layouts", "tracker.json")
    items_path = os.path.join(PACK, "items", "items.json")
    data_lua = os.path.join(PACK, "scripts", "data.lua")

    maps = json.load(open(maps_path, encoding="utf-8"))
    locs = json.load(open(locs_path, encoding="utf-8"))
    tracker = json.load(open(trk_path, encoding="utf-8"))
    items = json.load(open(items_path, encoding="utf-8"))

    regions = list(rd.location_rules.keys())  # display order = rulesdata order
    for r in rd.event_rules:                  # include event-only regions (e.g. the goal)
        if r not in regions:
            regions.append(r)
    region_set = set(regions)

    # idempotent: drop any prior check output
    maps = [m for m in maps if not m["name"].startswith("checks_")]
    locs = [g for g in locs if g["name"] not in region_set]

    location_mapping = {}  # ap_id -> "@Region/Check"
    new_maps, new_groups, new_tabs = [], [], []

    for region in regions:
        rules = {**rd.location_rules.get(region, {}), **rd.event_rules.get(region, {})}
        if not rules:
            continue
        names = list(rules)
        slug = slugify(region)
        render_checklist(slug, names)
        new_maps.append({
            "name": f"checks_{slug}", "img": f"assets/maps/checks_{slug}.png",
            "location_size": 18, "location_border_thickness": 2, "location_shape": "diamond",
        })
        children = []
        for i, name in enumerate(names):
            y = 4 + i * ROW_H + ROW_H // 2
            section = {"name": name}
            rules_list = access_rules_for(expand(rules[name]), n2c)
            if rules_list is not None:
                section["access_rules"] = rules_list
            children.append({
                "name": name,
                "map_locations": [{"map": f"checks_{slug}", "x": DOT_X, "y": y}],
                "sections": [section],
            })
            if name in loc_meta:
                location_mapping[loc_meta[name][1]] = f"@{region}/{name}"
        new_groups.append({"name": region, "children": children})
        new_tabs.append({"title": region, "content": {"type": "map", "maps": [f"checks_{slug}"]}})

    maps.extend(new_maps)
    locs.extend(new_groups)

    # append check tabs to the (single) tabbed widget, dropping prior check tabs
    def patch_tabs(o):
        if isinstance(o, dict):
            if o.get("type") == "tabbed":
                o["tabs"] = [t for t in o["tabs"]
                             if not (t.get("content", {}).get("maps", [""])[0].startswith("checks_"))]
                o["tabs"].extend(new_tabs)
                return True
            return any(patch_tabs(v) for v in o.values())
        if isinstance(o, list):
            return any(patch_tabs(v) for v in o)
        return False
    patch_tabs(tracker)

    # birthstones manual toggle item
    if not any(it["codes"] == BIRTHSTONE_CODE for it in items):
        items.append({
            "name": "Birthstones placed", "type": "toggle",
            "img": "assets/item_on.png", "disabled_img": "assets/item_off.png",
            "codes": BIRTHSTONE_CODE,
        })

    json.dump(maps, open(maps_path, "w", encoding="utf-8"), indent=2)
    json.dump(locs, open(locs_path, "w", encoding="utf-8"), indent=2)
    json.dump(tracker, open(trk_path, "w", encoding="utf-8"), indent=2)
    json.dump(items, open(items_path, "w", encoding="utf-8"), indent=2)

    # refresh autotracking LOCATION_MAPPING in data.lua
    if os.path.exists(data_lua):
        lua = open(data_lua, encoding="utf-8").read()
        block = "LOCATION_MAPPING = {\n" + "".join(
            f"  [{i}] = {json.dumps(p, ensure_ascii=False)},\n"
            for i, p in sorted(location_mapping.items())) + "}\n"
        lua2 = re.sub(r"LOCATION_MAPPING = \{.*?\n\}\n", block, lua, count=1, flags=re.S)
        open(data_lua, "w", encoding="utf-8").write(lua2)

    print(f"check tabs: {len(new_tabs)} regions, "
          f"{sum(len(g['children']) for g in new_groups)} checks, "
          f"{len(location_mapping)} autotrack-mapped")


if __name__ == "__main__":
    main()
