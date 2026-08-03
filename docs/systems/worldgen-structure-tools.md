# World generation — structure dispatch & shared helpers (G3)

Reverse-engineered from the **Generator** sprite. Post-rename names; row 1 = world bottom.
The circle/line placement primitives (`Fill Circle_g`, `Fill Horizontal Line`) are in
[worldgen-caves.md](worldgen-caves.md).

## The unifying insight: structures are GROWN from seed blocks

`Spawn House (tileID, x, left, right)` does **not** stamp a building. It:
1. Bails if the footprint (`x + left + right`) exceeds the level width.
2. Averages the terrain height across the footprint and **flattens toward it** with
   `Pavement Strip(x, y, step ±1)` (walks the surface up/down one step at a time, ~60%
   biased toward stepping, paving as it goes), then paves `left` columns, plants the seed,
   and paves `right` columns.
3. **Plants the single seed block `tileID` one row above the pavement and queues it in
   `@_GROW`.** The Processor's growth system then "grows" the full building out of the
   seed — the same mechanism as tree saplings. **Building layouts live in the Processor's
   grow handlers, not in the Generator.**

### `Spawn Structures %b (start?)` — the per-chunk surface-structure roll
- `random(1,5) == 3` → **no structure** this chunk (except the End).
- Excluded biomes (no surface structures): 1, 3, 5, 14 (ocean), 15, 16, 17, 18.
- Position `x = random(10, 0.6·levelWidth)`; then biome → seed id:
  | biome | seed block | notes |
  |---|---|---|
  | 9 | 700 | only 1/3 of the time |
  | 11 | 976 | |
  | 8 | 975 | |
  | 12 | 738 | wide footprint (padding 11+5) |
  | 10 | 1174 | |
  | 7 | 739 | |
  | 4 | 1806 or 668 | 50/50 |
  | default | 671 (1/3, not at world start) else 707 (1/7) | |

## The active-tile system — `Register Activity %n`

Registers a tile as "active" (furnace burning, redstone device, flowing fluid, growing
vine…): enqueues a block-light update, then allocates a **`refSize`(=6)-field record** in
`@_RefData` and stores the record pointer in `@_LevelRef[tile]`. This is the record that
redstone/TNT use (`+1` mode char, `+4` cooldown — see fluids-and-redstone doc).
**`refSize` is the `@_RefData` record stride.**

## Other helpers

- **`Block Name %s`** — reverse lookup: item/block *name* → id
  (`round(indexOf(@_BLOCK_DATA, name) / 21)`).
- **`Spawn Block %s Track %s`** — the structure "pen": writes a block at cursor `$track`,
  registers it active, advances the cursor by the given step (+1 right, ±levelWidth
  up/down). Used by nether trees, pillars, etc.
- **`Structure void %s`** — writes the indestructible barrier **1175** (unless the cell is
  already one of the special ids 1176/457/288/354/353) — protects structure interiors.
- **`Store Original`** — snapshots `@_LEVEL` into `@_LCopy` (the pristine pre-play copy,
  used for save-diffing).
- **`Clear Lists`** — resets all per-chunk world lists (level, refs, grow, light, harvest,
  caverns) at generation start.
- **`Freeze Surface %n (aboveRow)`** — per column, finds the topmost solid cell; if higher
  than `aboveRow`: water 38 → **ice 287** with **snow layer 283** above; other solid
  blocks get a snow layer (grass 2 also becomes snowy grass 284). Cold biomes call it with
  row 1 (freeze everything); others with `waterLevel + 15` (mountain snow caps).
- **`Add Water or Lava (count, maxY, typ)`** — sprinkles `count` fluid cells into random
  air cells (rows < 33 in the overworld — underground lakes; any row in the nether):
  30% walk **up** to the cave ceiling (hanging drips), 70% walk sideways to a wall, then
  place + register active.
- **`DoSkySea (x, ?, waterLevel)`** — per-column initializer: paints **sky light 16**
  directly down the air column (the BFS handles everything below), enqueues relights at the
  surface, and — for columns whose surface is below `waterLevel` — fills the column with
  `waterTileId` (oceans/pools) and queues a `@_GROW` at the floor (seagrass/kelp).
- **`Change Background %s`** — sets `backgroundId` + broadcasts `change background`.

## Fix cookbook

- **Structure frequency:** the `random(1,5)==3` skip and per-biome rolls in `Spawn Structures`.
- **Which biome gets which building:** the biome→seed table in `Spawn Structures`; the
  building's *shape* is in the Processor's grow handler for that seed id.
- **Underground lake amount:** the `Add Water or Lava(count, maxY, …)` call sites in `init`
  (6×22 water/lava overworld; 6×40 water; nether 4×(levelHeight−4) lava).
- **Snow line:** the `aboveRow` argument of `Freeze Surface` (`waterLevel + 15` normal,
  1 in snow biomes).
- **Protect/unprotect structure interiors:** `Structure void` (barrier 1175).
