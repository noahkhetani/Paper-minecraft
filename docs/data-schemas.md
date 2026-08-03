# Data-table schemas

The game's static data lives in flat Stage lists, read by computed index. Most are
**self-documenting** — their first rows describe their own column layout. These are also
exported verbatim to `game-data/`-style JSON by `tools/export_data.py` if needed.

Stride = how many cells each record occupies.

## `_MOB_DATA` (stride `mobDataStride` = 13)
Per-mob row: `Mob ID, Mob Name, Size %, Half Height, Y Offset, Root Costume, …`

## `_BLOCK_DATA` (stride `blockDataStride` = 21) — the item/block property table

Per-block-type row at `blockId * 21 + offset`. The base table ships in `_BLOCK_DATA_SAVE`
(1,903 rows) whose **row 0 is a self-documenting header**; runtime variants are appended by
Tiles' `Dup:` / `Duplicate Traits` builders (they copy fields +3…+15 from a source row).
Full schema (code offset `+k` = header field k):

| +k | field | values |
|---|---|---|
| +1 | Block ID | row id |
| +2 | Block Name | string |
| +3 | Solid for walking | `Y` / `N` / `P` (platform) |
| +4 | Hardness | 0 = not diggable, >0 ratio, −1 = instant dig |
| +5 | Digging tool + tier | `N`one `S`pade `A`xe `P`ickaxe s`H`ears s`W`ord `F`lint&steel, e.g. `P1`, `W2` |
| +6 | Liquid height | 0–9 |
| +7 | Flow direction | `N` / `.` source / `L` / `R` / `D` |
| +8 | Can fall | `N`/`Y`/`X` can't float/`W` needs wood/`L`,`R` attached |
| +9 | Light absorption | 0 transparent … 16 opaque; **negative = emits light** |
| +10 | Tile group | 1 Tool, 0 unplaceable, −1 Food, 8 unstackable-large, 10 Wood, 11 Door, 12 Spawn egg, 13–16 armor (helm/chest/legs/boots), 20 redstone-hand, 22 switch, 30/31 stairs, 34 max-stack-16 |
| +11 | Harvest block | 0 self, >1 tile id, −1 nothing, −n = 1/15 chance of n |
| +12 | Smelt into | block id (0 = none) |
| +13 | Furnace fuel burn | seconds (0 = not fuel) |
| +14 | Damage inflicted | weapon/hazard damage (mace = 5) |
| +15 | Creative tab | 1 building … 7 combat, −1 hidden |
| +16 / +17 | Tile / inventory sprite id | costume numbers |
| +18 | Item durability | e.g. mace 500 |
| +19 | Root item ID | family base (all pistons → 190) |
| +20 | Activate on load | `N` / `G`row / `A`ctivate / `B`urn / `R`edstone |

## `BIOME_DATA` (stride 9)
Per-biome row: `Biome ID, Name, Type (G/D/T/S/W/N), Altitude Multiplier, Altitude Offset,
Island Multiplier, Tree Type, Tree Frequency`. Used by `Init Ground Curves`:
`vmul = AltMult-1`, `voff = AltOffset-3`.

## `_LOOT_TABLES`
`Loot table Name, # entries`, then `(Item id, Weight, Min amount)` triples per entry.

## `_CHEST_LOOT`
Named pools (e.g. `Piglin Trades`) followed by `count` then item ids.

## `_FOOD_DATA`
Per-food row: `Block ID, Block Name, Hunger Points Restored, Saturation, Chance of food
poisoning, Item left after consuming`.

## `Enchant Data`
Per-tool enchant id groups (e.g. `Bow, 355, shovel, 537, 538, 539, …`).

## `ADVANCEMENT DATA` / `ADVANCEMENTS`
Advancement titles / tree (icon + name per advancement).

## World lists (runtime, not static)
`_LEVEL` (block id per tile, 1-based flat; `index = y*levelWidth + x + 1`), `_Light`,
`_INSIDE`, `_GROW`, `_HARVEST`, `_INV` (inventory), `_RANDOM` (pre-filled RNG stream walked
by `randomIndex`). See `docs/architecture.md` and `tools/decompile.py` for how each is used.
