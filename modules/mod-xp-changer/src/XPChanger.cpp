/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license
 */

#include "ScriptMgr.h"
#include "Player.h"
#include "Chat.h"
#include "GossipDef.h"
#include "ScriptedGossip.h"
#include "DatabaseEnv.h"
#include <unordered_map>

static std::unordered_map<uint32, float> playerXPRates;

enum XPRateAction
{
    XP_ACTION_02 = 1,
    XP_ACTION_05 = 2,
    XP_ACTION_07 = 3,
    XP_ACTION_10 = 4,
    XP_ACTION_15 = 5,
    XP_ACTION_20 = 6,
};

class XPChangerNPC : public CreatureScript
{
public:
    XPChangerNPC() : CreatureScript("npc_xp_changer") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        player->PlayerTalkClass->ClearMenus();

        float currentRate = 1.0f;
        auto it = playerXPRates.find(player->GetGUID().GetCounter());
        if (it != playerXPRates.end())
            currentRate = it->second;

        ChatHandler(player->GetSession()).PSendSysMessage("Your current XP rate: %.1fx", currentRate);

        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "0.2x - Slowpoke (20%)",        GOSSIP_SENDER_MAIN, XP_ACTION_02);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "0.5x - Taking it easy (50%)",  GOSSIP_SENDER_MAIN, XP_ACTION_05);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "0.7x - Steady pace (70%)",     GOSSIP_SENDER_MAIN, XP_ACTION_07);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "1.0x - Normal rate",           GOSSIP_SENDER_MAIN, XP_ACTION_10);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "1.5x - Fast learner (150%)",   GOSSIP_SENDER_MAIN, XP_ACTION_15);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "2.0x - Speed run (200%)",      GOSSIP_SENDER_MAIN, XP_ACTION_20);

        SendGossipMenuFor(player, 68, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* /*creature*/, uint32 /*sender*/, uint32 action) override
    {
        CloseGossipMenuFor(player);

        float rate;
        const char* rateName;

        switch (action)
        {
            case XP_ACTION_02: rate = 0.2f; rateName = "0.2x (20%)";    break;
            case XP_ACTION_05: rate = 0.5f; rateName = "0.5x (50%)";    break;
            case XP_ACTION_07: rate = 0.7f; rateName = "0.7x (70%)";    break;
            case XP_ACTION_10: rate = 1.0f; rateName = "1.0x (Normal)"; break;
            case XP_ACTION_15: rate = 1.5f; rateName = "1.5x (150%)";   break;
            case XP_ACTION_20: rate = 2.0f; rateName = "2.0x (200%)";   break;
            default: return true;
        }

        uint32 guid = player->GetGUID().GetCounter();
        playerXPRates[guid] = rate;

        CharacterDatabase.Execute("REPLACE INTO character_xp_rate (guid, rate) VALUES ({}, {})", guid, rate);

        ChatHandler(player->GetSession()).PSendSysMessage("XP rate set to %s.", rateName);
        return true;
    }
};

class XPChangerPlayerScript : public PlayerScript
{
public:
    XPChangerPlayerScript() : PlayerScript("XPChangerPlayerScript") { }

    void OnPlayerLogin(Player* player) override
    {
        uint32 guid = player->GetGUID().GetCounter();
        QueryResult result = CharacterDatabase.Query("SELECT rate FROM character_xp_rate WHERE guid = {}", guid);
        if (result)
        {
            Field* fields = result->Fetch();
            playerXPRates[guid] = fields[0].Get<float>();
        }
    }

    void OnPlayerLogout(Player* player) override
    {
        playerXPRates.erase(player->GetGUID().GetCounter());
    }

    void OnPlayerGiveXP(Player* player, uint32& amount, Unit* /*victim*/, uint8 /*xpSource*/) override
    {
        auto it = playerXPRates.find(player->GetGUID().GetCounter());
        if (it != playerXPRates.end())
            amount = uint32(float(amount) * it->second);
    }
};

void AddXPChangerScripts()
{
    new XPChangerNPC();
    new XPChangerPlayerScript();
}
