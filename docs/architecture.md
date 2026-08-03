# Architecture

A map of which sprite owns what. The complete custom-block inventory (every sprite's blocks)
is in [analysis/custom-block-inventory.md](analysis/custom-block-inventory.md).

Where the heavy logic lives, by block count:

| Sprite | Owns |
|--------|------|
| **Stage** | global state: world lists, inventory, mob/recipe/loot data, save snapshots |
| **Generator** | world generation: terrain heightmap, biomes, caves, structures |
| **Processor** | per-tick simulation: fluids, growth, falling blocks, redstone, furnaces, day/night, lighting |
| **Cursor** | player interaction: mining/placing, held items, tool damage, bow, effects, mob spawning |
| **Tiles** | tile/item rendering (pen) + container/inventory logic + recipes |
| **Mobs** | mob AI, spawning, combat |
| **Steve / Steves Head / Arm / Legs / Boots** | player character, layered body-part animation |
| **Save Game** | serialization/persistence (localStorage) via the `*_SAVE` lists |
| **Commands** | chat commands / cheats |
| HUD: Health, Hunger, Oxygen, Armor, XP, Boss Bar, Map, Advancements | status overlays |

To read any sprite's logic as pseudocode:
```bash
python tools/decompile.py "Generator"                      # list its custom blocks
python tools/decompile.py "Generator" "Init Ground Curves" # decompile one
python tools/decompile.py "Cursor" --hat "update health"   # decompile a broadcast handler
```

Data tables are documented in [data-schemas.md](data-schemas.md). Variable name mapping
(old → new) is in [variable-glossary.md](variable-glossary.md).

## Deep-dives (reverse-engineered systems)

Exact formulas, data layouts, and a "fix cookbook" per system:

- [systems/combat-and-damage.md](systems/combat-and-damage.md) — melee formula, crits,
  mace smash, cooldowns, durability, mob attacks, knockback, `@_MOB` field map, health pipeline.
- [systems/mob-ai.md](systems/mob-ai.md) — central sim + visual clones, movement state
  machine, aggro/chase, spawning/despawn lifecycle, portal transfer, dragon AI.
- [systems/fluids-and-redstone.md](systems/fluids-and-redstone.md) — water/lava spread &
  interactions, infinite water, activation pulses, pistons/doors/dispensers, TNT.
- [systems/player-physics-and-damage.md](systems/player-physics-and-damage.md) — movement
  constants, terrain speed table, fall-damage formula, contact hazards, drowning, armor slots.
- [systems/projectiles.md](systems/projectiles.md) — bow charge→velocity, arrow flight
  (damage = impact speed), tridents/Riptide, thrown items, the `@_HARVEST` projectile model.
- [systems/lighting.md](systems/lighting.md) — dual-channel sky/block light, budgeted BFS
  flood fill, sunlight columns, emitters via negative `_BLOCK_DATA[+9]`.
- The full 21-field `_BLOCK_DATA` item/block schema is in [data-schemas.md](data-schemas.md)
  — the item/block property table used across the game (damage, hardness, tools, fuel, light, drops).
- [systems/worldgen-caves.md](systems/worldgen-caves.md) — the `Make Seams` vein/cave engine,
  **the complete ore table** (density/size/depth per ore), deepslate conversion (rows < 16),
  cave biomes (dripstone/lush/deep dark), pools, bedrock.
- [systems/worldgen-trees.md](systems/worldgen-trees.md) — worldgen plants *saplings* (trees
  grow via the Processor), biome tree strings/frequency, nether tree stamps, RNG pinning.
- [systems/worldgen-structure-tools.md](systems/worldgen-structure-tools.md) — **structures
  grow from seed blocks** (biome→seed table), the active-tile system (`Register Activity` /
  `@_RefData`), snow/ice pass, underground lakes, sky/ocean column init.
