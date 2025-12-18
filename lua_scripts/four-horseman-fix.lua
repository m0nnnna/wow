-- Four Horsemen Solo-Friendly Script for Eluna (AzerothCore)
-- This script makes the bosses aggroable one at a time instead of all linking

-- Boss Entry IDs
local THANE_KORTHAZZ = 16064
local LADY_BLAUMEUX = 16065
local SIR_ZELIEK = 16063
local BARON_RIVENDARE = 30549  -- Use 16060 if using the original 40-man version

-- Table to track which bosses are in combat
local bossesInCombat = {}

-- Helper function to check if any horseman is in combat
local function IsAnyHorsemanInCombat()
    for _, inCombat in pairs(bossesInCombat) do
        if inCombat then
            return true
        end
    end
    return false
end

-- Helper function to make a boss evade if another is in combat
local function CheckAndEvade(creature)
    local entry = creature:GetEntry()
    
    -- Check if this boss is trying to enter combat while another is already fighting
    if not bossesInCombat[entry] and IsAnyHorsemanInCombat() then
        creature:SetReactState(0)  -- Set to passive
        creature:CombatStop(true)
        creature:DeleteThreatList()
        creature:SetHomePosition(creature:GetX(), creature:GetY(), creature:GetZ(), creature:GetO())
        creature:GetAI():EnterEvadeMode()
        return true
    end
    return false
end

-- OnEnterCombat event for all Four Horsemen
local function OnEnterCombat(event, creature, target)
    local entry = creature:GetEntry()
    
    -- If another boss is already in combat, evade
    if CheckAndEvade(creature) then
        return
    end
    
    -- Mark this boss as in combat
    bossesInCombat[entry] = true
    
    -- Set all other horsemen to passive so they don't aggro
    local nearbyCreatures = creature:GetCreaturesInRange(150, entry == THANE_KORTHAZZ and LADY_BLAUMEUX or 
                                                               entry == LADY_BLAUMEUX and SIR_ZELIEK or 
                                                               entry == SIR_ZELIEK and BARON_RIVENDARE or 
                                                               THANE_KORTHAZZ)
    
    -- Make all other horsemen passive
    local allEntries = {THANE_KORTHAZZ, LADY_BLAUMEUX, SIR_ZELIEK, BARON_RIVENDARE}
    for _, otherEntry in ipairs(allEntries) do
        if otherEntry ~= entry then
            local others = creature:GetCreaturesInRange(150, otherEntry)
            for _, other in ipairs(others) do
                if not other:IsInCombat() then
                    other:SetReactState(0)  -- Passive
                end
            end
        end
    end
end

-- OnLeaveCombat event (reset)
local function OnLeaveCombat(event, creature)
    local entry = creature:GetEntry()
    bossesInCombat[entry] = false
    
    -- If no horsemen are in combat, reset all to aggressive
    if not IsAnyHorsemanInCombat() then
        local allEntries = {THANE_KORTHAZZ, LADY_BLAUMEUX, SIR_ZELIEK, BARON_RIVENDARE}
        for _, bossEntry in ipairs(allEntries) do
            local bosses = creature:GetCreaturesInRange(150, bossEntry)
            for _, boss in ipairs(bosses) do
                boss:SetReactState(1)  -- Aggressive
            end
        end
    end
end

-- OnDied event (allow next boss to be attacked)
local function OnDied(event, creature, killer)
    local entry = creature:GetEntry()
    bossesInCombat[entry] = false
    
    -- Re-enable all remaining horsemen
    if not IsAnyHorsemanInCombat() then
        local allEntries = {THANE_KORTHAZZ, LADY_BLAUMEUX, SIR_ZELIEK, BARON_RIVENDARE}
        for _, bossEntry in ipairs(allEntries) do
            local bosses = creature:GetCreaturesInRange(150, bossEntry)
            for _, boss in ipairs(bosses) do
                boss:SetReactState(1)  -- Aggressive
            end
        end
    end
end

-- Register events for all Four Horsemen
RegisterCreatureEvent(THANE_KORTHAZZ, 1, OnEnterCombat)
RegisterCreatureEvent(THANE_KORTHAZZ, 2, OnLeaveCombat)
RegisterCreatureEvent(THANE_KORTHAZZ, 4, OnDied)

RegisterCreatureEvent(LADY_BLAUMEUX, 1, OnEnterCombat)
RegisterCreatureEvent(LADY_BLAUMEUX, 2, OnLeaveCombat)
RegisterCreatureEvent(LADY_BLAUMEUX, 4, OnDied)

RegisterCreatureEvent(SIR_ZELIEK, 1, OnEnterCombat)
RegisterCreatureEvent(SIR_ZELIEK, 2, OnLeaveCombat)
RegisterCreatureEvent(SIR_ZELIEK, 4, OnDied)

RegisterCreatureEvent(BARON_RIVENDARE, 1, OnEnterCombat)
RegisterCreatureEvent(BARON_RIVENDARE, 2, OnLeaveCombat)
RegisterCreatureEvent(BARON_RIVENDARE, 4, OnDied)

print(">> Four Horsemen Solo Script loaded successfully!")