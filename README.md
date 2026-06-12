# Legend of Kyrandia → Archipelago Randomizer (Book 1)

An [Archipelago](https://archipelago.gg) randomizer for *The Legend of Kyrandia*
(Book 1 first, then 2 & 3), built by **forking ScummVM** so the engine itself is
the Archipelago client.

See [docs/kyrandia_ap_handoff.md](docs/kyrandia_ap_handoff.md) for the architecture
and [roadmap/ROADMAP.md](roadmap/ROADMAP.md) for the plan and current status.

## Folder structure

| Folder | Purpose |
|--------|---------|
| `scummvm-2.0.0/` | The ScummVM engine fork. Only our **modified** `engines/kyra/` files are tracked; extract the rest from the GOG `scummvm-2.0.0.zip` (see [SETUP.md](SETUP.md)). |
| `build/` | Build scripts (`*.bat`), the AP client bridge (`deps/ap/bridge/`), and the generated MSVC solution + fetched deps (git-ignored). |
| `apworld/` | The Archipelago world (Python) — items, locations, regions, rules. |
| `tests/` | apworld unit tests (beatability sweep + data invariants). |
| `poptracker/` | PopTracker pack for the world. |
| `pyscripts/` | Tooling — data extractors and generators. |
| `research/` | Extracted & derived data: engine item tables, ID maps, findings. |
| `docs/` | Design docs: randomizer plan, AP handoff, legal/licensing notices. |
| `roadmap/` | Step-by-step plan and milestone status. |

## Status

Working vertical slice: a self-built ScummVM that connects to a live Archipelago
server, with an in-game connection screen, saves linked to their seed, and a
**real end-to-end loop** (pickup → location check → item received → delivered
in-game). Next: scrape the full location map so every pickup/event is a check.
See the roadmap for details.

## Building

This repo excludes the vanilla ScummVM tree and all third-party build
dependencies (they're large and re-fetchable). See **[SETUP.md](SETUP.md)** to
reconstitute a buildable tree from a fresh clone. You must supply your own
legally-owned Kyrandia game data (the repo ships **no** game content).

## License

This project is licensed **GPL-3.0-or-later** — see [LICENSE](LICENSE).

It contains a fork of [ScummVM](https://www.scummvm.org/) (GPL-3.0-or-later), so
the engine portion is a derivative work and must remain GPL-3.0-or-later.
Bundled/fetched third-party libraries keep their own (GPL-compatible) licenses:
apclientpp (MIT), nlohmann/json (MIT), websocketpp (BSD), asio (Boost), SDL2 (zlib).

The Archipelago world (`apworld/`) is provided here under the same license; if
upstreamed to Archipelago it would follow that project's contribution terms.

### Disclaimer

Not affiliated with, endorsed by, or associated with Electronic Arts, Westwood
Studios, the ScummVM project, or GOG. *The Legend of Kyrandia* is a trademark of
its respective owner. **You must own a legal copy of the game** — this project
ships no game assets and is a free, non-commercial, asset-free interop project.
