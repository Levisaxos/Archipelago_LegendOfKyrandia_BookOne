# tests/

Unit tests for the Kyrandia Book 1 apworld. Plain `unittest` (stdlib) — no
pytest or AP package install required.

## Run

```sh
# from the repo root
python -m unittest discover -s tests -p "test_*.py" -v
```

## What's covered

**`test_data_invariants.py`** — static checks on `apworld/kyrandia/data.py`.
No Archipelago install needed. Asserts:
- item / location IDs are unique,
- every region referenced by an edge/location exists,
- **every item named in a rule is progression or event** (the reachability
  invariant — `useful`/`filler` items never advance the sweep),
- the fixed item pool fits the location count,
- all regions are reachable from Menu with the full item set.

**`test_generation_beatable.py`** — end-to-end. For each of several seeds it:
1. rebuilds + installs `kyrandia.apworld`, then runs `ArchipelagoGenerate.exe`,
2. parses the spoiler's item placements,
3. runs an **independent logic sweep** over `data.py` (in `_helpers.sweep_beatable`)
   and asserts the `Victory` event is collectable and **all 64 locations are
   reachable**,
4. sanity-checks that AP's own playthrough also records the Malcolm/Victory event.

The sweep does NOT trust AP's playthrough section — it re-derives reachability
from our region graph against the actual placements, so a logic regression
(e.g. an unreachable check or an unwinnable seed) fails the test.

## Notes
- The generation test auto-**skips** if no Archipelago install is found. It looks
  at `$AP_ROOT`, then `C:\Program Files\Archipelago` (and a couple of fallbacks).
- It installs the apworld into `<AP>\custom_worlds\`; if that path isn't
  writable it skips with a message.
- `ArchipelagoGenerate.exe` is invoked with stdin = DEVNULL so its
  "Press enter to close" error prompt can't hang the run; stdout/stderr are
  captured and surfaced in the failure message.
