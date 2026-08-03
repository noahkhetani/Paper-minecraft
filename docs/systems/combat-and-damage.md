# Combat & damage math

Reverse-engineered from the blocks (all expressions quoted from decompiled code, post-rename
names). Player→mob lives in **Cursor**; mob→player in **Mobs**; health display/absorption in
**Health**. `realTimeMs` is a real-time seconds clock (despite the name); `@_MOB` is the live
mob table (one record per mob, stride = `mobMultiplier` variable at runtime; fields below).

## `@_MOB` row fields (offsets confirmed in code)

| offset | meaning |
|---|---|
| +0 | mob type id |
| +2 | mob instance id (used by `@_Explode`, harvest drops) |
| +3 / +4 | x / y (tiles) |
| +9 | **pending damage** — written by attacker, consumed by `Mob Damaged`; the special value `-5` means "interaction flash, no HP loss" |
| +10 | health |
| +11 | aggro-until timestamp (hostiles only attack while `> realTimeMs`) |
| +12 | invulnerable-until timestamp (i-frames) |
| +14 | per-mob action timer (attack cooldown / creeper fuse / blaze shoot delay) |
| +17 | name-tagged flag (name tag = item 1427; prevents despawn) |
| +18 | knockback direction on the mob (+1 = pushed right, set by `Hit Mob`) |
| +19 | original type (used to cure zombie villagers back) |

## Player → mob (melee)

Chain: click on mob → `Cursor::Hit Mob %s %b (mobIdx, falling?)`:

1. **Shield gate:** everything is skipped while `Using Shield != 0` (you can't attack while blocking).
2. ~500 lines of **item-on-mob interactions** run first (name tag, shears, buckets, dyes,
   saddles, brush, flint-and-steel on creeper → instant explosion, etc.). Each ends with
   `stop this script` — an interaction consumes the click instead of an attack.
3. **Swing rate limit:** `if timer < elapse stop; elapse = timer + 0.5` → max ~2 swings/sec,
   plus `justInteractedWithMob` grace (0.5 s) after interactions.
4. **I-frames:** only applies damage if `@_MOB[idx+12] < realTimeMs`.
5. Calls **`Get Damage (falling?)`** (below), then:
   - wind-burst mace + falling → `broadcast Wind Charge`
   - falling & not mace → crit particles (`@Crit particle`, 12–15 of them) + crit sound
   - **`@_MOB[idx+9] = damage`** (pending damage)
   - `@_MOB[idx+18] = ±1` — knockback direction: `+1` if Steve is left of the mob (`$_x < @_MOB[idx+3]`)
   - `Damage Tool(0)` — durability loss per swing (see below)

The **Mobs** sprite consumes `+9` in `Mob Damaged` (each mob clone polls its own row).

## The damage formula — `Cursor::Get Damage %b (falling?)`

```
data   = _BLOCK_DATA[heldCostume*blockDataStride + 10]    // +10: 1 ⇔ item is a damageable tool/weapon
Damage = 1 + (_BLOCK_DATA[heldCostume*blockDataStride + 14] - 1) * (data == 1)
```
→ **base damage is `_BLOCK_DATA[itemId*21 + 14]`**; bare hand / non-weapons = 1.

**Attack cooldown** (`attackCooldown = realTimeMs + X`, checked by the swing loop):
| weapon | X (s) |
|---|---|
| any " sword" | 0.6 |
| wooden/stone axe (ids 85, 83) | 1.2 |
| copper / iron axe | 1.1 |
| gold (104) / diamond / netherite axe | 0.6 |
| Mace | 1.67 |
| spear while `chargingSpearAttack` | 0 (no cooldown) |
| everything else | 0.6 |

**Modifiers, in order:**
- **Crit** (falling, not a mace): `Damage = Damage + Damage/2` (×1.5).
- **Mace smash** (falling, holding mace): regular mace adds `round(fallHeight)` where
  fallHeight = Steve's `fallHeight_s − ly`; **enchanted mace (id 1668)**:
  `Damage = round(Damage×1.5) + round(fallHeight + 3)`. (Fall > 50 → achievement 69;
  landing window `Mace Y = realTimeMs + 0.5`.)
- **Strength potion:** `+2 × level`; **Weakness:** `−4 × level`.
- **Charged spear:** `+ elytraSpeed×25` while elytra-flying, else `+ steveSpeed×15`.
- Clamp: `< 1 → 0` (applied both before and after modifiers).

## Durability — `Cursor::Damage Tool %s`

Skipped entirely in creative. Only items with `_BLOCK_DATA[id*21+10] == 1` take damage.
Durability is stored in **`@_INV[slot*2]`** (the even cell of the slot pair):
```
@_INV[slot*2] -= random(1, random(1,2))     // −1 with p=0.75, −2 with p=0.25
```
At `< 1` the item is deleted: `@_INV[slot*2−1] = "#"`, count 0 (tool breaks).

## Mob damage intake — `Mobs::Mob Damaged`

- Skip if i-framed (`+12 > realTimeMs`) or already dead (`+10 < 1`).
- `mobHealth −= @_MOB[+9]` unless `+9 == -5` (interaction flash only). `+9` is then reset to 0.
- **On survive:** i-frames `+12 = realTimeMs + 0.8`, hurt sound.
- **On death** (`health < 1`): `Death Harvest(cloneAsId, overkill = health < −20)` (drops/XP),
  brief `+12 = +0.3`, death sound, "Monsters Hunted" advancement within distance 4.
- Notable specials: slime (154) splits into 2–3 × type 194; sheared-state conversions at
  health < 9 (97→25, 96→6); wolf-style anger conversions (105→196 and all 105s within 6
  tiles aggro to 197, 5→104, 37→195 within 5, 218→107); blaze (89) sets shoot delay
  `+14 = realTimeMs + random(1,3)`; warden-kill advancement (199) within 16.

## Mob → player — `Mobs::Attack? %n (type)`

Runs only for hostiles (`type > 99` and not in `@Non-Hostile`), while aggro'd
(`@_MOB[+11] > realTimeMs`), and never in creative/spectator.

- **Ranged mobs** (`@Mobs_That_Shoot` pairs `[mobType, projectileId]`, plus 132/199): shoot
  via `Shoot Attack` when outside melee range (|Δx| ≥ 1.5 or |Δy| ≥ 1.8), on their `+14` timer.
- **Evoker (134):** 1/14 roll → summon vex (1592) if `MobCount < 26`; else 1/70 roll →
  fang trap (block 776) under the player within distance 12.
- **Creeper (101 / charged 208):** fuse starts within 1.5×1.8 (`+14 = realTimeMs + 1.5`,
  fuse sound); cancels if player escapes beyond 5×4; on expiry adds to `@_Explode`
  (power 3, charged 5) and sets own health 0.
- **Melee:** within **|Δx| < 1.4 and |Δy| < 1.8**, swing timer `+14 = realTimeMs + 1.5`:
  - If `Using Shield`: `broadcast DAMAGE_SHIELD` — **no health loss** (shield takes it).
  - Else: `health += floor(random(−lo,−hi) × defenseMultiplier)` — per-type damage ranges
    (e.g. types 109/123/209 roll −5..−8), **armor is applied as `defenseMultiplier`** and
    armor durability takes `armorDamage = random(3,5)`.
  - Knockback: `Knock Steve Back_P(left?, amount)` → `knockback ± amount` (0.2 typical,
    0.5 for heavy hitters); Steve's movement integrates `knockback`.
  - Sets `Death message = "was slain by a <mob name>"` pre-emptively.

## Health pipeline (player)

Damage writers mutate `health` directly, then `broadcast "update health"`. The **Health**
sprite receiver: absorption first — if `normalMaxHealth + goldenHearts > health`, the
difference comes out of `goldenHearts` (clamped ≥ 0), then `normalMaxHealth = health −
goldenHearts`; on a decrease it plays the hurt sound/flash, can spawn 1–3 silverfish (206)
under the "Infested" effect (10% roll), and animates the heart bar. Death/respawn is driven
by the `Death` state elsewhere (Stage Sprite / Save Game).

## Fix cookbook

- **Change a weapon's base damage** (e.g. mace): edit `_BLOCK_DATA[itemId*21 + 14]` — set at
  build time by Tiles' `Dup:`/`Duplicate Traits` init calls (search the item's name there);
  mace = item 1626, enchanted mace = 1668, wind-burst = 1723.
- **Change attack speed:** the cooldown constants in `Cursor::Get Damage %b` (0.6/1.1/1.2/1.67).
- **Change crit multiplier:** `Damage + (Damage/2)` in `Get Damage`.
- **Change mace smash scaling:** the falling branch of `Get Damage` (`round(fallHeight)` / `+3`).
- **Change a mob's melee damage:** its `random(−lo,−hi)` roll in `Mobs::Attack? %n`.
- **Change mob attack rate:** the `+14 = realTimeMs + 1.5` in `Attack?`.
- **Change player i-frames on mobs:** `+12 = realTimeMs + 0.8` in `Mob Damaged`.
- **Change tool durability loss:** `random(1, random(1,2))` in `Cursor::Damage Tool %s`.
- **Change creeper fuse/power:** fuse `1.5` s and `@_Explode` power 3/5 in `Attack?`.
