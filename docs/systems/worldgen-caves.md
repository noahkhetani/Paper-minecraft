# World generation — caves, ores & underground shaping (G1)

Reverse-engineered from the **Generator** sprite (expressions quoted from decompiled code,
post-rename names). Terrain heightmap + the deterministic PRNG are covered in the earlier
docs; this covers everything underground. Coordinates: **row 1 = world bottom (bedrock),
top rows = sky** (verified by the deepslate depth rule and sky-light seeding);
`index = x + y·levelWidth + 1`.

## The universal vein/cave engine — `Make Seams (typ, chance, size, maxRow, up?, onlyInID, link?)`

Everything underground (ores, gravel/dirt pockets, stone variants, lava pockets, air caves)
is placed by this one block:

- **Budget:** `total = levelWidth × maxRow × chance/100` **cells** (decremented per cell
  actually written by `Fill Horizontal Line`), with a hard cap of 300 seams.
- Each seam: `x = random(1, levelWidth)`; `y = random(1, maxRow)` — or, with `up?`,
  `y = random(maxRow, waterLevel)` (a band near water level; used for surface-anchored
  deposits like clay).
- **Shape:** `size > 0.5` → a blob: `Fill Circle_g(typ, x, y, random(1, size), roughness 1,
  onlyInID)`; else a single cell.
- **`link?` → the worm walker** (tunnels): heading is mostly-vertical 70% of the time
  (`±(60–119.9)°`) else any angle; step `random(0.8, 1.8)`; walks up to `random(0, 64)`
  steps, jittering the heading ±8° (70%) or ±35° (30%), occasionally re-rolling step size.
  Each step stamps a small circle; **4% of steps blow out a big chamber**
  (`Fill Circle_g` radius `random(1.5, size)`) and record its tile index in **`@Caverns`**
  — the list later used to place cave biomes and underground structures.

### Placement primitives
- **`Fill Circle_g (typ, x, y, radius, roughness, onlyInID, slip, chance)`** — scanline
  circle: per row, half-width `√(r²−y²)`, jittered ±`roughness` per row.
- **`Fill Horizontal Line (typ, x, y, x2, onlyInID, slip, chance)`** — writes cells
  `x…x2` of row y. `onlyInID` restricts replacement to that block (0 = any; 4 also matches
  628); **never overwrites** bedrock 6 / 1175 / 12. `slip`+`chance`: 1-in-`chance` cells get
  `slip` instead of `typ` (vein impurities; slip 591 is itself 1/4 replaced by 248; slip 785
  is queued into `@_GROW` with +400 s). Placing lava 81 registers the cell as active.

## The ore table — `Init Seams` (overworld, biomeId < 1000)

`Make Seams(type, chance%, size, maxRow, …)` calls, in order (waterLevel = 57):

| block | chance | size | max row | notes |
|---|---|---|---|---|
| Gravel 5 | 3.2 | 6 | 7 | linked (worm) |
| Granite 369 / Diorite 370 / Andesite 371 | 3.7 | 6 | 22 | linked |
| **Coal Ore 13** | 1.5 | 1.4 | 70 | |
| Tuff 640 | 3 | 3 | 7 | RNG-pinned via `Push Random Stack(1999)` |
| **Redstone Ore 217** | 0.1 | 1.5 | 31 (0.54·wl) | pinned |
| **Iron Ore 16** | 0.5 | 2 | 40 | pinned |
| **Emerald Ore 271** | 0.1 | 0.5 | 15 (0.27·wl) | pinned |
| **Lava pockets 81** | 1.7 | 2 | 23 (0.4·wl) | |
| **Copper Ore 689** | 1.7 | 2.5 | 7 | linked |
| **Iron Ore 16** (2nd band) | 0.6 | 2 | 60 | |
| **Gold Ore 15** | 0.1 | 0.5 | 128 (full) | |
| **Gold Ore 15** (2nd band) | 0.13 | 1.5 | 31 | |
| **Lapis Ore 697** | 0.5 | 1 | 15 | |
| Dirt 3 | 1 | 3 | 27 | linked |
| **Diamond Ore 14** | 0.7 | 0.6 | 15 | |
| (mod) Magnite Ore | 0.4 | 0.2 | 15 | if Mods[5] |

