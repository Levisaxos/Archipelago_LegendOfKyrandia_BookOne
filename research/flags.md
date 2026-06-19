# Legend of Kyrandia Book 1 — game-flag legend (living doc)

Decoded from `APFLAG` instrumentation (engine `setGameFlag`/`resetGameFlag`,
kyra_v1.cpp) correlated with surrounding `APSCENE`/`APCHAT`/`APTALK`/`APGET`
lines. Built up as we play; **confidence** noted per entry. Flag id is decimal
(hex in parens). These are the candidate keys for AP **event locations**.

> NOTE: some sequences below were produced with debugger `give`/`toggleflag`
> use, so a few quest flags may have fired out of canonical order. Verify on a
> clean run before relying on them for logic.

## Gates / progression (high value)

| Flag | Hex | Meaning | Confidence |
|------|-----|---------|-----------|
| 63 | 0x3F | Bridge: **saw given** to Herman (NOT "repaired" — see note below). | **High** |
| 59 | 0x3B | Bridge quest started — set after first Herman talk ("I'll see what I can do"). | High |

> **Bridge is NOT flag-driven.** The `BROKEN`→`BRIDGE` change is a *room-file swap*:
> a script calls `o1_setSceneFile(7, BRIDGE)` which permanently sets
> `_roomTable[7].nameIndex` (BRIDGE = room-file idx **42**, BROKEN = idx **75**),
> and it's saved in the savegame. No combination of flags (incl. 63 + amulet 7/45)
> makes scene 7 load `BRIDGE` on its own — the nameIndex gets re-defaulted to BROKEN
> before you reach the scene. To force it we re-apply the swap on every entry to
> scene 7 (engine fork, scene_lok.cpp). **Staged scenes** generally work this way —
> e.g. `XEDGE`/`XEDGEC` are two room files for scene 13, swapped by the same opcode.
> So "open a staged gate" = swap its nameIndex, not set a flag.
| 9  | 0x09 | Crossed the fixed bridge / Herman leaves to find the saw (post-fix). | Med |
| 138| 0x8A | **Willow healed** — set on "I healed the willow tree!" (teardrop placed in the sick willow). | High |
| 71 | 0x47 | **Malcolm encounter done** (dragon's mouth, scene 25) — set when Malcolm freezes the cave; keeps him from re-triggering. | **High** |
| 82 | 0x52 | **Dragon's-mouth ice / cave block** (scene 25) — set at the freeze; while set the cave is iced & impassable. **Re-open = reset 82, keep 71 set** (ice gone, Malcolm stays gone). | **High** |
| 117 | 0x75 | **Cave rock-gate "puzzle complete"** (scene 115 GATECV) — set when the 5-rock plate puzzle finishes ("I can get back outside"). Renders as gate-open **AND** rocks-on-plate, so forcing it makes the puzzle look already-done (can't throw rocks). | **High** |

> **Cave rock-gate — DECOUPLED (implemented).** We do NOT set 117 (it couples
> gate-open with puzzle-done/rocks-shown). The west exit (`_walkBlockWest` = 197) is
> defined the whole time, but the closed gate (a) makes the scene click-script swallow
> the left-edge click and (b) collision-blocks Brandon's walk path. Fix (processInput,
> kyra_lok.cpp): on a left-edge click in scene 115, **teleport straight to 197**
> (facing 6) before the script eats it — bypassing both. The 5-rock puzzle (flags 116,
> 118–122) is left fully intact → still the spot for the future "placed the rocks"
> check. **Cosmetic TODO:** it's an instant teleport (no walk) and the gate still
> *looks* closed — could clear the walk-mask + hide the gate sprite for polish.
| 116 | 0x74 | Cave rock-gate: plate active / puzzle started (scene 115, set on entry). | High |
| 118–122 | 0x76–0x7A | Cave rock-gate: the **5 rock throws** (one flag per throw, incl. the miss). Left untouched by always-open so the puzzle still plays → future "placed rocks" check. | High |
| 42 | 0x2A | **Altar repaired** — marble placed on the altar ("Perfect fit! Must be fixed now"). | High |
| 45 | 0x2D | **Amulet manifested** at the altar (after a rose is placed → silver rose → amulet appears). | High |
| 7  | 0x07 | **Royal Amulet obtained.** | High |

## Brynn / Note quest (HEALER, scene 2) — sequence uncertain (give-command run)

| Flag | Hex | Meaning | Confidence |
|------|-----|---------|-----------|
| 130 | 0x82 | Brynn told about Kallak → "there is a clue at your home". | High |
| 242 | 0xF2 | Picked up Kallak's **Note** at home (scene 0). | High |
| 124 | 0x7C | Showed the note to Brynn ("May I see it?"). | Med |
| 129 | 0x81 | Brynn decoded the note (reveals "Amulet… Lavender Rose"). | Med |
| 125 | 0x7D | Brynn quest: lavender-rose request issued. | Med |
| 126 | 0x7E | (paired with 125). | Low |
| 127 | 0x7F | Silver rose handed over / amulet quest armed ("place this rose upon the silver altar"). | Med |
| 128 | 0x80 | (paired with 127). | Low |
| 150 | 0x96 | Leaving Brynn after note ("Amulet? What Amulet?"). | Low |

## Merith marble chase (transient per-scene state)

| Flag | Hex | Meaning | Confidence |
|------|-----|---------|-----------|
| 65 | 0x41 | Merith chase active (set at start, reset when marble caught). | High |
| 66–69 | 0x42–0x45 | Per-screen chase progress (set on enter, reset on leave, as you follow Merith). | High |
| 83 | 0x53 | Chase near-catch (FORESTB). | Med |

## One-shot "first visit / examine" comment flags (NOT gates)

Brandon's scripted one-liner the first time you enter/examine a spot. Useful to
recognize so we don't mistake them for gates.

| Flag | Hex | Where | Confidence |
|------|-----|-------|-----------|
| 157 | 0x9D | FORESTA "Something strange is happening here!" | High |
| 136 | 0x88 | SICKWIL "This willow looks half dead!" | High |
| 207 | 0xCF | SICKWIL ooze comment | Med |
| 208 | 0xD0 | SICKWIL ooze comment | Med |
| 153 | 0x99 | CAVEB "I'd like to find this Malcolm" | High |
| 152 | 0x98 | EXTSPEL (Darm's) "Anybody home?" | High |
| 144 | 0x90 | TEMPLE "This is beautiful!" | High |
| 132 | 0x84 | SORROW teardrop caught | Med |
| 202 | 0xCA | SORROW teardrop caught (paired) | Low |
| 177 | 0xB1 | HEALER floor "slippery" comment | Low |

## Transient scene-exit flags (set then immediately reset on a transition)

`51 (0x33)`, `52 (0x34)` — flip set→reset across a single `APSCENE` (e.g.
GEM↔TRUNK). Internal exit bookkeeping, not events.

## Startup burst (new-game init)

On new game the engine sets a block of flags at once: 0–4, 17–33, 72–75, plus
55/57/172, and the intro sets 243/253/239 (0xF3/0xFD/0xEF, with 0xEF reset).
These are initial state, not gameplay events — ignore for location mapping.

## Unclassified / watch

`56 (0x38)` set at saw-give, reset at amulet — purpose unclear (pending quest
item?). `0 (0x00)` toggled frequently — looks like a scratch/temp flag, do not
rely on. `8 (0x8)`, `77 (0x4D)`, `53 (0x35)`, `123 (0x7B)`, `244 (0xF4)` seen
in intro/early — meanings TBD.
