# pyscripts/

Python tooling for extraction and data generation. Scripts resolve paths
relative to the repo root, so run them from anywhere:

```
python pyscripts/build_item_crosswalk.py
```

| Script | What it does |
|--------|--------------|
| `build_item_crosswalk.py` | Reads `research/kyra1_item_ids.txt` and writes `research/kyra1_items.json` — the engine-ID ↔ AP-ID item crosswalk. Edit the `M` mapping dict and re-run to refine. |
