# Legend of Kyrandia — Book 1 engine hook reference (for the AP fork)

Concrete C++ function / EMC-opcode locations in the ScummVM kyra engine that the
Archipelago fork will hook or reuse. Paths are under
`scummvm-2.0.0/engines/kyra/`. **Build-blocked (Phase 0/3)** — this is read-only
reference gathered now so the engine work is fast later.

> Line numbers are against the pristine ScummVM 2.0.0 source in this repo; verify
> before editing (the fork may have shifted them).

---

## Item "poof out of hand + re-drop in a random scene"

The vanilla mechanic where placing a **wrong gem on the birthstone altar** makes it
poof and re-drop at a random Act 1b scene. This is the **reusable primitive for the
renewable-consumable design** (`hazards.md §2`): on consume, scatter the item back
into a reachable scene instead of destroying it.

### `placeItemInGenericMapScene(int item, int index)` — `items_lok.cpp:111`

THE random-scene drop. `index` (0–5) selects a band of room/scene IDs from two static
tables (`itemMapSceneMinTable` / `itemMapSceneMaxTable`):

| index | rooms (hex) | rooms (dec) | note |
|------:|-------------|-------------|------|
| 0 | 0x00–0x10 | 0–16 | |
| **1** | **0x11–0x24** | **17–36** | generic-overflow band ≈ the "Act 1b" wrong-gem drop |
| 2 | 0x6D–0xC6 | 109–198 | |
| 3 | 0x25–0x6C | 37–108 | |
| 4 | 0xC7–0xF5 | 199–245 | |
| 5 | 0x00–0x00 | — | (empty) |

Algorithm: RNG-pick a room in `[min,max]` → validate it → place. Validation:
- room `nameIndex` must be in a hardcoded whitelist (the big `switch`),
- room must have **≥1 exit** (`northExit/eastExit/southExit/westExit` not all 0xFFFF) —
  excludes dead-end map scenes,
- room must **not be the current scene**,
- then `processItemDrop(room, item, -1, -1, 2, 0)`; if it fails (e.g. scene item slots
  full) the loop retries another room until one sticks.

**Fork gotcha:** the bands are **fixed scene-ID ranges, NOT AP-reachability-aware**.
For "respawn at a random *reachable* scene" we must either pass the index band that
matches the player's current act, or write a variant that draws from an AP-reachable
scene set (the fork knows the player's progress).

### `magicOutMouseItem(int animIndex, int itemPos)` — `items_lok.cpp:650`

The "poof": item leaves the hand with a sparkle animation + SFX (`0x5E` for animIndex 2,
else `0x37`), then clears the held item. `animIndex` selects the sparkle style.

### EMC opcodes that drive the above

| Opcode | Location | Effect |
|--------|----------|--------|
| `o1_magicOutMouseItem(animIndex)` | `script_lok.cpp:344` | poof item out of hand |
| `o1_placeItemInGenericMapScene(item, index)` | `script_lok.cpp:303` | scatter to a band |
| `o1_dropItemInScene(item, x, y)` | `script_lok.cpp:133` | drop in CURRENT scene if a slot is free; **else** fall back to `placeItemInGenericMapScene` with **index 0 for the Marble (item 43), index 1 otherwise** |

The `o1_dropItemInScene` fallback (index 1 for non-Marble items) corroborates that the
wrong-gem return scatters into band 1 (rooms 17–36).

**Caveat:** the altar PUZZLE logic itself — what counts as a wrong gem, and the exact
`index` it passes — lives in **EMC bytecode** in the DAT PAK files, NOT in this C++.
The machinery above is certain; the altar's exact call needs an EMC disassembly or a
ScummVM debugger trace.

---

## Birthstone gem table (altar requirement)

See `hazards.md §4`. The 4 required gems live in `_birthstoneGemTable[4]` (`kyra_lok.h:428`),
set/read by EMC via `o1_setBirthstoneGem(index, gemId)` (`script_lok.cpp:293`) and
`o1_getBirthstoneGem(index)` (`script_lok.cpp:1439`); persisted in the savegame
(`saveload_lok.cpp`). Debugger `birthstones` command lists them (`debugger.cpp:289`).
**Fork:** suppress the native middle-two RNG and set the table from slot_data
`birthstone_gems` (the apworld already emits it).

---

## Related hook surfaces (documented elsewhere)

- **Item grant / pickup hooks** (where items reach the player — the suppress-grant
  points): `processInputHelper` ground pickup, `magicInMouseItem` scripted catch,
  `setHandItem` gift, direct-to-inventory. See memory `ref-kyra-pickup-hooks`.
- **Event flag chokepoint** (`setGameFlag`, `kyra_v1.cpp`) — every event funnels
  through it; event-location id = flag id. See memory `ref-kyra-pickup-hooks` + `flags.md`.
- **AP feedback primitives** (on-screen text `printText`, drop-on-floor `dropItem` —
  both 12-slot caps). See memory `ref-kyra-ap-feedback-primitives`.
- **No-build testing** via the ScummVM debugger (`give` / `birthstones` / `scenes` /
  `enter`). See memory `ref-scummvm-debugger`.
