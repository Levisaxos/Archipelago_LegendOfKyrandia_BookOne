# Kyrandia → Archipelago — Roadmap

Step-by-step plan to a working **Book 1 item-randomizer**, then stretch goals.

**Scope of V1:** item randomizer only (shuffle *what* each pickup gives). Entrance/
region shuffle and the full "open world" redesign are post-V1.

**Status legend:** ✅ done · 🔄 in progress · ⬜ not started · 🧱 blocked

Phases 1–5 below map to the agreed plan (research → apworld → engine mod → AP
connection → V1). **Phase 0** is a prerequisite track (build toolchain) that must be
unblocked before Phases 3–5; it can run in parallel with Phases 1–2.

---

## Phase 0 — Prerequisites (build toolchain) ✅ DONE

- ✅ **Toolchain:** MSVC (VS 2022 Professional, v143). C++ workload + Win11 SDK 10.0.26100 installed.
- ✅ **Fork base:** pinned to ScummVM 2.0.0 (exact GOG match), full source at `scummvm-2.0.0/`.
- ✅ **Dependencies:** SDL2 2.32.2 VC prebuilt libs at `build/deps/`; `create_project.exe` built.
- ✅ **Minimal build:** Kyra-only + SDL2 solution (`build/msvc/`), built via `build/build_scummvm.bat`
  (retargets generated v141 projects to v143). Produces `build/msvc/Release64/scummvm.exe` (13 MB).
- ✅ **Verified:** our exe runs and detects the GOG Kyrandia data (`kyra1 CD/DOS/English`).
- **Deliverable:** ✅ reproducible local build of ScummVM running Kyrandia. Edit→rebuild loop works.

---

## Phase 1 — Research / instrumentation 🔄

Goal: the authoritative item / location / flag maps and the hazard list — the raw
material everything else is built on.

- ✅ **Engine item-ID table** — extracted `k1ItemNames` (0–106) → `research/kyra1_item_ids.txt`.
- ✅ **Engine ↔ AP crosswalk** — `research/kyra1_items.json` (+ generator). Verified Ruby=6, Teardrop=52, etc.
- ✅ **Item-grant mechanism** — identified `magicInMouseItem` / `o1_magicInMouseItem`; `_itemInHand` + cursor `_shapes[216+id]`. (The teardrop→ruby hook point.)
- ✅ **Charge ladders** — confirmed Fireberries 29–33 are depleting charge states (model in crosswalk).
- ⬜ **Read-only instrumentation** *(now unblocked — Phase 0 done)* — log every inventory add/remove and `setGameFlag`/`queryGameFlag` across a full playthrough. This *is* the raw location/flag map and the way to replace the DRAFT location list below with verified data.
- 🔄 **Location enumeration** — ✅ DRAFT done: `research/locations.json` v2 (64 networked locations + 5 event locations: pickups, NPC turn-ins, potion brews, the ice-break, 4 spell-earns) derived from the plan doc + walkthrough knowledge. ⬜ NOT yet verified screen-by-screen; per-entry accuracy + exact screen/gem counts still pending instrumentation.
- 🔄 **Hazard list** — ✅ DRAFT done: `research/hazards.md` (two forced inventory wipes, consumables/charge ladders, native gem RNG, one-way transitions, instant-death) with apworld-vs-engine responsibilities. ⬜ full death-screen list + exact wipe code/flag triggers still need a playthrough.
- ⬜ **Resolve open mappings** — spell→source→color (Magestones 95–101); charge-ladder `kind` for Scroll/potions/waters; Jade(58) vs Obsidion(59) key; native gem RNG behavior (`o1_setBirthstoneGem` + `_birthstoneGemTable`).
- ✅ **Confirm hook points in code** — pickup/grant sites found (`processInputHelper` ground pickup, `magicInMouseItem` scripted catch, `setHandItem` gift, direct-to-inventory); scene items in `_roomTable[sceneId].itemsTable[]` → ground location = `(sceneId, slot)`. FLAG chokepoint found: `setGameFlag` (kyra_v1.cpp:511) — single 3-line fn every event funnels through (opcode `o1_setGameFlag`) → event location = flag id. Complete outgoing surface = `processInputHelper` + `setGameFlag`.
- **Deliverable:** `research/locations.json` + `research/logic.md` + `research/hazards.md` exist as **DRAFT** (consumed by the apworld); ⬜ the instrumentation-verified versions + fully-confirmed crosswalk remain.

---

## Phase 2 — AP world ("apworld") ✅ DONE (DRAFT logic)  *(Python)*

Goal: a loadable Archipelago world for Book 1 that generates valid seeds, even before
the game client exists. Source at `apworld/kyrandia/` (built to `apworld/kyrandia.apworld`);
`data.py` is the single source of truth → `pyscripts/dump_research.py` regenerates the
research JSON, `pyscripts/build_apworld.py` zips it. Targets Archipelago 0.6.6.

