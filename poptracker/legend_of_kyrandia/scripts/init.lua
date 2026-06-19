-- PopTracker entry point. Loaded automatically when the pack opens.

-- Data tables + logic providers first, so access rules / variable providers exist
-- before any layout references them.
ScriptHost:LoadScript("scripts/data.lua")
ScriptHost:LoadScript("scripts/logic.lua")

-- Register the pack's content with PopTracker. Without these calls nothing is
-- loaded and the tracker comes up empty.
Tracker:AddItems("items/items.json")
Tracker:AddMaps("maps/maps.json")
Tracker:AddLocations("locations/locations.json")
Tracker:AddLayouts("layouts/tracker.json")
Tracker:AddLayouts("layouts/broadcast.json")

-- Autotracking only matters for the AP variant, but registering the handlers is
-- harmless otherwise (they fire only on an active Archipelago connection).
ScriptHost:LoadScript("scripts/autotracking.lua")
