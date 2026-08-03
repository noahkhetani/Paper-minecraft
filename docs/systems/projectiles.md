# Projectiles: bow, thrown items, tridents

Reverse-engineered from Cursor (launch) + Tiles (flight). Expressions quoted from decompiled
code, post-rename names.

## Core design: projectiles are `@_HARVEST` entities

There is no separate projectile system. Launching pushes a 6-field record onto `@_HARVEST`
— the same list used for dropped items — and the Tiles sprite simulates it:

```
[x, y, itemId, count, vx, vy]
spawn:    x = _x + 0.9·sin(aim),  y = _y + 0.3 + 0.9·cos(aim)   (aim = Steves Head direction)
```
(Dropped-item records use `vy = -999` as a marker; real vy means "in flight".)

## Charging & firing (Cursor)

- **`Do Bow Action`** — while holding the bow: `BowPull += 0.125 × tickCount`, capped at
  **2.5** (~0.7 s to full charge). Only starts if `Got any arrows` finds ammo.
- **`Got any arrows`** — scans `@_INV` slots 36→1 for arrow item **131**; creative or an
  "infinity" bow returns 99999 (no ammo consumed on fire is handled by that fake index).
  Tridents skip the check.
- **`Do Shoot Bow (projectileType)`** — blocked if the diagonal launch tile is solid.
  - Consumes one arrow + bow durability (`Damage Tool`).
  - **Power enchant: `BowPull += 1`** (others `+= 0.5`) — a flat charge bonus.
  - Launch velocity **`v = BowPull × 0.3 × (sin, cos)(aim)`** → full-charge arrow speed 0.9,
    Power bow 1.05.
  - **Trident (held 1573):** right-click Riptide (`broadcast Riptide`, 1 s `@Cooldowns[7]`);
    thrown → projectile **1309**, and the *item itself* leaves the inventory (slot → `#`),
    carrying its durability in the record's count field.
- **`Do Throw Projectile (id)`** — snowballs/eggs/pearls/potions etc.: fixed speed
  **0.65**, one item consumed, blocked when the cursor tile is solid.

## Flight & impact (Tiles::`Do Arrow In Flight %s`)

- **Gravity: `vy −= 0.04` per step**; position integrates (vx, vy); arrows stick into solid
  blocks (`StuckIn`).
- **Mob hit:** scans `@_MOB` for a mob whose tile (+2, or +levelWidth above for tall
  hostiles) matches the projectile's tile. Damage written to pending-damage `+9`:
  - **trident (1309): `ceiling(8 × √(vx²+vy²))`**
  - **everything else: `ceiling(4 × √(vx²+vy²))`**
  → damage is literally the impact speed; a falling arrow hits harder. Full-charge bow ≈ 4,
  Power bow ≈ 5 (+ whatever gravity added).
- Immune: mob 193, and the **wither (159) while health < 200** (shield phase).
- Aggro conversions on hit: piglin 108→109, 105→196, 37→195 (same as melee).
- Special arrow **1422** bursts into item 1311 × `random(3,11)` on impact instead of damage.

## Fix cookbook

- **Bow charge speed / cap:** `0.125` and `2.5` in `Do Bow Action`.
- **Bow power:** the `× 0.3` velocity factor in `Do Shoot Bow`, or the impact multipliers
  `8`/`4` in `Do Arrow In Flight`.
- **Power enchant strength:** the `BowPull += 1` branch in `Do Shoot Bow`.
- **Arrow gravity (arc):** `sy += −0.04` at the top of `Do Arrow In Flight`.
- **Thrown-item speed:** `0.65` in `Do Throw Projectile`.
- **Riptide cooldown:** `@Cooldowns[7] = realTimeMs + 1` in `Do Shoot Bow`.
- **What counts as ammo:** item id `131` in `Got any arrows`.
