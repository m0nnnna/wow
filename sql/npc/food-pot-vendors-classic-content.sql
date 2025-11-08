USE acore_world;

-- RISTA IAS - POTS (ID 629612)
SET @E=629612, @N='Rista Ias', @S='Potion Peddler', @I='Buy', @L=80, @H=80, @F=35, @FL=128, @AI='SmartAI', @SCR='';

DELETE FROM creature_template WHERE entry=@E;

INSERT INTO creature_template (
`entry`,`difficulty_entry_1`,`difficulty_entry_2`,`difficulty_entry_3`,
`KillCredit1`,`KillCredit2`,`name`,`subname`,`IconName`,`gossip_menu_id`,
`minlevel`,`maxlevel`,`exp`,`faction`,`npcflag`,
`speed_walk`,`speed_run`,`speed_swim`,`speed_flight`,`detection_range`,`scale`,
`rank`,`dmgschool`,`DamageModifier`,`BaseAttackTime`,`RangeAttackTime`,
`BaseVariance`,`RangeVariance`,`unit_class`,`unit_flags`,`unit_flags2`,
`dynamicflags`,`family`,`trainer_type`,`trainer_spell`,`trainer_class`,`trainer_race`,
`type`,`type_flags`,`lootid`,`pickpocketloot`,`skinloot`,
`PetSpellDataId`,`VehicleId`,`mingold`,`maxgold`,
`AIName`,`MovementType`,`HoverHeight`,`HealthModifier`,`ManaModifier`,`ArmorModifier`,
`ExperienceModifier`,`RacialLeader`,`movementId`,`RegenHealth`,
`mechanic_immune_mask`,`spell_school_immune_mask`,`flags_extra`,
`ScriptName`,`VerifiedBuild`
) VALUES
(@E,0,0,0,0,0,@N,@S,@I,0,@L,@H,2,@F,@FL,
1,1.14286,1,1,18,1,
0,0,1.0,2000,2000,
1.0,1.0,1,2,2048,
0,0,0,0,0,0,
7,0,0,0,0,
0,0,0,0,
@AI,0,1,1,1,1,
1.0,0,0,1,
0,0,2,@SCR,12340);

DELETE FROM creature_equip_template WHERE CreatureID=@E AND ID=1;
INSERT INTO creature_equip_template (CreatureID,ID,ItemID1,ItemID2,ItemID3,VerifiedBuild)
VALUES (@E,1,19026,0,0,0);

DELETE FROM npc_vendor WHERE entry=@E;
INSERT INTO npc_vendor (entry,item,maxcount,incrtime,ExtendedCost,VerifiedBuild)
VALUES 
(@E,13510,0,0,0,0),(@E,13511,0,0,0,0),(@E,13512,0,0,0,0),(@E,13513,0,0,0,0),
(@E,13506,0,0,0,0),(@E,20079,0,0,0,0),(@E,20080,0,0,0,0),(@E,20081,0,0,0,0),
(@E,13452,0,0,0,0),(@E,20007,0,0,0,0),(@E,13445,0,0,0,0),(@E,12451,0,0,0,0),
(@E,12460,0,0,0,0),(@E,12457,0,0,0,0),(@E,12455,0,0,0,0),(@E,17708,0,0,0,0),
(@E,21546,0,0,0,0),(@E,9264,0,0,0,0),(@E,13454,0,0,0,0),(@E,13459,0,0,0,0),
(@E,13458,0,0,0,0),(@E,13456,0,0,0,0),(@E,13457,0,0,0,0),(@E,13461,0,0,0,0),
(@E,18253,0,0,0,0),(@E,3387,0,0,0,0),(@E,9030,0,0,0,0),(@E,5634,0,0,0,0);


-- HERIA BOL - FOOD (629613)
SET @E=629613, @N='Heria Bol', @S='Gourmet', @I='Buy', @L=80, @H=80, @F=35, @FL=128, @AI='SmartAI', @SCR='';

DELETE FROM creature_template WHERE entry=@E;

INSERT INTO creature_template (
`entry`,`difficulty_entry_1`,`difficulty_entry_2`,`difficulty_entry_3`,
`KillCredit1`,`KillCredit2`,`name`,`subname`,`IconName`,`gossip_menu_id`,
`minlevel`,`maxlevel`,`exp`,`faction`,`npcflag`,
`speed_walk`,`speed_run`,`speed_swim`,`speed_flight`,`detection_range`,`scale`,
`rank`,`dmgschool`,`DamageModifier`,`BaseAttackTime`,`RangeAttackTime`,
`BaseVariance`,`RangeVariance`,`unit_class`,`unit_flags`,`unit_flags2`,
`dynamicflags`,`family`,`trainer_type`,`trainer_spell`,`trainer_class`,`trainer_race`,
`type`,`type_flags`,`lootid`,`pickpocketloot`,`skinloot`,
`PetSpellDataId`,`VehicleId`,`mingold`,`maxgold`,
`AIName`,`MovementType`,`HoverHeight`,`HealthModifier`,`ManaModifier`,`ArmorModifier`,
`ExperienceModifier`,`RacialLeader`,`movementId`,`RegenHealth`,
`mechanic_immune_mask`,`spell_school_immune_mask`,`flags_extra`,
`ScriptName`,`VerifiedBuild`
) VALUES
(@E,0,0,0,0,0,@N,@S,@I,0,@L,@H,2,@F,@FL,
1,1.14286,1,1,18,1,
0,0,1.0,2000,2000,
1.0,1.0,1,2,2048,
0,0,0,0,0,0,
7,0,0,0,0,
0,0,0,0,
@AI,0,1,1,1,1,
1.0,0,0,1,
0,0,2,@SCR,12340);

DELETE FROM creature_equip_template WHERE CreatureID=@E AND ID=1;
INSERT INTO creature_equip_template (CreatureID,ID,ItemID1,ItemID2,ItemID3,VerifiedBuild)
VALUES (@E,1,20452,0,0,0);

DELETE FROM npc_vendor WHERE entry=@E;
INSERT INTO npc_vendor (entry,item,maxcount,incrtime,ExtendedCost,VerifiedBuild)
VALUES 
(@E,20452,0,0,0,0),(@E,13931,0,0,0,0),(@E,18254,0,0,0,0),(@E,21023,0,0,0,0),
(@E,13813,0,0,0,0),(@E,13810,0,0,0,0),(@E,20748,0,0,0,0),(@E,20749,0,0,0,0),
(@E,12404,0,0,0,0),(@E,16005,0,0,0,0),(@E,18262,0,0,0,0);

-- Add creature models for custom NPCs
DELETE FROM creature_template_model WHERE CreatureID IN (629612, 629613);

INSERT INTO creature_template_model 
(`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
VALUES
(629612, 0, 4162, 1, 1, 12340),
(629613, 0, 4162, 1, 1, 12340);
