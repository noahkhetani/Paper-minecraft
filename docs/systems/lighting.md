# Lighting engine (Processor)

Reverse-engineered from `Process Light Loop` / `Process Light Mod` / `Get Light From` /
`Get Illumination` / `Add To Light Mod` — the whole engine is ~100 lines. Post-rename names.

## Data model

`@_Light` is **double length** (2 × levelWidth×levelHeight):
- **Indices 1 … len(_LEVEL): sky-light channel.** The sky row (highest indices — larger
  index = higher up) is seeded **16** by the Generator; sunlight floods down from there.
- **Indices len+1 … 2·len: block-light channel.** Seeded by emitter blocks — a block emits
  when its `_BLOCK_DATA[+9]` (light absorption) is **negative**; brightness = `−(+9)`.

Absorption: `_BLOCK_DATA[tile*21 + 9]` (0 = transparent, 16 = opaque, clamped ≥ 0 when
passing through).

## Propagation — a budgeted BFS flood fill

- `@_LightMod` is the work queue (dedup'd by `Add To Light Mod`). Any change (placed/broken
  block, toggled bulb) enqueues the affected cell in one or both channels.
- **`Process Light Loop`** drains at most **25 cells per tick** — the perf bound that keeps
  relighting smooth but makes big changes visibly "ripple".
- **`Process Light Mod`** per cell:
  1. Seed: sky row → 16 (sky channel); emitter → `−(+9)` (block channel).
  2. Pull light from the 4 neighbours via `Get Light From` (neighbour light − this block's
     absorption), take the max.
  3. **Sunlight column trick:** the value only decays −1 per tile if the cell *above* has
     less than 16 — full sunlight travels straight down undiminished.
  4. If the new value is **higher** than stored: store it and enqueue any neighbour with
     less than value−1 (spread). If **lower**: store it and enqueue *all* neighbours
     (light removal re-propagates — this is how breaking a torch darkens the area).

## Display — `Get Illumination %n`

```
brightness = max( skyLight[tile] − globalLight , blockLight[tile] )
```
`globalLight` is the day/night dimmer (0 at noon, larger at night) — so sky-lit areas dim at
night but torch-lit areas don't. Renderers (Tiles/Mobs/Steve) call this per tile/entity.

## Fix cookbook

- **Relight speed:** the `repeat 25` budget in `Process Light Loop`.
- **A block's opacity / glow:** `_BLOCK_DATA[id*21 + 9]` (negative = emits that much light).
- **Night darkness:** whatever drives `globalLight` in `Do Day Night Cycle`.
- **Light falloff:** the `−1` decay step in `Process Light Mod` (the `depth2 += −1` after
  the north-neighbour check).
