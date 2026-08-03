# Player physics & damage intake (Steve / Steve Legs / Health / Oxygen)

Reverse-engineered from the blocks (expressions quoted from decompiled code, post-rename
names). Combat damage *dealt* by the player is in
[combat-and-damage.md](combat-and-damage.md); this covers movement and everything that
hurts the player.

## Movement & physics (Steve::SteveTick, ~30 Hz, scaled by `tickCount`)

- **Base walk speed:** `steveSpeed = 0.15` tiles/step, then `Calculate Speed` multipliers.
- **Horizontal motion:** `_sx = _sx*0.6 ± 0.05` per step — friction 0.6, acceleration 0.05.
- **Knockback:** integrated into x each step and decayed `knockback *= 0.85`, zeroed below
  0.05 (this is what mob hits feed via `Knock Steve Back_P`).
- **Jump:** buffered 0.05 s (`doJump = timer + 0.05`); grounded jump sets `_sy = 0.1`.
  Double-tap jump within 0.3 s toggles fly in creative (`IsFlyMode`), always-fly on ghast.
- **Collision probes** at y-offsets −0.15 / −0.6 / +0.4 / +0.9 / −1.5 via `getTile_S` +
  `isBlock_S`; **half-tile step-up** raises `ly += 0.5`; wall contact nudges `lx += 0.999`
  and arms an `onWall` timer (0.2 s).
- **Swimming:** holding **R** in water (2 water cells, not sneaking/boat/riding) sets
  `Swimming? = "y"`.
- Standing in water/powder-snow rain (weather 3/5 with sky light > 12) removes the Fire effect.
- Respawn teleports to `respawnIndex` (bed) else `worldSpawn`:
  `x = 0.5 + (idx−1) mod levelWidth`, `y = 0.85 + (idx−1)/levelWidth`.

### Terrain speed table (`Calculate Speed`, multiplicative)

| condition | × |
|---|---|
| elytra flying | fixed 0.30 |
| soul sand/soil (257/1185) | 0.6 (Soul Speed boots: **1.45**) |
| end stone (675/692) + enderite boots | 1.45 |
| hay 561 | 0.3 · cobweb-ish 410 | 0.5 · 246 w/o Weaving | 0.1 |
| 287 (speed path) | 1.5 |
| sneaking / shield up / eating | 0.3 |
| Slowness | 0.65 · Speed potion | 1.5 |
| minecart: on rail 1.3, off rail 0.1 |
| swimming: in water 1.3, out 0.1 |
| boat: ice 1.8, water 1.5, land 0.1 |
| riding: pig 0.05, ghast 0.7, camel 1.0, horses … |

Armor slots in `@_INV`: **73 helmet, 75 chest, 77 leggings, 79 boots** (item id at the odd
index, durability at the even one).

## Fall damage (`Calculate Fall Damage` + application in `loopTicks`)

Computed on landing, from fall distance `d = floor(ly − fallHeight_s)`:

```
damage = d + 4                              // base (so ~4 blocks are safe)
hay bale (561):        floor((d+4) * 0.3)
Feather Falling boots: floor((d+4) * 0.7)
pointed dripstone 1178: floor(d * 1.7) + 4
slime 556 (not holding down) / boat / nautilus: 0
powder snow 1419: no damage (block becomes 1420)
```
Skipped entirely while **elytra-flying**, during the **mace-smash window**
(`Mace Y = realTimeMs + 0.5` set on a falling mace hit — the mace cancels your fall damage),
and after a wind-charge bounce (`Breeze Y`).

**Application:** `health += damage × resistanceMultiplier` → fall damage **bypasses armor**
(`defenseMultiplier` unused) but respects Resistance. Surviving a >123-block fall grants
advancement 24.

## Contact hazards (`In Lava %s %s %b` — misnamed: handles all standing-in damage)

- Hazard strength is **`_BLOCK_DATA[tile*21 + 14]`** — the same "damage" field weapons use.
  Cactus (11) and magma-without-Frost-Walker force 1; **void** (below y 0) adds +20.
- Immunity: Fire Resistance potion (lava/fire), leather armor piece vs powder snow,
  strider riding (lava — it floats: `_sy = 0.1`, hop 0.36 with space).
- On first contact: `health += floor(−t × defenseMultiplier)` (armor helps here),
  `armorDamage += 1`, `broadcast fire` for lava/fire, `update health`.
- Then periodic: an `InLava` counter accumulates `tickCount` per tick and re-damages when it
  exceeds 16 (magma: 26), resetting by −50 (magma/cactus −25) — i.e. roughly every 0.5–1.7 s.
- Death messages set here: "was pricked to death" (cactus/berry 11/410/412), "died in the
  void", "tried to swim in lava".

## Air / drowning / suffocation (`Can Breath? %s` + Oxygen HUD)

- `_BLOCK_DATA[tile*21 + 7]` ∈ {`.`, `D`} marks unbreathable fluid at head height.
- Air starts at 22 bubbles; drains `0.04 × tickCount` per tick; each wrap below 0 deals
  **−2 HP ("drowned")**. Prevented by turtle helmet (helmet slot `@_INV[73] == 1327`),
  Water Breathing, Conduit Power, or Breath of the Nautilus.
- **Suffocation** (head inside a solid block, `+3 == "Y"`, excluding the `+10 == "11"`
  marker class): drains at 0.0666 and deals **−1 HP ("suffocated in a wall")**, also burning
  a golden heart if present.
- The Oxygen sprite is display-only (`Update Air`: costume = bubble count at x100,y−91).

## Health pipeline recap (see combat doc for details)

All damage writers mutate `health` directly then `broadcast "update health"`; the Health
sprite burns absorption (`goldenHearts`) first, plays hurt flash/sound, may spawn silverfish
under "Infested", and animates the bar. Armor enters as `defenseMultiplier` (contact + mob
damage), `resistanceMultiplier` scales fall damage and potion resistance.

## Fix cookbook

- **Walk speed:** `steveSpeed = 0.15` at the top of `SteveTick`; per-terrain multipliers in
  `Calculate Speed`.
- **Jump height:** `_sy = 0.1` (jump impulse) in `SteveTick`.
- **Fall damage:** the `+ 4` safe-fall offset and surface multipliers in
  `Calculate Fall Damage`; the `× resistanceMultiplier` application in `loopTicks`.
- **Knockback feel:** decay `0.85` and deadzone `0.05` in `SteveTick`.
- **Lava/contact damage rate:** the `>16` threshold and `−50` reset in `In Lava`.
- **Drowning speed/damage:** `0.04` drain and `−2` HP in `Can Breath?`.
- **Hazard damage per block:** `_BLOCK_DATA[blockId*21 + 14]` (set in Tiles' item builder).
- **Swim key:** the **R** check in `Steve::Tick`.
