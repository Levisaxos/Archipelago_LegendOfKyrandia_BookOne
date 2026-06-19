"""Build the PopTracker scene-grid maps from the room exit table.

Reads dumps/room_table.csv (id,name,N,E,S,W) + the dumps/*.bmp scene screenshots,
lays each section out as a spatial grid (BFS over cardinal exits, nearest-free-cell
conflict resolution for interior mazes), stitches the screenshots into one PNG per
section (labelled placeholder for any scene not yet dumped), and rewrites the pack's
maps.json / locations.json / layouts/tracker.json (originals backed up to *.bak).

One clickable marker per ROOM (labelled "id NAME") — this is a layout/QA view, not the
AP checks yet. Re-run after dumping more screenshots or tweaking SECTIONS.

Usage:  python pyscripts/build_scene_grid.py
"""
from __future__ import annotations

import collections
import csv
import glob
import json
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMPS = os.path.join(ROOT, "dumps")
CSV = os.path.join(DUMPS, "room_table.csv")
PACK = os.path.join(ROOT, "poptracker", "legend_of_kyrandia")
MAPS_DIR = os.path.join(PACK, "assets", "maps")

TILE_W, TILE_H = 192, 120          # downscaled scene tile (from 320x200)
MARKER = 34                        # location dot size in map pixels

# Section spec: inclusive id ranges, or a special token resolved against the room graph:
#   "WEST_FOREST"      = the isolated component you fall into past Zanthia's trap door
#   "ZANTHIA_APPROACH" = rooms 37-108 that are NOT in WEST_FOREST (the approach)
# Isolated (zero-exit, unreferenced) rooms are dropped from every section for now and
# will be re-attached to their real entrance once the APSCENE log is wired in.
WEST_FOREST_SEED = 75  # any room known to be in the post-trap-door west forest
SECTIONS = [
    ("section1", "1 · Until the Bridge",            [(0, 16)]),
    ("section2", "2 · To the Dragon's Mouth",       [(17, 36)]),
    ("section3", "3 · The Cave",                    [(109, 198)]),
    ("section4", "4 · Zanthia (before trap door)",  "ZANTHIA_APPROACH"),
    ("section5", "5 · After the Trap Door",         "WEST_FOREST"),
    ("section6", "6 · The Castle",                  [(199, 245)]),
]

DELTA = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}


def load_rooms():
    rooms = {}
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            rooms[int(r["id"])] = {
                "name": r["name"],
                "N": int(r["north"]), "E": int(r["east"]),
                "S": int(r["south"]), "W": int(r["west"]),
            }
    return rooms


def expand(ranges):
    out = []
    for a, b in ranges:
        out.extend(range(a, b + 1))
    return out


def resolve_ids(spec, rooms, comp_of, comp_size, west_comp):
    """Turn a section spec into a list of room ids, dropping isolated island rooms."""
    if spec == "WEST_FOREST":
        ids = [i for i in rooms if comp_of[i] == west_comp]
    elif spec == "ZANTHIA_APPROACH":
        ids = [i for i in expand([(37, 108)]) if i in rooms and comp_of[i] != west_comp]
    else:
        ids = [i for i in expand(spec) if i in rooms]
    # size-1 components = zero-exit island rooms (dead entries or click-only interiors);
    # exclude until APSCENE attaches the real ones to their entrance.
    return [i for i in ids if comp_size[comp_of[i]] > 1]


