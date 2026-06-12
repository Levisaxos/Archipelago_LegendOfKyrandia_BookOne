## Licensing & Legal Notices

### Obligations we MUST meet
- **Fork is GPL-3.0-or-later.** ScummVM is GPLv3+, so our distributed build is a
  derivative work. The whole thing must be GPLv3+, we must publish complete
  corresponding source, and we must preserve all upstream copyright/license
  notices. No closed-source engine changes.
- **Ship NO game content.** Never distribute Kyrandia data files (.PAK, scripts,
  audio, art) or anything derived from them. The user supplies their own
  GOG-purchased copy. Our distribution = engine fork + our code only.
- **Keep third-party license notices.** Bundle the license texts for every
  dependency we ship (see below).

### Dependency licenses (all compatible with GPLv3)
| Component | License | Notes |
|-----------|---------|-------|
| ScummVM | GPL-3.0-or-later | copyleft — governs the whole distributable |
| apclientpp | MIT (© 2021 black-sliver) | retain MIT notice |
| nlohmann/json | MIT | |
| websocketpp | BSD | |
| asio | Boost Software License | |
| valijson | BSD | |
| OpenSSL | use 3.x (Apache-2.0, GPLv3-compatible) | avoid 1.x — historical GPL incompatibility |
| kyra.dat | GPL (ships with ScummVM) | redistribute only what upstream ScummVM ships; don't extend it |

### Naming / trademark
- **Do not present the build as "ScummVM."** Rename our fork; ScummVM is
  protective of its name/logo and has a strict no-piracy stance.
- **Do not use Westwood/EA/Kyrandia branding or logos** in a way implying
  endorsement.
- Use a descriptive project name + disclaimer, e.g.:
  > "Not affiliated with, endorsed by, or associated with Electronic Arts,
  > Westwood Studios, the ScummVM project, or GOG. The Legend of Kyrandia is a
  > trademark of its respective owner. You must own a legal copy of the game."

### DRM
- GOG is DRM-free → no anti-circumvention (DMCA §1201 / EU) concern. Targeting the
  GOG version specifically keeps us clear here; do not add support that requires
  bypassing DRM on any other edition.

### Archipelago (Python world)
- The AP world enters the Archipelago ecosystem under AP's own license /
  contribution terms — review those before upstreaming. Keep game content out of
  the world: only IDs, names, and logic.

### Risk posture
- Keep the project **free and non-commercial.** Don't sell it; don't bundle game
  files. This is the normal "asset-free, open-source interop mod" space — low
  practical risk, but mods remain a grey area a rights-holder could object to.

> Not legal advice — verify before public release.