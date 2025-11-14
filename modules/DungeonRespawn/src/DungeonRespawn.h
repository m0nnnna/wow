#ifndef MODULE_DUNGEONRESPAWN_H
#define MODULE_DUNGEONRESPAWN_H

#include "ScriptMgr.h"
#include "LFGMgr.h"
#include "Player.h"
#include "Config.h"
#include "Chat.h"
#include "ObjectAccessor.h"
#include "EventProcessor.h"
#include <vector>
#include <sstream>

struct DungeonData
{
    uint32 map;
    float x;
    float y;
    float z;
    float o;
};

struct PlayerRespawnData
{
    ObjectGuid guid;
    DungeonData dungeon;
    bool isTeleportingNewMap;
    bool inDungeon;
};

std::vector<PlayerRespawnData> respawnData;

bool drEnabled;
float respawnHpPct;

class DSPlayerScript : public PlayerScript
{
public:
    DSPlayerScript() : PlayerScript("DSPlayerScript") { }

private:
    bool IsInsideDungeonRaid(Player* player);
    PlayerRespawnData* GetOrCreateRespawnData(Player* player);
    void CreateRespawnData(Player* player);
    void OnPlayerReleasedGhost(Player* player) override;
    bool OnPlayerBeforeTeleport(Player* player, uint32 mapid, float x, float y, float z, float orientation, uint32 options, Unit* target) override;
    void OnPlayerMapChanged(Player* player) override;
    void OnPlayerLogin(Player* player) override;
    void OnPlayerLogout(Player* player) override;

    struct DelayedRespawn : public BasicEvent
    {
        DelayedRespawn(ObjectGuid guid, uint32 mapid, float x, float y, float z, float o, float hpPct)
            : m_guid(guid), m_mapid(mapid), m_x(x), m_y(y), m_z(z), m_o(o), m_hpPct(hpPct) {}

        ~DelayedRespawn() override = default;

        bool Execute(uint64 /*execTime*/, uint32 /*diff*/) override;

        ObjectGuid m_guid;
        uint32 m_mapid;
        float m_x, m_y, m_z, m_o;
        float m_hpPct;
    };
};

class DSWorldScript : public WorldScript
{
public:
    DSWorldScript() : WorldScript("DSWorldScript") { }

private:
    void OnAfterConfigLoad(bool reload) override;
    void OnShutdown() override;
    void SaveRespawnData();
};

#endif //MODULE_DUNGEONRESPAWN_H