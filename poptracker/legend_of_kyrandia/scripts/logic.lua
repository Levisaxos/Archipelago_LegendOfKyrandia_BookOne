-- Kyrandia Book 1 logic: a fixpoint reachability sweep that mirrors the
-- Archipelago apworld (apworld/kyrandia/data.py). See scripts/data.lua for the
-- generated tables.
--
-- Every PopTracker access rule for a location is "^$kyra_loc|<ap_id>", which
-- returns an AccessibilityLevel directly. Powers/goal use "^$kyra_event|<name>"
-- and "^$kyra_goal".

local KYRA_STATE = nil
local KYRA_SIG = nil

local function has_all(have, reqs)
  for _, r in ipairs(reqs) do
    if not have[r] then return false end
  end
  return true
end

-- Cheap signature of the relevant provider counts so we only recompute the
-- fixpoint when the held-item set actually changes.
local function signature()
  local parts = {}
  for _, c in pairs(KYRANDIA.item_code) do
    parts[#parts + 1] = c .. (Tracker:ProviderCountForCode(c) > 0 and "1" or "0")
  end
  parts[#parts + 1] = "amu" .. (Tracker:ProviderCountForCode("opt_start_amulet") > 0 and "1" or "0")
  table.sort(parts)
  return table.concat(parts, "|")
end

local function compute()
  -- Held items (received / toggled).
  local have = {}
  for name, c in pairs(KYRANDIA.item_code) do
    if Tracker:ProviderCountForCode(c) > 0 then have[name] = true end
  end
  -- start_with_amulet slot option behaves as if the Amulet is already held.
  if Tracker:ProviderCountForCode("opt_start_amulet") > 0 then
    have["Amulet"] = true
  end

  -- Fixpoint: expand reachable regions through gated edges, then earn any
  -- event item (the 4 spells + Victory) whose region is reachable and whose
  -- item requirements are met. Repeat until nothing new appears.
  local regions = { [KYRANDIA.start] = true }
  local changed = true
  while changed do
    changed = false
    for _, e in ipairs(KYRANDIA.edges) do
      if regions[e.from] and not regions[e.to] and has_all(have, e.req) then
        regions[e.to] = true
        changed = true
      end
    end
    for _, ev in ipairs(KYRANDIA.events) do
      if regions[ev.region] and not have[ev.grants] and has_all(have, ev.req) then
        have[ev.grants] = true
        changed = true
      end
    end
  end

  return { regions = regions, have = have }
end

local function state()
  local s = signature()
  if s ~= KYRA_SIG then
    KYRA_SIG = s
    KYRA_STATE = compute()
  end
  return KYRA_STATE
end

-- Access rule for a real (networked) location.
function kyra_loc(id)
  local st = state()
  local loc = KYRANDIA.loc_by_id[tonumber(id)]
  if not loc then return AccessibilityLevel.None end
  if st.regions[loc.region] and has_all(st.have, loc.req) then
    return AccessibilityLevel.Normal
  end
  return AccessibilityLevel.None
end

-- Informational: a derived spell power is "reachable" once it is in logic.
function kyra_event(name)
  local st = state()
  if st.have[name] then return AccessibilityLevel.Normal end
  return AccessibilityLevel.None
end

-- Informational: the win condition.
function kyra_goal()
  local st = state()
  if st.have["Victory"] then return AccessibilityLevel.Normal end
  return AccessibilityLevel.None
end
