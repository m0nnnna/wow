# mod-xp-changer

An AzerothCore module that lets players adjust their personal XP rate via an in-game NPC.

## Features

- Per-player XP rate that persists across sessions
- Rates are applied to all XP sources (kills, quests, etc.)
- Rate is saved to the character database on change and restored on login

## XP Rates

| Option | Multiplier |
|--------|-----------|
| Slowpoke | 0.2x (20%) |
| Taking it easy | 0.5x (50%) |
| Steady pace | 0.7x (70%) |
| Normal rate | 1.0x |
| Fast learner | 1.5x (150%) |
| Speed run | 2.0x (200%) |

## Installation

1. Copy the module folder into your AzerothCore `modules/` directory.
2. Re-run CMake and rebuild the server.
3. Apply the SQL files:
   - `sql/world/base/xp_changer_npc.sql` → world database
   - `sql/characters/base/xp_rate_table.sql` → characters database
4. Spawn the NPC (entry `629100`) somewhere in the world, or use `.npc add 629100` in-game.

## NPC

The **XP Guide** (entry `629100`) is a level 80 gossip NPC. Talk to it to see your current rate and select a new one.
