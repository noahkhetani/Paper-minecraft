# World generation — trees & vegetation (G2)

Reverse-engineered from the **Generator** sprite. Post-rename names; row 1 = world bottom.

## The key insight: worldgen plants saplings, not trees

Overworld trees are **not constructed by the Generator**. `Make Tree` plants a *sapling*
and queues it in `@_GROW` with grow-time 0 — the Processor's normal growth system
(`Grow Sapling` → `Grow Tree`, see the world-simulation doc) builds the actual tree on the
first simulation ticks. Tree *shapes* therefore live in **Processor::Grow Tree**, not here.

## `Make Tree (x, y, size)`

1. Picks a random letter from the biome's tree-type string `BIOME_DATA[7 + biomeId*9]`
   (e.g. plains `"OB"` — equal odds per letter, so duplicates weight the odds).
2. Letter → sapling block id: **O**ak 55, **B**irch 176, **S**pruce 175, **J**ungle 177,
   **D**ark-oak 298, **A**cacia 405, c**H**erry 597, **M** 46, **R** 1735, **P** 1756
   (unknown letters default to oak 55).
3. Plants on grass (2) or 998 one row above the candidate; adds to `@_GROW` with time 0.
4. **Desert rule:** on sand (7/364) in a `D`-type biome it plants a **3-tall cactus (11)**
   column instead.

Candidate positions come from the `@tree` list — (x, y) pairs recorded per column by
`Make New Strip` during terrain fill.

## `Populate Trees and shrubs`

- **Pass 1 — trees:** for each `@tree` candidate, roll `random(0,100)` against the biome's
  tree frequency (`BIOME_DATA[8 + biomeId*9]`); success → `Make Tree(x, y, random(2,3))`
  and the candidate is consumed.
- **Pass 2 — decorations:** `random(4,12)` of the remaining candidates get shrubs/grass;
  flowers are drawn as `@flowers[random(1, random(1, len))]` — the nested random **biases
  toward the front of the `@flowers` list**, making early-listed flowers commoner.
- Further passes add berry/moss features (e.g. 1802/1803), and vines (registered active via
  `Register Activity` so they grow/animate).

## `Spawn Nether Tree (TrunkID, LeavesID)` — crimson/warped

Fixed-shape stamp using the `Spawn Block %s Track %s` cursor (`$track` walks the level
list; step `levelWidth` = up one row):
trunk height `random(2,5)`, then a canopy of rows 3 → 5 → 5 → 3 leaves with a
**shroomlight (396)** embedded in the first canopy row.

## RNG pinning — `Push Random Stack %n` / `Pop Random Stack`

`Push` saves `randomIndex` onto `@RNDStack` and jumps it by the given offset; `Pop`
restores. Generation stages wrapped in push/pop draw from a **fixed position in the
`_RANDOM` stream**, so their output is identical regardless of how many draws earlier
stages consumed (used around parts of the ore table; offset 1999 there).

## Fix cookbook

- **Tree density per biome:** `BIOME_DATA[8 + biomeId*9]` (frequency vs the 0–100 roll).
- **Which trees appear:** the tree-type string `BIOME_DATA[7 + biomeId*9]` (repeat letters
  to weight, e.g. `"OOB"` = 2/3 oak).
- **Add a new tree letter:** the letter→sapling ladder in `Make Tree`.
- **Cactus height:** the `repeat 3` in `Make Tree`'s desert branch.
- **Nether tree shape:** the row pattern in `Spawn Nether Tree` (trunk `random(2,5)`,
  canopy 3/5/5/3, shroomlight 396).
- **Flower mix:** order of the `@flowers` list (front = common) in `Populate Trees and shrubs`.
- **Tree size/shape at growth time:** that's **Processor::Grow Tree** (world-simulation
  doc), not the Generator.
