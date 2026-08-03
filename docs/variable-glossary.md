# Variable glossary (renames)

Maps the original cryptic Scratch names to the readable names now in
`extracted-sb3-file/project.json`. Renames are applied strictly by **(owner, id)** with
`tools/rename_vars.py`, so behaviour is unchanged — only readability. This file is generated
from `tools/rename_map.json` by `tools/gen_glossary.py`; don't edit it by hand.

Conventions: the original used a leading `_` to mark engine-internal state; new names are
plain readable camelCase. Already-clear names (e.g. `Hardcore`, `XP_LEVEL`, `Beacon`) and
conventional loop counters (`i`, `x`, `y`, `t`) are intentionally left unchanged.


**200 names renamed so far**, across 6 target(s).


## Stage (global state) — 110 renamed

| old | new |
|-----|-----|
| `_ArmFrame` | `armFrame` |
| `_DamageArmor` | `armorDamage` |
| `attack_cooldown` | `attackCooldown` |
| `_BACKGROUND` | `backgroundId` |
| `_BiomeID` | `biomeId` |
| `_Biome_Tints` | `biomeTints` |
| `_DMUL` | `blockDataStride` |
| `broadcast#` | `broadcastNumber` |
| `_ScrX` | `cameraX` |
| `_ScrY` | `cameraY` |
| `canclick?` | `canClick` |
| `charge attack time` | `chargeAttackTime` |
| `charge attack for spear?` | `chargingSpearAttack` |
| `chosen-option` | `chosenOption` |
| `_CHUNK_SEED` | `chunkSeed` |
| `_ClearHarvestIdx` | `clearHarvestIndex` |
| `_Creative Indent` | `creativeIndent` |
| `_CurrentVillagerTrade` | `currentVillagerTrade` |
| `_Cursor` | `cursorId` |
| `day-night-time` | `dayNightTime` |
| `_Death Location` | `deathLocation` |
| `_Death Seed` | `deathSeed` |
| `_DefenseMul` | `defenseMultiplier` |
| `_DragSrcID` | `dragSourceId` |
| `DragonHealth` | `dragonHealth` |
| `_amplifier` | `effectAmplifier` |
| `_effect` | `effectId` |
| `elapsed time` | `elapsedTime` |
| `EndpY` | `endPortalY` |
| `Ender Dragon HP` | `enderDragonHp` |
| `_FAST` | `fastMode` |
| `_Chars` | `fontChars` |
| `_FoodMul` | `foodMultiplier` |
| `_FoodSaturation` | `foodSaturation` |
| `_ForceDelay` | `forceDelay` |
| `_fcount` | `frameCount` |
| `_Mode` | `gameMode` |
| `game string` | `gameString` |
| `_Gamma` | `gamma` |
| `_GEN_VERSION` | `genVersion` |
| `_GLight` | `globalLight` |
| `_GoldHealth` | `goldenHearts` |
| `_Health_s` | `health` |
| `_HeldC` | `heldCostume` |
| `_HeldC Name` | `heldCostumeName` |
| `_HeldInvID` | `heldInventoryId` |
| `_Holding_Totem` | `holdingTotem` |
| `_Hunger` | `hunger` |
| `_Locked` | `inputLocked` |
| `_InsideIdx` | `insideIndex` |
| `_Creative?` | `isCreative` |
| `_Eating` | `isEating` |
| `_Spectator` | `isSpectator` |
| `_Survival` | `isSurvival` |
| `_ItemTrading` | `itemTrading` |
| `just interacted with mob` | `justInteractedWithMob` |
| `_KeyDelayTrick` | `keyDelayTrick` |
| `_KnockBack` | `knockback` |
| `_LastDir` | `lastDirection` |
| `_lsy` | `levelHeight` |
| `_lsx` | `levelWidth` |
| `_lsxNeg` | `levelWidthNeg` |
| `_LightProb` | `lightProbe` |
| `_Lighting?` | `lightingEnabled` |
| `lightningx` | `lightningX` |
| `_loot` | `lootRoll` |
| `_MaxHarvest` | `maxHarvest` |
| `_MaxMobsBad` | `maxHostileMobs` |
| `_MaxMobs` | `maxMobs` |
| `MAX PLAYER HEALTH` | `maxPlayerHealth` |
| `_Max_Reach` | `maxReach` |
| `_Mob100` | `mobCap100` |
| `_MDMUL` | `mobDataStride` |
| `_MobMul` | `mobMultiplier` |
| `nextelytradamage` | `nextElytraDamage` |
| `_NextSelID` | `nextSelectionId` |
| `_NextSpawn` | `nextSpawnTick` |
| `_NormHealth` | `normalMaxHealth` |
| `_Numseed` | `numericSeed` |
| `_WalkFrame` | `playerWalkFrame` |
| `_RandIdx` | `randomIndex` |
| `_RandomSeed` | `randomSeed` |
| `_Raw Survival` | `rawSurvival` |
| `_TimeReal` | `realTimeMs` |
| `_REFSIZE` | `refSize` |
| `_resistance mul` | `resistanceMultiplier` |
| `_respawnIdx` | `respawnIndex` |
| `_respawnSeed` | `respawnSeed` |
| `_rocket_ticks` | `rocketTicks` |
| `_SHOWCURSOR` | `showCursor` |
| `_Skin` | `skin` |
| `_Sound` | `soundOn` |
| `_SpawnArea` | `spawnArea` |
| `_Speak` | `speakOn` |
| `Speaker #` | `speakerNumber` |
| `_SpriteCount` | `spriteCount` |
| `_SteveLight` | `steveLight` |
| `_Steve_Speed` | `steveSpeed` |
| `_ticks` | `tickCount` |
| `_tickTime` | `tickTime` |
| `_UnderCursor` | `tileUnderCursor` |
| `_UnderCursor Name` | `tileUnderCursorName` |
| `_ToolTipID` | `tooltipId` |
| `_ToolTipWait` | `tooltipWait` |
| `_Spyglass` | `usingSpyglass` |
| `_wardenx` | `wardenX` |
| `_wardeny` | `wardenY` |
| `_Worldspawn` | `worldSpawn` |
| `_WorldSpawnSeed` | `worldSpawnSeed` |
| `_XRAY` | `xrayEnabled` |