- ✅ Scaffolded the apworld (modern AP 0.6.x API: `World`, options dataclass, items/locations/regions/rules). Springboard = the working `gcfw` world.
- ✅ **Item pool** (33 progression / 24 useful / padded filler) and **location list** (64 + 5 event), all from `data.py`.
- ✅ **Region graph + access rules** — 11 regions, "Model A" vanilla item gates (globally-open, *not* intra-act sub-graphs). Reachability invariant enforced (every rule item is progression/event).
- ✅ **Completion condition** — reworked from "place regalia" to the true goal: **Defeat Malcolm (turn to stone)** = Crown + Sceptre + Royal chalice + Mirror + Red Spell → Victory.
- ✅ Structural hazards modeled in logic (wipes assumed neutralized; no early-region check gated on a late-region item; consumables treated as one persistent unit).
- ✅ **Universal Tracker support** (`interpret_slot_data` + `re_gen_passthrough`).
- ✅ Generated & validated **single- and multi-world** seeds; **unit tests** (`tests/`) prove beatability via an independent logic sweep + data invariants (7 tests pass).
- ⬜ *Pending Phase 1:* swap the DRAFT logic for instrumentation-verified data; flesh out `fill_slot_data` with the AP-id→engine-id crosswalk the client needs; optional traps / option variants / hint groups.
- **Deliverable:** ✅ a Kyrandia apworld that generates a valid Book 1 seed (DRAFT logic, provably winnable under its own rules).

---

## Phase 3 — Engine mod (ScummVM fork): offline item randomizer ⬜  *(needs Phase 0)*

Goal: the forked engine suppresses vanilla item grants and applies externally-chosen
item identities — driven by a **local seed file** (no server yet).

- 🔄 **Outgoing hook** — ✅ suppress-grant PROVEN in-game (garnet id 0 destroy-on-pickup with vanish FX, `processInputHelper`). ⬜ still need: emit a "location checked" event (log/file), and generalize from one hard-coded id to all tracked pickups.
- ⬜ **Incoming primitive** — a function to add inventory item / set flag by engine ID, with a small queue.
- ⬜ **Remap proof — the teardrop→ruby test:** static seed maps the willow location (engine 52) → grant engine 6. Validate via the crosswalk.
- ⬜ **Charge-ladder handling** — on grant, always hand the **head** (full) ID; on pickup-detect, treat any member ID as the item.
- ⬜ **Neutralize wipes + gem RNG** — remove the two inventory wipes; suppress native birthstone RNG so placement is controlled.
- ⬜ **Persist randomizer state** across save/load (extend kyra save or side-file keyed to seed+slot).
- **Deliverable:** forked ScummVM that, given a local seed file, shuffles item identities in-game (offline).

---

## Phase 4 — AP connection ⬜  *(needs Phases 2 + 3)*

Goal: wire the engine to a live Archipelago server.