Nether (1000 ≤ biomeId < 2000): Magma 941, Gravel 5, Soul Sand 257, **Nether Gold 346**,
**Quartz 347**, Blackstone 351, Basalt 417 (all full height), **Ancient Debris 355**
(0.4 / 0.44 / rows ≤ 42). End + Mods[8]: Enderite Ore.

`Push Random Stack(n)` / `Pop Random Stack` save/restore `randomIndex` — pinning a
generation stage to a **fixed position in the `_RANDOM` stream** so those ores land
identically regardless of earlier draw counts.

## Caves — `Init Caves`

Non-flat worlds only. Overworld: `randomIndex` pinned to 4000/4010, cave budget
`random(6,12)`, then air ("1") seams `size 4, maxRow waterLevel+4, up?` — plus clay 53
blobs *inside sand* near water level (skipped in deserts). Nether: `random(12,20)` air
seams, size 6, full height. Afterwards `randomIndex = 5000` and the bottom row is sealed
with **Bedrock 6** (`Fill Horizontal Line("6", row 0)`);
`Adjust Bedrock Layer Lighting` zeroes sky-light across that row.

## Deepslate conversion — `Add Postgen`

`@Deepores` is a pairs table `[oreId, deepVariantId]`: 13→629, 14→630, 15→631, 16→632,
271→633, 217→634, 697→698, 689→977. In the post-gen sweep: **any ore in rows y < 16 is
swapped to its deep variant.** (Add Postgen also prunes unsupported plants and rolls ocean
monuments at 1/75 per qualifying ocean cell — full coverage in the structures docs.)

## Cave biomes — dripstone / lush / deep dark

All three share one pattern: the caller sets `$ss_g` to a tile index (a `@Caverns` chamber),
then:
- **`Spawn Dripstone Cave`** — paints a Dripstone-block (1177) shell, radius 7, only inside
  stone 4. Later **`Stalagmites & Stalactites`** scans all 1177-with-air-above: 1/3 chance
  of 1–3 pointed-dripstone (1178) stalagmites growing up; then finds the ceiling (scan up,
  max row 70 — **quirk: uses a hardcoded `+= 200` instead of levelWidth**) and 1/2 chance
  hangs 1–4 stalactites (1179) down from stone/59/1177 ceilings.
- **`Spawn Lush Cave`** — moss (305) shell radius 7; moss floors with air above grow
  glow-berry vines (1351, 1/3) or cave vines (311, else), registered active; ceilings get
  27 rolls of the **"lush cave" loot table**; result 827 is queued in `@_GROW`.
- **`Spawn Deep Dark`** — sculk (723) shell radius 7; ceilings get "Deep Dark" loot-table
  decorations.

## Pools — `Enlarge pool bounds`

Scans columns 2…199: where the surface dips below water level, it walks the pool edge
leftward (marking `altitude = waterLevel−1` while the water-level row is air) so pools have
clean edges, then calls `DoSkySea(column, 1, waterLevel | 0)` per column to fill the water
column (see structure-tools doc).

## Fix cookbook

- **Ore rarity/size/depth:** the exact `Make Seams` rows above in `Init Seams` — change
  chance (density %), size (blob radius), or max row (depth band).
- **More/fewer caves:** `random(6,12)` budget and seam `size 4` in `Init Caves`
  (nether: `random(12,20)`, size 6).
- **Deepslate depth:** the `< 16` row check in `Add Postgen`.
- **Add a new ore:** append a `Make Seams` call in `Init Seams` + (optionally) a pair in
  `@Deepores` for a deep variant.
- **Cave-biome size:** the radius-7 `Fill Circle_g` calls in `Spawn Dripstone/Lush/Deep Dark`.
- **Stalactite frequency:** the `random(1,3)==1` / `random(1,2)==1` rolls in
  `Stalagmites & Stalactites`.
- **Vein impurities:** the `slip`/`chance` args of `Fill Horizontal Line`.
