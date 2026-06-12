# Kyrandia → Archipelago — Project Handoff

Goal: an Archipelago (archipelago.gg) randomizer for The Legend of Kyrandia,
starting with **Book 1**, then Books 2 & 3. End state: a thing a user installs
on their PC that alters game mechanics and puts AP in the middle.

Companion doc: `kyrandia_book1_randomizer_plan.md` (content/ID data plan).

---

## Ground rules (for Claude Code)
- Work on **local files on my machine**. No GitHub pushes unless I explicitly say so.
- **No worktrees.**
- Languages: **C++** (ScummVM engine fork) + **Python** (AP world). Not C#.
- Any code lifted from elsewhere: cite source URL + license, and offer a clean-room version.

---

## Architecture (decided)
- **Fork ScummVM** (GPL-3.0-or-later — forking allowed, source must be published).
  This is the client side of the AP integration.
- GOG Kyrandia is **already ScummVM-based** (just data files + bundled ScummVM),
  so the user swaps in our build / points it at the GOG game folder. Easy install.
- **No mod API exists** for ScummVM game logic, and no Lua/memory bridge — the
  engine fork is the correct and only clean route.
- Embed **apclientpp** (black-sliver's C++ AP client lib) in the fork so ScummVM
  itself is the AP client (single process, no separate connector).
  Repo: https://github.com/black-sliver/apclientpp  — verify its license before bundling.
- Book 1 engine class: `KyraEngine_LoK` in `engines/kyra/`.

### Data flow
- **Outgoing (game → AP):** hook the item-pickup / inventory-add path and the
  game-flag set path. On a pickup or key flag flip → map to an AP **location ID**
  → call apclientpp `LocationChecks`. Suppress the vanilla item grant (remove the
  scene object, give nothing locally).
- **Incoming (AP → game):** on apclientpp item-received callback → translate AP
  **item ID** to "add inventory item" or "set game flag" via the engine's own
  functions. Need a small **queue** (Book 1's inventory is tiny / can be full).
- **Saves:** persist AP state (sent checks, received items) across save/load —
  extend kyra save format or keep a side-file keyed to seed+slot.

---

## Design philosophy: make it non-linear ("open")
Replace **story gates** with **item gates that open a region edge both ways**.

Core rule: **every one-way transition must become two-way once its unlock is
received, or get a separate return path.**

Gate → unlock mapping:
| Vanilla gate | AP unlock item | Notes |
|---|---|---|
| Broken bridge | `Bridge Repaired` | drop NPC requirement; "talk to Herman" can stay as a *check* |
| Grotto / labyrinth entrance | `Grotto Access` | vanilla = knife-throw + flute |
| Pegasus to grave island | `Pegasus` | **transport, not a wall** — must be a 2-way portal OR place return vehicle on island side |

Engine work this implies (because we're forking anyway):
1. **Add return exits** that don't exist in vanilla (chasm crossing, foyer, island).
2. **Remove the two forced inventory wipes** (labyrinth "drop everything except
   scroll"; foyer destroying items) — otherwise backtracking strands items.
3. **Return-path keys must be un-losable** (amulet spells = safe; never gate a
   return on a consumable).
4. **Suppress native gem RNG** so AP controls gem placement (don't run both).

Scope call: start with **intra-act shuffle** (safe logic). Full cross-act
entrance shuffle only after returns + wipe-removal are proven.

---

## First testing steps (Claude Code)
1. Get ScummVM source locally; build vanilla; confirm **Book 1 (GOG data) runs**.
2. Locate hook points in `engines/kyra/` for `KyraEngine_LoK`:
   - inventory add/remove functions
   - `setGameFlag` / `queryGameFlag` (+ the EMC opcodes that call them)
   - the scene item-pickup handler
3. **Read-only instrumentation first:** log every flag-set and inventory-add.
   Play through and record the sequence — this *is* the raw location/flag map.
4. Cross-reference that log against `kyrandia_book1_randomizer_plan.md` to firm up
   the item/location lists and find the death/softlock + wipe trigger points.
5. Only then: pull in apclientpp and wire outgoing `LocationChecks`.

## Open questions to resolve during testing
- Exact function/struct names for inventory + flags in `KyraEngine_LoK`.
- Full death-screen / softlock list.
- Where the two inventory wipes are triggered in code.
- Spell → source → color mapping (verify against the flag log).
- Whether to model acts as separate logic sub-graphs or globally open.
