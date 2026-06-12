# Legend of Kyrandia (Book 1) Setup Guide — DRAFT

> **Status: pre-alpha.** This apworld generates valid Archipelago seeds for
> testing, but the **game client does not exist yet** — the forked ScummVM engine
> that talks to Archipelago is still in development (see the project roadmap).
> There is nothing playable to connect to a server at this stage. This guide
> covers generating/inspecting seeds and tracking them.

## What works today
- The apworld loads in Archipelago and generates a single- or multi-world seed.
- Logic is a **first-pass draft** (item randomizer scope) and needs verification
  against a real playthrough.

## Installing the apworld
1. Copy `kyrandia.apworld` into your Archipelago `custom_worlds/` folder
   (this build: `C:\Program Files\Archipelago\custom_worlds\`).
2. Restart the Archipelago Launcher.

## Generating a test seed
1. Create a YAML for the game **The Legend of Kyrandia - Book 1** (the Options
   page / `ArchipelagoOptionsCreator` will list it once the apworld is installed).
2. Run **Generate**.
3. Inspect the spoiler log to confirm placement and reachability.

## Options
- **Goal** — `kyragem_ending` (place Crown + Sceptre + Royal Chalice). Only goal in V1.
- **Start With Amulet** — start holding the Amulet (loosens logic; useful for testing).
- **Death Link** — standard AP death link toggle (no client effect yet).

## Universal Tracker
This world ships with UT support (`interpret_slot_data` + re-gen passthrough), so
once connected, Universal Tracker can reconstruct the logic and show reachable
checks. Until the game client exists, use the Text Client + UT to exercise the
logic.