def global_layout(rooms):
    """Lay out each cardinal-connected COMPONENT into global grid cells via BFS, with
    nearest-free-cell conflict resolution for non-planar interior mazes. Returns
    pos[room]=(col,row) (per-component local origin) and comp_of[room]=component id."""
    adj = collections.defaultdict(dict)
    und = collections.defaultdict(set)
    for i, r in rooms.items():
        for d in DELTA:
            t = r[d]
            if t in rooms:
                adj[i][d] = t
                und[i].add(t)
                und[t].add(i)

    seen, comp_of, comps = set(), {}, []
    for i in rooms:
        if i in seen:
            continue
        stack, comp = [i], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack += [y for y in und[x] if y not in seen]
        for x in comp:
            comp_of[x] = len(comps)
        comps.append(comp)

    pos = {}
    bumped = 0
    for comp in comps:
        occupied = {}

        def free_cell(cell):
            if cell not in occupied:
                return cell, False
            cx, cy = cell
            r = 1
            while True:
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        if max(abs(dx), abs(dy)) != r:
                            continue
                        nc = (cx + dx, cy + dy)
                        if nc not in occupied:
                            return nc, True
                r += 1

        root = min(comp)
        pos[root] = (0, 0)
        occupied[(0, 0)] = root
        q = collections.deque([root])
        bfs_seen = {root}
        while q:
            a = q.popleft()
            ax, ay = pos[a]
            # traverse undirected so one-way rooms (entered by clicking, only an exit
            # out) are still reached; infer the direction from whichever side's exit exists.
            for t in und[a]:
                if t in bfs_seen:
                    continue
                d = next((dd for dd, tt in adj[a].items() if tt == t), None)
                if d is None:
                    d = next((OPP[dd] for dd, tt in adj[t].items() if tt == a), None)
                if d is None:
                    continue
                bfs_seen.add(t)
                dx, dy = DELTA[d]
                cell, was_bumped = free_cell((ax + dx, ay + dy))
                pos[t] = cell
                occupied[cell] = t
                bumped += was_bumped
                q.append(t)
    return pos, comp_of, bumped


def layout_local(ids, rooms):
    """Lay a section out from its OWN internal exits (not the global map), so a section
    that is a subset of a big component still packs tightly. Each internally-connected
    sub-cluster is BFS-placed (undirected, conflict-resolved) and tiled left-to-right."""
    S = set(ids)
    adj = collections.defaultdict(dict)
    und = collections.defaultdict(set)
    for i in ids:
        for d in DELTA:
            t = rooms[i][d]
            if t in S:
                adj[i][d] = t
                und[i].add(t)
                und[t].add(i)

    seen, clusters = set(), []
    for i in sorted(ids):
        if i in seen:
            continue
        stack, comp = [i], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack += [y for y in und[x] if y not in seen]
        clusters.append(comp)
    clusters.sort(key=len, reverse=True)

    placed, xoff, bumped = {}, 0, 0
    for comp in clusters:
        occ = {}

        def free_cell(cell):
            if cell not in occ:
                return cell
            cx, cy = cell
            r = 1
            while True:
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        if max(abs(dx), abs(dy)) != r:
                            continue
                        nc = (cx + dx, cy + dy)
                        if nc not in occ:
                            return nc
                r += 1

        root = min(comp)
        lp = {root: (0, 0)}
        occ[(0, 0)] = root
        q = collections.deque([root])
        bs = {root}
        while q:
            a = q.popleft()
            ax, ay = lp[a]
            for t in und[a]:
                if t in bs:
                    continue
                d = next((dd for dd, tt in adj[a].items() if tt == t), None)
                if d is None:
                    d = next((OPP[dd] for dd, tt in adj[t].items() if tt == a), None)
                if d is None:
                    continue
                bs.add(t)
                dx, dy = DELTA[d]
                want = (ax + dx, ay + dy)
                cell = free_cell(want)
                bumped += cell != want
                lp[t] = cell
                occ[cell] = t
                q.append(t)

        minc = min(c for c, _ in lp.values())
        minr = min(r for _, r in lp.values())
        width = max(c for c, _ in lp.values()) - minc + 1
        for room, (c, r) in lp.items():
            placed[room] = (c - minc + xoff, r - minr)
        xoff += width + 1

    cols = max(c for c, _ in placed.values()) + 1
    rows = max(r for _, r in placed.values()) + 1
    return placed, cols, rows, bumped


def screenshot_for(room_id):
    hits = glob.glob(os.path.join(DUMPS, f"kyra_scene_{room_id:03d}_*.bmp"))
    return hits[0] if hits else None


def _font(size):
    for path in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def label(draw, x, y, text, font):
    pad = 2
    try:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        tw, th = r - l, b - t
    except Exception:
        tw, th = len(text) * 6, 11
    draw.rectangle([x, y, x + tw + 2 * pad, y + th + 2 * pad], fill=(0, 0, 0))
    draw.text((x + pad, y + pad), text, fill=(255, 235, 120), font=font)