- ✅ **Feasibility confirmed** (2026-06-11): apclientpp = MIT, header-only deps except OpenSSL (TLS only). Poll-based (`apclient.poll()` per frame) → fits ScummVM loop. The garnet demo already exercises the whole client surface with hardcoded values.
- ⬜ **First test the easy way:** compile with `WSWRAP_NO_SSL`, connect to a LOCAL AP server over `ws://` (no OpenSSL needed). Generate a Book 1 seed from the apworld (AP 0.6.6 installed).
- ✅ **Stack compiles/links/RUNS standalone** (2026-06-11): `build/deps/ap/test_connect.exe` proves apclientpp+asio+websocketpp build under MSVC v143 and attempt a real ws:// connection. Pinned asio-1-12-2 + websocketpp-0.8.2 (latest are incompatible). Recipe in `build/build_ap_test.bat` + memory.
- ⬜ Embed **apclientpp** as an isolated bridge (`engines/kyra/ap_bridge.cpp`, `FORBIDDEN_SYMBOL_ALLOW_ALL`, /EHsc) — plain ap_init/ap_poll/ap_sendCheck + item callback; retain MIT notices per `docs/legal_disclaimer.md`. Add OpenSSL 3.x later for public `wss://`.
- ✅ **Embedded + CONNECTED** (2026-06-11): `ap_bridge.lib` (built by `build/build_ap_bridge.bat`, /MD) linked into scummvm.exe via `ScummVM_Global64.props` edits (include dir + ap_bridge.lib;ws2_32.lib;shell32.lib). Engine: connect in `init()` (ConfMan ap_host/ap_slot/ap_password, default ws://localhost:38281 / Player1), connection screen + per-frame `KyraAP::poll()` in `mainLoop()`. Verified: our build joined a local AP server hosting a generated Kyrandia seed ("Player1 ... has joined").
- 🔄 **Outgoing wired (first real location)**: ground pickup of Garnet (engine 0) → `KyraAP::sendCheck(1010002)` + suppress (poof) + auto-fading `drawSentenceCommand` message. ⬜ Generalize: full `(sceneId, slot) -> AP location id` map needs Phase 1 instrumentation (only garnet hardcoded so far). Also hook events via `setGameFlag`.
- ✅ **Incoming wired**: `KyraAP::nextReceivedItem` → `apItemToEngineId` (generated `ap_item_map.h` from crosswalk+apworld, 61 items) → `apDropReceivedItem` drops on floor near Brandon. Bridge dedupes by `NetworkItem.index` (reconnect-safe). ⬜ TODO: floor-full queue/retry; tag AP-dropped items so re-pickup doesn't re-check; 4 items (Amulet/Mallet/Jewel/Purple rose) have no engine id.
- ✅ **In-game connection form** (2026-06-11): `KyraEngine_LoK::apConnectionScreen()` at mainLoop start — editable Server/Slot/Password fields (raw events via `_system->getEventManager()->pollEvent`, TAB/arrows/type/ENTER), pre-filled from + saved to ConfMan (ap_host/ap_slot/ap_password). No .txt needed. (Could move to go() if we want it before the intro.)
- ✅ **Saves linked to seed/server** (2026-06-11): `saveload_lok.cpp` prefixes the visible save name with the address (`host:port | name`, strip-on-resave heuristic via " | "+colon) and appends a machine-readable AP chunk (`MKTAG('A','P','K','1')` + host + slot) read back on load (pos/size-guarded so vanilla saves are safe). Uses ConfMan ap_host/ap_slot (no bridge change).
- ⬜ Connection flow polish: reconnect-on-load (use the save's stored server), invalid-slot error timeout back to form, native dialog styling, seed_name verification. Add zlib/compression + OpenSSL for prod `wss://`.
- **Deliverable:** 🔄 connection DONE; check/item flow next.

---

## Phase 5 — Working V1 ⬜

Goal: a releasable Book 1 item-randomizer.

- ⬜ Full playthrough on a generated seed, start → Kyragem ending, **no softlock**; fix logic/hook gaps.
- ⬜ Multiworld smoke test (2 slots, or Kyrandia + another game).
- ⬜ Goal/completion send; optional deathlink.
- ⬜ **Packaging (asset-free):** engine fork + our code only (user supplies GOG data); rename from "ScummVM"; bundle dependency license texts; ship the disclaimer (per `docs/legal_disclaimer.md`).
- ⬜ **Docs:** install/setup guide, player options (yaml), known issues.
- **Deliverable:** V1 item-randomizer release.

---

## Phase 6 — Stretch (post-V1) ⬜

Only after V1 proves the returns + wipe-removal are sane.

- ⬜ **Entrance / region shuffle** — add return-path edges that don't exist in vanilla (chasm, foyer, island); make one-way transitions two-way on unlock.
- ⬜ Cross-act shuffle (beyond intra-act).
- ⬜ Expanded item categories (full gem pool, amulet spells, traps), hint system, more options.
- ⬜ **Books 2 & 3** (id spaces already reserved at 2,000,000 / 3,000,000).

---

## Decisions
1. ✅ Toolchain: **MSVC** (VS 2022, v143). *(resolved — Phase 0)*
2. ✅ Fork base: **pinned ScummVM 2.0.0**. *(resolved — Phase 0)*
3. Inventory-wipe strategy: **remove wipes** vs **per-act logic sub-graphs** — apworld currently assumes wipes are removed; confirm in Phase 3. *(open)*
4. Charge-ladder / duplicate `kind` for potions/waters/scroll — resolve in Phase 1 instrumentation. *(open)*

## Status snapshot (2026-06-11)
✅ Phase 0 (build toolchain) · ✅ Phase 2 (apworld, DRAFT logic) · 🔄 Phase 1 (research: DRAFT
deliverables done, instrumentation pending) · 🔄 Phase 3 (engine mod: suppress-grant proven).

## Immediate next step
The two parallel tracks that unblock the most:
- **Phase 1 — read-only instrumentation** (now possible — Phase 0 build works). A logged
  playthrough turns the DRAFT `research/` data into verified `(sceneId, slot)` + flag maps;
  the existing apworld tests then re-validate the corrected logic automatically.
- **Phase 3 — engine mod** — generalize the proven suppress-grant hook to all tracked
  pickups + emit "location checked" events, then the teardrop→ruby remap proof.
- *(Then Phase 4 wires apclientpp once Phases 2+3 meet.)*
