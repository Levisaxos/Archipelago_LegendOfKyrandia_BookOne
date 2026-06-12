-- Archipelago autotracking: marks received items and checked locations.
-- Mapping tables (ITEM_MAPPING / LOCATION_MAPPING) live in scripts/data.lua.
-- Only fires when connected to an AP server with the "ap" variant.

local function onClear(slot_data)
  -- Reset tracked items so a fresh connection starts clean.
  for _, m in pairs(ITEM_MAPPING) do
    local o = Tracker:FindObjectForCode(m[1][1])
    if o then
      if m[2] == "toggle" then
        o.Active = false
      elseif m[2] == "consumable" then
        o.AcquiredCount = 0
      end
    end
  end
  -- Reflect the start_with_amulet slot option.
  local amu = Tracker:FindObjectForCode("opt_start_amulet")
  if amu then
    local v = slot_data and slot_data["start_with_amulet"]
    amu.Active = (v ~= nil and v ~= 0 and v ~= false)
  end
end

local function onItem(index, item_id, item_name, player_number)
  local m = ITEM_MAPPING[item_id]
  if not m then return end
  local o = Tracker:FindObjectForCode(m[1][1])
  if not o then return end
  if m[2] == "toggle" then
    o.Active = true
  elseif m[2] == "consumable" then
    o.AcquiredCount = o.AcquiredCount + 1
  end
end

local function onLocation(location_id, location_name)
  local path = LOCATION_MAPPING[location_id]
  if not path then return end
  local o = Tracker:FindObjectForCode(path)
  if o then
    o.AvailableChestCount = 0
  end
end

Archipelago:AddClearHandler("kyra clear", onClear)
Archipelago:AddItemHandler("kyra item", onItem)
Archipelago:AddLocationHandler("kyra location", onLocation)
