"""Generate a PopTracker pack from the apworld's data.py.

data.py is the single source of truth (items, regions, edges, locations,
events). This script emits a complete PopTracker pack under
`poptracker/legend_of_kyrandia/` whose logic mirrors Archipelago's reachability
sweep exactly:

  * a Lua fixpoint (scripts/logic.lua) expands regions through gated edges,
    earns the 4 spells + Victory as derived EVENT items, then reports each
    location as in-logic (green) / out-of-logic (red).
  * progression items are user-toggled (or AP-autotracked); spells are DERIVED,
    never toggled, because in AP they are earned by doing an event while in
    logic -- not received over the network.

Run from anywhere; paths resolve relative to the repo root.

Regenerate after editing data.py:  python pyscripts/build_poptracker.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA_PY = os.path.join(REPO, "apworld", "kyrandia", "data.py")
PACK = os.path.join(REPO, "poptracker", "legend_of_kyrandia")


def _load_data():
    spec = importlib.util.spec_from_file_location("kyradata", DATA_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slug(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


# --------------------------------------------------------------------------- #
# Tiny dependency-free PNG writer (flat RGBA) -- avoids needing Pillow.
# --------------------------------------------------------------------------- #
def write_flat_png(path: str, w: int, h: int, rgba: tuple[int, int, int, int]) -> None:
    def chunk(typ: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + typ
            + data
            + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # 8-bit RGBA
    row = bytes(rgba) * w
    raw = bytearray()
    for _ in range(h):
        raw.append(0)  # filter: none
        raw += row
    idat = zlib.compress(bytes(raw), 9)
    blob = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(blob)


def write_swatch_png(path: str, rgba: tuple[int, int, int, int]) -> None:
    write_flat_png(path, 32, 32, rgba)


# --------------------------------------------------------------------------- #
# Map layout: place a region's locations on a grid.
# --------------------------------------------------------------------------- #
BG_W, BG_H = 480, 320
GRID_COLS = 6
CELL_W, CELL_H = 72, 56
ORIGIN_X, ORIGIN_Y = 44, 40


def grid_xy(index: int) -> tuple[int, int]:
    col = index % GRID_COLS
    row = index // GRID_COLS
    return ORIGIN_X + col * CELL_W, ORIGIN_Y + row * CELL_H


def write(rel: str, content: str) -> None:
    path = os.path.join(PACK, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def write_json(rel: str, obj) -> None:
    write(rel, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- #
# Lua emission helpers
# --------------------------------------------------------------------------- #
def lua_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def lua_list(names: list[str]) -> str:
    return "{" + ", ".join(lua_str(n) for n in names) + "}"


def main() -> None:
    D = _load_data()

    prog = [n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.PROGRESSION]
    useful = [n for n, (_i, c) in D.ITEM_TABLE.items() if c == D.USEFUL]

    # name -> code (slug). Include progression + useful (filler is irrelevant to
    # the tracker). Codes must be unique.
    tracked = prog + useful
    code = {n: slug(n) for n in tracked}
    assert len(set(code.values())) == len(code), "slug collision in item codes"

    # Regions that actually hold real locations get a map tab.
    regions_with_locs: list[str] = []
    by_region: dict[str, list[tuple]] = {}
    for (name, region, loc_id, req) in D.LOCATIONS:
        by_region.setdefault(region, []).append((name, region, loc_id, req))
        if region not in regions_with_locs:
            regions_with_locs.append(region)

    # ----------------------------------------------------------------- assets
    os.makedirs(os.path.join(PACK, "assets"), exist_ok=True)
    write_flat_png(os.path.join(PACK, "assets", "bg.png"), BG_W, BG_H, (24, 28, 38, 255))
    # Simple coloured swatches so every item has an icon without art assets.
    write_swatch_png(os.path.join(PACK, "assets", "item_on.png"), (95, 200, 120, 255))
    write_swatch_png(os.path.join(PACK, "assets", "item_off.png"), (70, 78, 96, 255))
    write_swatch_png(os.path.join(PACK, "assets", "opt_on.png"), (90, 150, 230, 255))
    write_swatch_png(os.path.join(PACK, "assets", "opt_off.png"), (70, 78, 96, 255))

    # ---------------------------------------------------------------- manifest
    manifest = {
        "name": "The Legend of Kyrandia - Book 1 (AP)",
        "game_name": "The Legend of Kyrandia - Book 1",
        "package_uid": "legend_of_kyrandia_book1_ap",
        "package_version": "0.1.0",
        "author": "Kyrandia AP randomizer project",
        "variants": {
            "standard": {"display_name": "Standard", "flags": ["ap"]},
        },
        "min_poptracker_version": "0.18.2",
    }
    write_json("manifest.json", manifest)

    # ------------------------------------------------------------------- items
    items = []
    for n in prog:
        items.append({
            "name": n,
            "type": "toggle",
            "img": "assets/item_on.png",
            "disabled_img": "assets/item_off.png",
            "codes": code[n],
        })
    for n in useful:
        items.append({
            "name": n,
            "type": "toggle",
            "img": "assets/item_on.png",
            "disabled_img": "assets/item_off.png",
            "codes": code[n],
        })
    # Setting toggle: start the run already holding the Amulet (slot option).
    items.append({
        "name": "Start With Amulet",
        "type": "toggle",
        "img": "assets/opt_on.png",
        "disabled_img": "assets/opt_off.png",
        "codes": "opt_start_amulet",
    })
    write_json("items/items.json", items)

    # --------------------------------------------------------------- locations
    location_mapping: dict[int, str] = {}
    loc_root = []
    for region in regions_with_locs:
        children = []
        for i, (name, _region, loc_id, _req) in enumerate(by_region[region]):
            x, y = grid_xy(i)
            children.append({
                "name": name,
                "map_locations": [{"map": slug(region), "x": x, "y": y}],
                "sections": [{"access_rules": [f"^$kyra_loc|{loc_id}"]}],
            })
            location_mapping[loc_id] = f"@{region}/{name}"
        loc_root.append({"name": region, "children": children})

    # Derived "Powers & Goal" panel (informational; not networked).
    power_children = []
    powers = [
        ("Heal Spell", "^$kyra_event|Heal Spell"),
        ("Wisp Spell", "^$kyra_event|Wisp Spell"),
        ("Red Spell", "^$kyra_event|Red Spell"),
        ("Blue Spell", "^$kyra_event|Blue Spell"),
        ("Defeat Malcolm (Goal)", "^$kyra_goal"),
    ]
    for i, (pname, rule) in enumerate(powers):
        x, y = grid_xy(i)
        power_children.append({
            "name": pname,
            "map_locations": [{"map": "powers", "x": x, "y": y}],
            "sections": [{"access_rules": [rule]}],
        })
    loc_root.append({"name": "Powers & Goal", "children": power_children})
    write_json("locations/locations.json", loc_root)

    # -------------------------------------------------------------------- maps
    maps = []
    for region in regions_with_locs:
        maps.append({
            "name": slug(region),
            "location_size": 22,
            "location_border_thickness": 2,
            "location_shape": "rect",
            "img": "assets/bg.png",
        })
    maps.append({
        "name": "powers",
        "location_size": 22,
        "location_border_thickness": 2,
        "location_shape": "diamond",
        "img": "assets/bg.png",
    })
    write_json("maps/maps.json", maps)

    # ---------------------------------------------------------------- layouts
    # Item grid rows (8 per row) over progression items.
    def chunk_rows(names, per_row):
        return [names[i:i + per_row] for i in range(0, len(names), per_row)]

    prog_rows = [[code[n] for n in row] for row in chunk_rows(prog, 8)]
    useful_rows = [[code[n] for n in row] for row in chunk_rows(useful, 8)]

    region_tabs = []
    for region in regions_with_locs:
        region_tabs.append({"title": region, "content": {"type": "map", "maps": [slug(region)]}})
    region_tabs.append({"title": "Powers & Goal", "content": {"type": "map", "maps": ["powers"]}})

    tracker_default = {
        "tracker_default": {
            "type": "array",
            "orientation": "horizontal",
            "content": [
                {
                    "type": "array",
                    "orientation": "vertical",
                    "h_alignment": "left",
                    "content": [
                        {
                            "type": "group",
                            "header": "Progression Items",
                            "content": {"type": "itemgrid", "item_margin": "3,3", "rows": prog_rows},
                        },
                        {
                            "type": "group",
                            "header": "Setting",
                            "content": {"type": "itemgrid", "item_margin": "3,3", "rows": [["opt_start_amulet"]]},
                        },
                        {
                            "type": "group",
                            "header": "Other Items (no logic effect)",
                            "content": {"type": "itemgrid", "item_margin": "3,3", "rows": useful_rows},
                        },
                    ],
                },
                {
                    "type": "group",
                    "header": "Locations (green = in logic)",
                    "content": {"type": "tabbed", "tabs": region_tabs},
                },
            ],
        }
    }
    write_json("layouts/tracker.json", tracker_default)

    # Broadcast: compact item grid only.
    tracker_broadcast = {
        "tracker_broadcast": {
            "type": "group",
            "header": "Kyrandia Items",
            "content": {"type": "itemgrid", "item_margin": "2,2", "rows": prog_rows},
        }
    }
    write_json("layouts/broadcast.json", tracker_broadcast)

    # ----------------------------------------------------------- scripts/data.lua
    lines = []
    lines.append("-- GENERATED by pyscripts/build_poptracker.py from apworld/kyrandia/data.py")
    lines.append("-- Do not edit by hand; rerun the generator after changing data.py.")
    lines.append("KYRANDIA = {}")
    lines.append(f"KYRANDIA.start = {lua_str(D.MENU)}")
    lines.append("")
    lines.append("KYRANDIA.edges = {")
    for (frm, to, req) in D.EDGES:
        lines.append(f"  {{ from = {lua_str(frm)}, to = {lua_str(to)}, req = {lua_list(req)} }},")
    lines.append("}")
    lines.append("")
    lines.append("KYRANDIA.events = {")
    for (name, region, grants, req) in D.EVENT_LOCATIONS:
        lines.append(
            f"  {{ region = {lua_str(region)}, grants = {lua_str(grants)}, req = {lua_list(req)} }},"
        )
    lines.append("}")
    lines.append("")
    lines.append("KYRANDIA.loc_by_id = {")
    for (name, region, loc_id, req) in D.LOCATIONS:
        lines.append(f"  [{loc_id}] = {{ region = {lua_str(region)}, req = {lua_list(req)} }},")
    lines.append("}")
    lines.append("")
    lines.append("-- item display-name -> tracker code (logic reads these provider counts)")
    lines.append("KYRANDIA.item_code = {")
    for n in tracked:
        lines.append(f"  [{lua_str(n)}] = {lua_str(code[n])},")
    lines.append("}")
    lines.append("")
    lines.append("-- AP item id -> { {code}, type }  (autotracking)")
    lines.append("ITEM_MAPPING = {")
    for n in tracked:
        ap_id = D.ITEM_NAME_TO_ID[n]
        lines.append(f"  [{ap_id}] = {{ {{ {lua_str(code[n])} }}, \"toggle\" }},")
    lines.append("}")
    lines.append("")
    lines.append("-- AP location id -> tracker section path  (autotracking)")
    lines.append("LOCATION_MAPPING = {")
    for loc_id, path in location_mapping.items():
        lines.append(f"  [{loc_id}] = {lua_str(path)},")
    lines.append("}")
    lines.append("")
    write("scripts/data.lua", "\n".join(lines))

    # --------------------------------------------------------- static lua files
    write("scripts/logic.lua", LOGIC_LUA)
    write("scripts/autotracking.lua", AUTOTRACKING_LUA)
    write("scripts/init.lua", INIT_LUA)

    # ------------------------------------------------------------------- README
    write("README.md", PACK_README)

    print(f"PopTracker pack written to: {os.path.relpath(PACK, REPO)}")
    print(f"  items: {len(prog)} progression + {len(useful)} other (+1 setting)")
    print(f"  locations: {len(D.LOCATIONS)} networked, across {len(regions_with_locs)} regions")
    print(f"  events derived in logic: {len(D.EVENT_LOCATIONS)}")
    print("Load it in PopTracker via 'Open Pack...' (or symlink into the packs dir).")


# --------------------------------------------------------------------------- #
# Static Lua: the reachability engine. data.lua provides the tables.
# --------------------------------------------------------------------------- #
LOGIC_LUA = r"""-- Kyrandia Book 1 logic: a fixpoint reachability sweep that mirrors the
-- Archipelago apworld (apworld/kyrandia/data.py). See scripts/data.lua for the
-- generated tables.
--
-- Every PopTracker access rule for a location is "^$kyra_loc|<ap_id>", which
-- returns an AccessibilityLevel directly. Powers/goal use "^$kyra_event|<name>"
-- and "^$kyra_goal".

