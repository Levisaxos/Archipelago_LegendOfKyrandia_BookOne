# The Legend of Kyrandia - Book 1 - PopTracker pack

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
