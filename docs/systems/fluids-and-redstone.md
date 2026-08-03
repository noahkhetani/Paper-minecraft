# Fluids & redstone (Processor)

Reverse-engineered from the **Processor** sprite (expressions quoted from decompiled code,
post-rename names). Both systems run inside the Processor's per-tick "active tiles" scan:
active things (flowing fluid, primed TNT, powered devices) are registered in `@_LevelRef` /
`@_RefData` records (`refIdx`), and the tick loop calls the handlers below.

## Fluids — `Process Flowing Tile %n %s` + `Flow Sideways %n %n`

**Representation.** Fluid family is by block-id range: water family base **38**, lava base
**81** (ids < 39 and the waterlogged pair 1576/1577 count as water). `Get Water Stats(tile)`
decodes a tile into globals: `flowBase2` (38/81/0), `flowDir2` (`.` = source, `D`/`L`/`R` =
flow direction), `depth2` (0–8). Flow tiles encode direction+depth in the id:
**`id = base − offset + depth`** with offset **18 = leftward**, **10 = rightward** flow.
Air is block id **1**.

**Per active fluid tile, each tick:**
1. **Interaction with the block above** (`refTile − levelWidth`): if it's the *other* fluid
   family → it solidifies: current tile lava → above becomes **stone (4)**; current tile
   water meeting lava above → **obsidian (52)** if the lava is a source, else
   **cobblestone (41)**.
2. **Fall:** if the block below isn't solid and depth < 9 → below becomes `base − 1`
   (37 falling water / 80 falling lava).
3. **Dry-up:** a flow tile checks its upstream neighbour (L→right cell, R→left cell,
   D→above). If upstream depth isn't greater than its own, it dries: water → air instantly;
   **lava recedes slowly** — 80 % chance (`random(1,5) > 1`) it's queued into `@_GROW` with a
   0.4 s delay instead.
4. **Spread:** only when sitting on a solid block or on a source (`canFlow`), and only with
   depth ≥ 2. Spreads to both sides (skipping its own upstream side) via `Flow Sideways`
   with depth − 1.

**`Flow Sideways(tileIdx, baseOffset)`:**
- Other fluid family met sideways → **cobblestone (41)**.
- Target not solid and shallower than the incoming depth → write
  `(base − baseOffset) + depth` (the directional flow tile).
- **Infinite water:** if the target is a **water source** (depth 8, `.`) and the incoming
  flow direction opposes it (left-spread meeting an R-flow or right-spread meeting L-flow)
  → the tile is rewritten as a full **source (38)**. Two flows meeting regenerate sources.

## Redstone / activation

**Model.** There is no per-wire power level scan; activation is **event-driven pulses**.
`Activate Blocks Around (idx, notDiags?)` pokes `Collateral Checks_pr` at the 4 orthogonal
neighbours (plus 4 diagonals unless suppressed); checks decide per-tile whether to activate
the device there. Active devices hold state in `@_RefData` records: `+1` = mode char
(`r` repeater-latched, `D` detonating, `X…` primed-TNT), `+4` = re-trigger cooldown
timestamp (default `timer + 2`, short pulses `timer + 0.3`), `+5` = aux counter.

**`Activate Redstone (refIdx, refTile, tile, opt)`** — the device dispatcher (opt: `o` gated
by the `+4` cooldown, `t` timed pulse that auto-releases after 0.3 s, `r` repeater chain):
- **Repeater family** (193/383/233/1424/1682/1173/1741 and 1051–1053) → `Activate Repeater`
  (chained delay; marks the record `r`).
- **Pistons** — family flag is `_BLOCK_DATA[tile*21 + 19] == "190"`; ids map to direction:
  190/191 extend/contract **up** (`+levelWidth`), 206/207 **down**, 227/228 **right** (+1),
  230/231 **left** (−1) → `Piston Extend` / `Piston Contract` move blocks via `Move Tile`.
- **Doors:** `@Door Data (Redstone)` holds open/closed id pairs → `Toggle Door` swaps them.
  **Trapdoors:** the pair is computed arithmetically (`tile*2 ± 1 − tile`).
- **Droppers (1708–1711)** vs **dispensers (1683–1686, 1634)** → `Dropper/Dispenser`
  (dispensers *use* the item: `Shoot From Dispenser`; droppers just eject).
- **Copper bulbs** (block name contains "bulb"): toggle lit/unlit by id ±1 (waxed variants
  inverted), then `Add To Light Mod` twice to refresh lighting.
- **Command block (1680):** looks up `@command_block` triplets `[tileIdx, chunkSeed, cmd]`,
  runs the command via `broadcast runcommandblockcommand`, then removes the entry.
- Anything else → `Deactivate Tile`.

## TNT — `Detinate %n %n %b` (+ `Explode Circle_pr`)

- Priming sets `@_RefData[+1] = "D"`, fuse `+4 = timer + random(2.5, 3.1)` (chain-ignited
  TNT: `random(0.5, 1.5)`), and the primed TNT **falls** (`Initiate Block Fall`).
- End crystal (1568) explodes immediately with radius **6**.
- Explosion sizes via `Explode Circle_pr(x, y, radius, …)`: standard TNT **6**, creeper-type
  entries **3.5**, and escalating variants **7 / 14 / 28** (modded TNTs). Mob/player damage
  from explosions is routed through the `@_Explode` queue (see combat doc: creepers push
  `[mobId, power]` with power 3, charged 5).
- Mods can re-skin TNT behaviour (`Switch tnt (mods)`: water/lava/hostile/farm variants).

## Fix cookbook

- **Water spread distance:** the `depth2 < 2` stop and the `depth − 1` decrement in
  `Process Flowing Tile` (max run ≈ 7 tiles from a source).
- **Lava recede speed:** the `random(1,5) > 1` + `+0.4 s` queue in `Process Flowing Tile`.
- **Water+lava products:** the literals 4 / 52 / 41 in `Process Flowing Tile` (above-cell
  branch) and 41 in `Flow Sideways`.
- **Disable infinite water:** remove the depth-8 source branch in `Flow Sideways`.
- **TNT fuse / radius:** `random(2.5,3.1)` and the `Explode Circle_pr(…, 6, …)` call in
  `Detinate`.
- **Repeater/pulse timing:** the `timer + 2` and `timer + 0.3` cooldowns in
  `Activate Redstone`.
- **Piston direction/behavior:** the id→direction table at the top of `Activate Redstone`
  and `Piston Extend/Contract`.
