-- PopTracker entry point. Loaded automatically when the pack opens.
ScriptHost:LoadScript("scripts/data.lua")
ScriptHost:LoadScript("scripts/logic.lua")

-- Autotracking only matters for the AP variant, but registering the handlers is
-- harmless otherwise (they fire only on an active Archipelago connection).
ScriptHost:LoadScript("scripts/autotracking.lua")
