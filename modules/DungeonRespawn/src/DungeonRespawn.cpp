#include "DungeonRespawn.h"
#include <sstream>  // For ostringstream
#include "Util.h"   // For getMSTime()

bool DSPlayerScript::IsInsideDungeonRaid(Player* player)
{
    if (!player)
    {
        return false;
    }

    Map* map = player->GetMap();
    if (!map)
    {
        return false;
    }

    if (!map->IsDungeon() && !map->IsRaid())
    {
        return false;
    }

    return true;
}

bool DSPlayerScript::DelayedRespawn::Execute(uint64 /*execTime*/, uint32 /*diff*/)
{
    Player* player = ObjectAccessor::FindConnectedPlayer(m_guid);
    if (!player)
    {
        return true;
    }

    uint32 startTime = getMSTime();  // Optional: Log timing
    player->TeleportTo(m_mapid, m_x, m_y, m_z, m_o);
    player->SetHealth(uint32(player->GetMaxHealth() * (m_hpPct / 100.0f)));

    std::ostringstream oss;
    oss << "|cffff0000[DungeonRespawn]|r Respawned at the dungeon entrance with " << static_cast<int>(m_hpPct) << "% HP.";
    player->SendSystemMessage(oss.str().c_str());

    LOG_INFO("module", "DungeonRespawn: Teleported %s in %ums", player->GetName().c_str(), getMSTime() - startTime);  // Optional timing log

    return true;
}

void DSPlayerScript::OnPlayerReleasedGhost(Player* player)
{
    if (!drEnabled)
    {
        return;
    }

    if (!IsInsideDungeonRaid(player))
    {
        return;
    }

    PlayerRespawnData* prData = GetOrCreateRespawnData(player);
    if (!prData || prData->dungeon.map == 0)
    {
        return;
    }

    // Near-instant: 0ms delay (fires right after GY spawn)
    player->m_Events.AddEvent(new DelayedRespawn(player->GetGUID(), prData->dungeon.map, prData->dungeon.x,
                                                  prData->dungeon.y, prData->dungeon.z, prData->dungeon.o, respawnHpPct),
                              getMSTime() + 0);
}

bool DSPlayerScript::OnPlayerBeforeTeleport(Player* player, uint32 mapid, float /*x*/, float /*y*/, float /*z*/, float /*orientation*/, uint32 /*options*/, Unit* /*target*/)
{
    if (!drEnabled)
    {
        return true;
    }

    if (!player)
    {
        return true;
    }

    if (player->GetMapId() != mapid)
    {
        auto prData = GetOrCreateRespawnData(player);
        prData->isTeleportingNewMap = true;
    }

    return true;
}

void DSWorldScript::OnAfterConfigLoad(bool reload)
{
    if (reload)
    {
        SaveRespawnData();
        respawnData.clear();
    }

    drEnabled = sConfigMgr->GetOption<bool>("DungeonRespawn.Enable", false);
    respawnHpPct = sConfigMgr->GetOption<float>("DungeonRespawn.RespawnHealthPct", 50.0f);

    QueryResult qResult = CharacterDatabase.Query("SELECT `guid`, `map`, `x`, `y`, `z`, `o` FROM `dungeonrespawn_playerinfo`");

    if (qResult)
    {
        uint32 dataCount = 0;

        do
        {
            Field* fields = qResult->Fetch();

            PlayerRespawnData prData;
            DungeonData dData;
            prData.guid = ObjectGuid(fields[0].Get<uint64>());
            dData.map = fields[1].Get<uint32>();
            dData.x = fields[2].Get<float>();
            dData.y = fields[3].Get<float>();
            dData.z = fields[4].Get<float>();
            dData.o = fields[5].Get<float>();
            prData.dungeon = dData;
            prData.isTeleportingNewMap = false;
            prData.inDungeon = false;

            respawnData.push_back(prData);

            dataCount++;
        } while (qResult->NextRow());

        LOG_INFO("module", "Loaded %u rows from 'dungeonrespawn_playerinfo' table.", dataCount);
    }
    else
    {
        LOG_INFO("module", "Loaded 0 rows from 'dungeonrespawn_playerinfo' table.");
    }
}

void DSWorldScript::OnShutdown()
{
    SaveRespawnData();
}

void DSWorldScript::SaveRespawnData()
{
    for (const auto& prData : respawnData)
    {
        if (prData.inDungeon)
        {
            CharacterDatabase.Execute("INSERT INTO `dungeonrespawn_playerinfo` (guid, map, x, y, z, o) VALUES (%u, %u, %f, %f, %f, %f) ON DUPLICATE KEY UPDATE map=%u, x=%f, y=%f, z=%f, o=%f",
                prData.guid.GetRawValue(),
                prData.dungeon.map,
                prData.dungeon.x,
                prData.dungeon.y,
                prData.dungeon.z,
                prData.dungeon.o,
                prData.dungeon.map,
                prData.dungeon.x,
                prData.dungeon.y,
                prData.dungeon.z,
                prData.dungeon.o);
        }
        else
        {
            CharacterDatabase.Execute("DELETE FROM `dungeonrespawn_playerinfo` WHERE guid = %u", prData.guid.GetRawValue());
        }
    }
}

PlayerRespawnData* DSPlayerScript::GetOrCreateRespawnData(Player* player)
{
    for (auto it = respawnData.begin(); it != respawnData.end(); ++it)
    {
        if (player->GetGUID() == it->guid)
        {
            return &(*it);
        }
    }

    CreateRespawnData(player);
    return GetOrCreateRespawnData(player);
}

void DSPlayerScript::OnPlayerMapChanged(Player* player)
{
    if (!player)
    {
        return;
    }

    auto prData = GetOrCreateRespawnData(player);
    if (!prData)
    {
        return;
    }

    bool inDungeon = IsInsideDungeonRaid(player);
    prData->inDungeon = inDungeon;

    if (!inDungeon)
    {
        return;
    }

    if (!prData->isTeleportingNewMap)
    {
        return;
    }

    prData->dungeon.map = player->GetMapId();
    prData->dungeon.x = player->GetPositionX();
    prData->dungeon.y = player->GetPositionY();
    prData->dungeon.z = player->GetPositionZ();
    prData->dungeon.o = player->GetOrientation();

    prData->isTeleportingNewMap = false;
}

void DSPlayerScript::CreateRespawnData(Player* player)
{
    DungeonData newDData;
    newDData.map = 0;  // Invalid marker
    newDData.x = 0;
    newDData.y = 0;
    newDData.z = 0;
    newDData.o = 0;

    PlayerRespawnData newPrData;
    newPrData.dungeon = newDData;
    newPrData.guid = player->GetGUID();
    newPrData.isTeleportingNewMap = false;
    newPrData.inDungeon = false;
    
    respawnData.push_back(newPrData);
}

void DSPlayerScript::OnPlayerLogin(Player* player)
{
    if (!player)
    {
        return;
    }

    GetOrCreateRespawnData(player);
}

void DSPlayerScript::OnPlayerLogout(Player* player)
{
    // No-op: Removed old playersToTeleport logic
}

void SC_AddDungeonRespawnScripts()
{
    new DSWorldScript();
    new DSPlayerScript();
}