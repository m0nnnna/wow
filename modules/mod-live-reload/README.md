# mod-live-reload

## Description

Adds a suite of `.rlive` GM commands that reload world database tables into the running worldserver without a restart. Covers every major system — vendor inventories, item prices, creature templates, boss spell slots, loot tables, smart scripts, gossip menus, spawn pools, and more.

Also includes Python tooling (`tools/`) for applying SQL files and triggering reloads automatically via SOAP from outside the game.

## The problem this solves

AzerothCore loads world data into memory at startup. Normally, any edit to the database — changing an NPC's vendor list, adjusting item prices, tweaking a creature's stats — requires a full worldserver restart to take effect. On a live server this means kicking all players.

This module hot-reloads that data in place. Most changes are visible to players within seconds of the command being run.

## In-game commands

All commands require `SEC_ADMINISTRATOR` (GM level 3) and work from both the worldserver console and in-game chat.

| Command | What it reloads | Notes |
|---|---|---|
| `.rlive vendor [entry]` | `npc_vendor` | Visible on next vendor window open |
| `.rlive trainer` | `npc_trainer` | |
| `.rlive item` | `item_template` | Prices, stats, flags |
| `.rlive quest` | `quest_template` + relations | |
| `.rlive creature <entry>` | `creature_template` (single entry) | Respawns all live instances in 3s |
| `.rlive gobject <entry>` | `gameobject_template` (full table) | Respawns live instances of entry |
| `.rlive script` | `smart_scripts` | Picks up on next AI event |
| `.rlive gossip` | `gossip_menu` + `gossip_menu_option` + conditions | |
| `.rlive loot <type>` | Any loot table | Types: `creature` `fishing` `gameobject` `skinning` `pickpocketing` `mail` `disenchant` `prospecting` `milling` |
| `.rlive pool` | `pool_template` | |
| `.rlive condition` | `conditions` | |
| `.rlive access` | `access_requirement` | Dungeon/raid entry requirements |
| `.rlive spell` | All SpellMgr modifier tables | `spell_bonus_data`, `spell_linked_spell`, `spell_proc`, `spell_threats`, `spell_group`, `spell_area`, `spell_pet_auras`, `spell_required` |
| `.rlive spells <entry>` | `creature_template_spell` (single entry) | **Hot-patches live instances in memory — no despawn, safe during combat** |
| `.rlive all` | Everything above | Does not force respawns |

### Boss spell hot-patching

`.rlive spells <entry>` is the standout command for raid content. After changing which spells a boss casts in `creature_template_spell`, this command reloads those slots and patches them directly onto every currently live instance of that creature — with no despawn and no AI reset. The boss stays alive and in combat, and will use the updated spells from its next cast cycle onward.

This does **not** affect spells hardcoded in C++ boss scripts. Those require a recompile.

## Installation

```
1) Clone or copy this module into the modules/ directory of your AzerothCore source.
2) Re-run cmake and rebuild the worldserver.
3) Enable SOAP in worldserver.conf (required for the Python tools — not required for console use):
       SOAP.Enabled = 1
       SOAP.IP      = 127.0.0.1
       SOAP.Port    = 7878
4) Launch the worldserver. Look for "mod_live_reload_commandscript" in the startup log.
5) Test from the console:  .rlive vendor
```

No SQL imports required. No config file required.

## Python tools (`tools/`)

Optional automation layer that sits outside the game. Useful when editing the DB directly via HeidiSQL, DBeaver, or Keira and you want reloads to fire automatically.

### Setup

```bash
pip install mysql-connector-python watchdog
cp tools/config.example.json tools/config.json
# Edit config.json with your MySQL credentials and SOAP GM account
```

### watch.py — auto-apply and reload

```bash
python tools/watch.py
```

Watches the `sql/` folder. Drop any `.sql` file in and it will:
1. Execute the SQL against the world database
2. Detect which tables were modified
3. Send the matching `.rlive` command via SOAP
4. Move the file to `sql/done/`

### reload.py — manual trigger

```bash
python tools/reload.py npc_vendor
python tools/reload.py item_template
python tools/reload.py all
python tools/reload.py ".rlive spells 12345"   # raw command
```

### config.example.json

Copy to `config.json` and fill in your values:

```json
{
  "soap": {
    "host": "127.0.0.1",
    "port": 7878,
    "username": "your_gm_account",
    "password": "your_gm_password"
  },
  "mysql": {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "your_mysql_password",
    "database": "acore_world"
  }
}
```

## Requirements

- AzerothCore 3.3.5a (wotlk branch)
- C++17 or later
- Python 3.8+ (tools only)
- `mysql-connector-python`, `watchdog` (tools only, install via pip)

## Credits

- Built for a custom private server running AzerothCore with mod-individual-progression
