"""Turn the dumped Kyrandia item sprites into PopTracker item icons.

Reads dumps/kyra_item_<NNN>.bmp (107 engine item sprites, 64x64, magenta-keyed bg),
maps each pack item code to its engine sprite id, writes transparent on/off PNGs into
the pack's assets/items/, and points items.json at them. Items with no sprite keep the
generic placeholder.

Mapping chain: pack code -> AP id (data.lua ITEM_MAPPING) -> engine id (kyra1_items.json),
with a normalized-name fallback and a few explicit overrides.

Re-run after build_poptracker.py (which regenerates items.json from data.py).

Usage:  python pyscripts/build_item_sprites.py
"""
from __future__ import annotations

import json
import os
import re
import shutil

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMPS = os.path.join(ROOT, "dumps")
PACK = os.path.join(ROOT, "poptracker", "legend_of_kyrandia")
ITEMS_JSON = os.path.join(PACK, "items", "items.json")
OUT_DIR = os.path.join(PACK, "assets", "items")
MAGENTA = (255, 0, 255)

# code -> engine id, for items the auto-mapping can't resolve by AP id or name.
# NOTE: the amulet is NOT the "Ankh" item (#45) -- the Ankh is a separate game item.
# The real amulet icon comes from `dumpamulet` (assets composited separately); until
# then `amulet` / `opt_start_amulet` keep the placeholder.
OVERRIDES = {
    "jewel": 0,             # AP "Jewel" (1000000) == the starting Garnet sprite
    "purple_rose": 16,      # one rose sprite in-game; shared with "Lavender rose"
}
SKIP = set()


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def build_code_to_engine():
    cross = json.load(open(os.path.join(ROOT, "research", "kyra1_items.json"), encoding="utf-8"))["items"]
    lua = open(os.path.join(PACK, "scripts", "data.lua"), encoding="utf-8").read()
    ap_to_code = {int(m.group(1)): m.group(2)
                  for m in re.finditer(r'\[(\d+)\]\s*=\s*\{\s*\{\s*"([^"]+)"', lua)}

    eng_by_ap_code = {}     # code -> engine id (via AP id)
    name_to_eng = {}        # normalized engine name -> engine id (head occurrence)
    for e in cross:
        if e.get("ap_id") in ap_to_code:
            eng_by_ap_code.setdefault(ap_to_code[e["ap_id"]], e["engine_id"])
        name_to_eng.setdefault(norm(e["engine_name"]), e["engine_id"])

    def resolve(code, name):
        if code in SKIP:
            return None
        if code in OVERRIDES:
            return OVERRIDES[code]
        if code in eng_by_ap_code:
            return eng_by_ap_code[code]
        for key in (norm(name), norm(code)):
            if key in name_to_eng:
                return name_to_eng[key]
        return None

    return resolve


def keyed(engine_id):
    """Load a sprite BMP, key magenta -> transparent."""
    im = Image.open(os.path.join(DUMPS, f"kyra_item_{engine_id:03d}.bmp")).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if (r, g, b) == MAGENTA:
                px[x, y] = (0, 0, 0, 0)
    return im


def dimmed(im):
    """Desaturated + darkened copy for the disabled (not-collected) state."""
    gray = im.convert("RGB").convert("L")
    dark = gray.point(lambda v: int(v * 0.5)).convert("RGBA")
    dark.putalpha(im.getchannel("A"))
    return dark


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    items = json.load(open(ITEMS_JSON, encoding="utf-8"))
    resolve = build_code_to_engine()

    if not os.path.exists(ITEMS_JSON + ".bak"):
        shutil.copy2(ITEMS_JSON, ITEMS_JSON + ".bak")

    done, placeholder = [], []
    for it in items:
        code = it["codes"]
        engine = resolve(code, it.get("name", ""))
        bmp = os.path.join(DUMPS, f"kyra_item_{engine:03d}.bmp") if engine is not None else None
        if engine is None or not os.path.exists(bmp):
            # reset to the generic placeholder so removing a mapping reverts cleanly
            it["img"] = "assets/item_on.png"
            it["disabled_img"] = "assets/item_off.png"
            placeholder.append(code)
            continue
        on = keyed(engine)
        on.save(os.path.join(OUT_DIR, f"{code}.png"))
        dimmed(on).save(os.path.join(OUT_DIR, f"{code}_off.png"))
        it["img"] = f"assets/items/{code}.png"
        it["disabled_img"] = f"assets/items/{code}_off.png"
        done.append(code)

    json.dump(items, open(ITEMS_JSON, "w", encoding="utf-8"), indent=2)
    print(f"sprites wired: {len(done)}/{len(items)}")
    print(f"kept placeholder: {placeholder}")


if __name__ == "__main__":
    main()
