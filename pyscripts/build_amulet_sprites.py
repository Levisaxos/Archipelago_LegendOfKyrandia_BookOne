"""Turn the dumped amulet images into PopTracker item icons.

Inputs (from `dumpamulet`, run while in the ALTAR scene):
  dumps/kyra_amulet_full.bmp    - amulet with all 4 jewels  -> the "amulet" item icon
  dumps/kyra_amulet_pos0..3.bmp - amulet with one jewel lit -> per-gem on/off sprites

Produces, in the pack's assets/items/:
  amulet.png / _off.png                          (the amulet item)
  amulet_red/blue/heal/wisp.png + _off.png       (each gem: coloured = on, grey = off)

Then makes the 4 gems toggle items in items.json and appends them to the Progression
Items grid in the layout, so the amulet + 4 colour pips sit with the rest of the items.

Gem layout on the amulet: red=left, blue=right, heal=gold/top, wisp=purple/bottom.
Each gem's "on" is cropped from the dump where it's lit; "off" from a dump where its
socket is empty (grey). Coords are in the 384x200 dump space.

Usage:  python pyscripts/build_amulet_sprites.py
"""
from __future__ import annotations

import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMPS = os.path.join(ROOT, "dumps")
PACK = os.path.join(ROOT, "poptracker", "legend_of_kyrandia")
ITEMS_JSON = os.path.join(PACK, "items", "items.json")
LAYOUT = os.path.join(PACK, "layouts", "tracker.json")
OUT_DIR = os.path.join(PACK, "assets", "items")
MAGENTA = (255, 0, 255)

# code, display, gem center (dump px), "on" dump (gem lit), "off" dump (socket grey).
# Centers measured from the dumps (each gem spans ~99x59); box sized to fit fully.
GEMS = [
    ("amulet_heal", "Heal Spell", (201,  69), "pos2", "pos0"),
    ("amulet_wisp", "Wisp Spell", (201, 157), "pos3", "pos0"),
    ("amulet_red",  "Red Spell",  (113, 113), "pos0", "pos1"),
    ("amulet_blue", "Blue Spell", (289, 113), "pos1", "pos0"),
]
GEM_W, GEM_H = 104, 64


def key_transparent(im):
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][:3] == MAGENTA:
                px[x, y] = (0, 0, 0, 0)
    return im


def crop_gem(posname, center):
    im = key_transparent(Image.open(os.path.join(DUMPS, f"kyra_amulet_{posname}.bmp")))
    cx, cy = center
    return im.crop((cx - GEM_W // 2, cy - GEM_H // 2, cx + GEM_W // 2, cy + GEM_H // 2))


def amulet_icon():
    im = key_transparent(Image.open(os.path.join(DUMPS, "kyra_amulet_full.bmp")))
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im


def add_pips_to_progression(layout, codes):
    """Append a row of the gem codes to the Progression Items itemgrid (idempotent)."""
    def find_grid(o):
        if isinstance(o, dict):
            if o.get("type") == "group" and o.get("header") == "Progression Items":
                c = o.get("content", {})
                if c.get("type") == "itemgrid":
                    return c
            for v in o.values():
                r = find_grid(v)
                if r:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = find_grid(v)
                if r:
                    return r
        return None

    grid = find_grid(layout)
    if not grid:
        return False
    flat = [c for row in grid["rows"] for c in row]
    if any(c in flat for c in codes):  # already added
        return True
    grid["rows"].append(list(codes))
    return True


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # amulet item icon
    amu = amulet_icon()
    amu.save(os.path.join(OUT_DIR, "amulet.png"))
    off = amu.convert("RGB").convert("L").point(lambda v: int(v * 0.5)).convert("RGBA")
    off.putalpha(amu.getchannel("A"))
    off.save(os.path.join(OUT_DIR, "amulet_off.png"))

    # per-gem on (lit) / off (grey socket)
    for code, _name, center, on_pos, off_pos in GEMS:
        crop_gem(on_pos, center).save(os.path.join(OUT_DIR, f"{code}.png"))
        crop_gem(off_pos, center).save(os.path.join(OUT_DIR, f"{code}_off.png"))

    # items.json: point amulet at its icon; add the 4 gem toggle items
    items = json.load(open(ITEMS_JSON, encoding="utf-8"))
    have = {it["codes"] for it in items}
    for it in items:
        if it["codes"] in ("amulet", "opt_start_amulet"):
            it["img"] = "assets/items/amulet.png"
            it["disabled_img"] = "assets/items/amulet_off.png"
    for code, name, *_ in GEMS:
        if code not in have:
            items.append({
                "name": name, "type": "toggle",
                "img": f"assets/items/{code}.png",
                "disabled_img": f"assets/items/{code}_off.png",
                "codes": code,
            })
    json.dump(items, open(ITEMS_JSON, "w", encoding="utf-8"), indent=2)

    # layout: append the 4 gems to the Progression Items grid
    layout = json.load(open(LAYOUT, encoding="utf-8"))
    ok = add_pips_to_progression(layout, [g[0] for g in GEMS])
    json.dump(layout, open(LAYOUT, "w", encoding="utf-8"), indent=2)

    print(f"amulet icon {amu.size}; gems: {[g[0] for g in GEMS]}; grid row added: {ok}")


if __name__ == "__main__":
    main()