def stitch(slug, placed, cols, rows, rooms):
    img = Image.new("RGB", (cols * TILE_W, rows * TILE_H), (18, 18, 22))
    draw = ImageDraw.Draw(img)
    font = _font(13)
    have = 0
    for room, (c, r) in placed.items():
        x0, y0 = c * TILE_W, r * TILE_H
        shot = screenshot_for(room)
        if shot:
            tile = Image.open(shot).convert("RGB").resize((TILE_W, TILE_H))
            img.paste(tile, (x0, y0))
            have += 1
        else:
            draw.rectangle([x0, y0, x0 + TILE_W - 1, y0 + TILE_H - 1],
                           fill=(40, 40, 52), outline=(70, 70, 90))
            draw.text((x0 + TILE_W // 2 - 24, y0 + TILE_H // 2 - 6),
                      "no shot", fill=(150, 150, 170), font=font)
        draw.rectangle([x0, y0, x0 + TILE_W - 1, y0 + TILE_H - 1], outline=(90, 90, 110))
        label(draw, x0 + 2, y0 + 2, f"{room} {rooms[room]['name']}", font)
    os.makedirs(MAPS_DIR, exist_ok=True)
    img.save(os.path.join(MAPS_DIR, f"{slug}.png"))
    return have


def backup(path):
    if os.path.exists(path) and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")


def main():
    rooms = load_rooms()
    pos, comp_of, bumped = global_layout(rooms)
    comp_size = collections.Counter(comp_of.values())
    west_comp = comp_of[WEST_FOREST_SEED]
    dropped = sorted(i for i in rooms if comp_size[comp_of[i]] == 1)
    print(f"global layout: {len(rooms)} rooms, {len(comp_size)} components, "
          f"{bumped} maze-bumped")
    print(f"dropped {len(dropped)} isolated island rooms (re-add via APSCENE later): "
          f"{', '.join(str(i) for i in dropped)}\n")
    maps_json, locations_json, tabs = [], [], []

    for slug, title, spec in SECTIONS:
        ids = resolve_ids(spec, rooms, comp_of, comp_size, west_comp)
        placed, cols, rows, bumped_s = layout_local(ids, rooms)
        have = stitch(slug, placed, cols, rows, rooms)
        print(f"{slug:9s} {title:28s} rooms={len(ids):3d} shots={have:3d} "
              f"missing={len(ids) - have:3d} grid={cols}x{rows} bumped={bumped_s}")

        maps_json.append({
            "name": slug, "img": f"assets/maps/{slug}.png",
            "location_size": MARKER, "location_border_thickness": 2,
            "location_shape": "rect",
        })
        children = []
        for room, (c, r) in sorted(placed.items()):
            cx = c * TILE_W + TILE_W // 2
            cy = r * TILE_H + TILE_H // 2
            nm = f"{room} {rooms[room]['name']}"
            children.append({
                "name": nm,
                "map_locations": [{"map": slug, "x": cx, "y": cy}],
                "sections": [{"name": nm}],
            })
        locations_json.append({"name": title, "children": children})
        # tab structure must match PopTracker's proven form: a tab is
        # {"title": ..., "content": <widget>}, NOT a widget with "type" at tab level.
        tabs.append({"title": title, "content": {"type": "map", "maps": [slug]}})

    # write maps + locations (backed up)
    mpath = os.path.join(PACK, "maps", "maps.json")
    lpath = os.path.join(PACK, "locations", "locations.json")
    tpath = os.path.join(PACK, "layouts", "tracker.json")
    for p in (mpath, lpath, tpath):
        backup(p)
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(maps_json, f, indent=2)
    with open(lpath, "w", encoding="utf-8") as f:
        json.dump(locations_json, f, indent=2)

    # patch the tabbed map block in the layout, keep the item grids
    with open(tpath, encoding="utf-8") as f:
        layout = json.load(f)
    for col in layout["tracker_default"]["content"]:
        if col.get("type") == "group" and col.get("content", {}).get("type") == "tabbed":
            col["content"]["tabs"] = tabs
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=2)

    print("\nWrote maps.json, locations.json, tracker.json (originals -> *.bak)")


if __name__ == "__main__":
    main()