## Cursor — 17 renamed

| old | new |
|-----|-----|
| `_Campfire` | `campfire` |
| `data2` | `cursorDataB` |
| `data3` | `cursorDataC` |
| `pr_dist` | `cursorDistance` |
| `invIdx_c` | `cursorInventoryIndex` |
| `refIdx_c` | `cursorRefIndex` |
| `tile_c` | `cursorTile` |
| `tileIdx_c` | `cursorTileIndex` |
| `xx` | `cursorTileX` |
| `yy` | `cursorTileY` |
| `Dig_Type` | `digType` |
| `DUR` | `durability` |
| `_Food` | `foodItem` |
| `lastX_c` | `lastCursorX` |
| `lastY_c` | `lastCursorY` |
| `lArmTick` | `leftArmTick` |
| `newTip` | `newTooltip` |

## Generator — 20 renamed

| old | new |
|-----|-----|
| `vmul` | `altitudeMultiplier` |
| `voff` | `altitudeOffset` |
| `BMUL` | `biomeDataStride` |
| `dir_g` | `genDirection` |
| `i_g` | `genIndex` |
| `refIdx_g` | `genRefIndex` |
| `t2_g` | `genTempB` |
| `xx_g` | `genTileX` |
| `yy_g` | `genTileY` |
| `dy` | `genVerticalStep` |
| `x_g` | `genX` |
| `y_g` | `genY` |
| `g_IsFlat` | `isFlatWorld` |
| `LastY` | `lastY` |
| `sand` | `sandDepth` |
| `i_z3` | `stripFillIndex` |
| `g_tyy` | `terrainHeight` |
| `_WaterLevel` | `waterLevel` |
| `water Tile ID` | `waterTileId` |
| `g_worldSize` | `worldSize` |

## Mobs — 23 renamed

| old | new |
|-----|-----|
| `cloneAsID` | `cloneAsId` |
| `Common drops` | `commonDrops` |
| `digIdx` | `digIndex` |
| `Drop Amount` | `dropAmount` |
| `MDOff` | `mobDataOffset` |
| `dirP` | `mobDirection` |
| `mob dist` | `mobDistance` |
| `halfY_P` | `mobHalfY` |
| `healthP` | `mobHealth` |
| `hurtingP` | `mobHurting` |
| `inWaterP` | `mobInWater` |
| `idx_p` | `mobIndex` |
| `light_p` | `mobLight` |
| `lightMod_p` | `mobLightMod` |
| `ofy_p` | `mobOffsetY` |
| `stateP` | `mobState` |
| `tileP` | `mobTile` |
| `tileIdxP` | `mobTileIndex` |
| `typP` | `mobType` |
| `mob x` | `mobX` |
| `mob y` | `mobY` |
| `Pillager Spawn` | `pillagerSpawn` |
| `within range` | `withinRange` |

## Processor — 19 renamed

| old | new |
|-----|-----|
| `gt_i` | `growTileIndex` |
| `iterate-command` | `iterateCommand` |
| `iterate-commandblock` | `iterateCommandBlock` |
| `LightE2` | `lightEast2` |
| `LightN2` | `lightNorth2` |
| `LightS2` | `lightSouth2` |
| `LightW2` | `lightWest2` |
| `checkTile_pr` | `procCheckTile` |
| `count_pr` | `procCount` |
| `data2` | `procDataB` |
| `dir_pr` | `procDirection` |
| `pr_dist` | `procDistance` |
| `refIdx_pr` | `procRefIndex` |
| `refIt_pr` | `procRefItem` |
| `refMode_pr` | `procRefMode` |
| `refTile_pr` | `procRefTile` |
| `t_pr` | `procTemp` |
| `tile_pr` | `procTile` |
| `pr_tool` | `procTool` |

## Tiles — 11 renamed

| old | new |
|-----|-----|
| `beacon level #` | `beaconLevelNum` |
| `CloneAsID` | `cloneAsId` |
| `clonesid` | `clonesId` |
| `_gold-count` | `goldCount` |
| `t_ilumTmp` | `illuminationTemp` |
| `isfull?` | `isFull` |
| `ix` | `renderOffsetX` |
| `iy` | `renderOffsetY` |
| `i_t` | `tilesIndex` |
| `refIdx_t` | `tilesRefIndex` |
| `t_tileIdx` | `tilesTileIndex` |