local KYRA_STATE = nil
local KYRA_SIG = nil

local function has_all(have, reqs)
  for _, r in ipairs(reqs) do
    if not have[r] then return false end
  end
  return true
end

-- Cheap signature of the relevant provider counts so we only recompute the
-- fixpoint when the held-item set actually changes.
local function signature()
  local parts = {}
  for _, c in pairs(KYRANDIA.item_code) do
    parts[#parts + 1] = c .. (Tracker:ProviderCountForCode(c) > 0 and "1" or "0")
  end
  parts[#parts + 1] = "amu" .. (Tracker:ProviderCountForCode("opt_start_amulet") > 0 and "1" or "0")
  table.sort(parts)
  return table.concat(parts, "|")
end

local function compute()
  -- Held items (received / toggled).
  local have = {}
  for name, c in pairs(KYRANDIA.item_code) do
    if Tracker:ProviderCountForCode(c) > 0 then have[name] = true end
  end
  -- start_with_amulet slot option behaves as if the Amulet is already held.
  if Tracker:ProviderCountForCode("opt_start_amulet") > 0 then
    have["Amulet"] = true
  end

  -- Fixpoint: expand reachable regions through gated edges, then earn any
  -- event item (the 4 spells + Victory) whose region is reachable and whose
  -- item requirements are met. Repeat until nothing new appears.
  local regions = { [KYRANDIA.start] = true }
  local changed = true
  while changed do
    changed = false
    for _, e in ipairs(KYRANDIA.edges) do
      if regions[e.from] and not regions[e.to] and has_all(have, e.req) then
        regions[e.to] = true
        changed = true
      end
    end
    for _, ev in ipairs(KYRANDIA.events) do
      if regions[ev.region] and not have[ev.grants] and has_all(have, ev.req) then
        have[ev.grants] = true
        changed = true
      end
    end
  end

  return { regions = regions, have = have }
end

local function state()
  local s = signature()
  if s ~= KYRA_SIG then
    KYRA_SIG = s
    KYRA_STATE = compute()
  end
  return KYRA_STATE
end

-- Access rule for a real (networked) location.
function kyra_loc(id)
  local st = state()
  local loc = KYRANDIA.loc_by_id[tonumber(id)]
  if not loc then return AccessibilityLevel.None end
  if st.regions[loc.region] and has_all(st.have, loc.req) then
    return AccessibilityLevel.Normal
  end
  return AccessibilityLevel.None
end

-- Informational: a derived spell power is "reachable" once it is in logic.
function kyra_event(name)
  local st = state()
  if st.have[name] then return AccessibilityLevel.Normal end
  return AccessibilityLevel.None
end

-- Informational: the win condition.
function kyra_goal()
  local st = state()
  if st.have["Victory"] then return AccessibilityLevel.Normal end
  return AccessibilityLevel.None
end
"""


AUTOTRACKING_LUA = r"""-- Archipelago autotracking: marks received items and checked locations.
-- Mapping tables (ITEM_MAPPING / LOCATION_MAPPING) live in scripts/data.lua.
-- Only fires when connected to an AP server with the "ap" variant.

local function onClear(slot_data)
  -- Reset tracked items so a fresh connection starts clean.
  for _, m in pairs(ITEM_MAPPING) do
    local o = Tracker:FindObjectForCode(m[1][1])
    if o then
      if m[2] == "toggle" then
        o.Active = false
      elseif m[2] == "consumable" then
        o.AcquiredCount = 0
      end
    end
  end
  -- Reflect the start_with_amulet slot option.
  local amu = Tracker:FindObjectForCode("opt_start_amulet")
  if amu then
    local v = slot_data and slot_data["start_with_amulet"]
    amu.Active = (v ~= nil and v ~= 0 and v ~= false)
  end
end

local function onItem(index, item_id, item_name, player_number)
  local m = ITEM_MAPPING[item_id]
  if not m then return end
  local o = Tracker:FindObjectForCode(m[1][1])
  if not o then return end
  if m[2] == "toggle" then
    o.Active = true
  elseif m[2] == "consumable" then
    o.AcquiredCount = o.AcquiredCount + 1
  end
end

local function onLocation(location_id, location_name)
  local path = LOCATION_MAPPING[location_id]
  if not path then return end
  local o = Tracker:FindObjectForCode(path)
  if o then
    o.AvailableChestCount = 0
  end
end

Archipelago:AddClearHandler("kyra clear", onClear)
Archipelago:AddItemHandler("kyra item", onItem)
Archipelago:AddLocationHandler("kyra location", onLocation)
"""


INIT_LUA = r"""-- PopTracker entry point. Loaded automatically when the pack opens.

-- Data tables + logic providers first, so access rules / variable providers exist
-- before any layout references them.
ScriptHost:LoadScript("scripts/data.lua")
ScriptHost:LoadScript("scripts/logic.lua")

-- Register the pack's content with PopTracker. Without these calls nothing is
-- loaded and the tracker comes up empty.
Tracker:AddItems("items/items.json")
Tracker:AddMaps("maps/maps.json")
Tracker:AddLocations("locations/locations.json")
Tracker:AddLayouts("layouts/tracker.json")
Tracker:AddLayouts("layouts/broadcast.json")

-- Autotracking only matters for the AP variant, but registering the handlers is
-- harmless otherwise (they fire only on an active Archipelago connection).
ScriptHost:LoadScript("scripts/autotracking.lua")
"""


PACK_README = """# The Legend of Kyrandia - Book 1 - PopTracker pack

Generated from `apworld/kyrandia/data.py` by `pyscripts/build_poptracker.py`.
**Do not hand-edit** the JSON / `scripts/data.lua` -- rerun the generator after
changing `data.py` so the tracker logic stays identical to the apworld's
reachability rules.

## What it shows

* **Progression Items** grid -- click an item to mark that you have it. As you
  toggle items, locations recolour.
* **Setting** -- toggle *Start With Amulet* to match that slot option.
* **Locations** tabs (one per region) -- each dot is a check:
  * **green** = in logic (you can reach + satisfy it with the items you hold)
  * **red/dim** = not in logic yet
  * click a dot to mark it collected.
* **Powers & Goal** tab -- the 4 amulet spells and the win condition light up
  green the moment they come into logic. These are *derived* (earned by doing an
  event while in logic), so there is no item to toggle for them -- exactly like
  Archipelago treats them.

## Auto-tracking (optional)

The pack has the `ap` flag. Open it in PopTracker, click **AP**, and connect to
your Archipelago server. Received items toggle on automatically and checked
locations are marked. Manual toggling still works when not connected.

## Logic status

Mirrors the apworld's **DRAFT v2** logic (not yet playthrough-verified). When the
apworld logic tightens, regenerate this pack.

## Installing

Point PopTracker at this folder (Load Pack -> Open the parent `poptracker`
folder, or copy `legend_of_kyrandia/` into your PopTracker `packs/` directory).
"""


if __name__ == "__main__":
    main()
