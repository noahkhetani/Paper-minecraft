# Mob AI: architecture, movement, targeting, lifecycle

Reverse-engineered from the **Mobs** sprite (expressions quoted from decompiled code,
post-rename names). Combat specifics (damage numbers, `Mob Damaged`, `Attack?`) are in
[combat-and-damage.md](combat-and-damage.md).

## Architecture: central sim + visual clones

Mobs are **not** simulated by their clones. The live-mob table `@_MOB` holds one record per
mob; `Process Mobs` (driven from the Mobs sprite's main loop) iterates it **centrally**:

```
cloneAsId = 1
until cloneAsId > len(@_MOB):
    if type > 0:  MobCount += 1;  repeat tickCount: Process Mob
    elif type == -1 and @_MOB[+1] == 0:  Add To Mob Pool(cloneAsId)   // free the row
    cloneAsId += mobMultiplier
```

- **`mobMultiplier` is the `@_MOB` row stride** (misleading name inherited from `_MobMul`;
  the row is ~21 cells). `cloneAsId` is the row base index.
- `repeat tickCount:` — AI steps scale with the frame budget (`tickCount`), so mob speed
  tracks game speed.
- Sprite **clones are pure renderers**: when a row with `+1 == 0` comes within ~9–11 tiles of
  `cameraX` (±8 of `cameraY`), the sim sets `+1 = 1`, resets the despawn clock
  (`+15 = 999999999`) and creates a clone; the clone start-script copies its row
  (`mobHealth`, `mobType`, size from `@_MOB_DATA[mobDataOffset+3]`, y-offset `+5`) and only
  draws/animates.
- Mobs crossing a portal are moved between chunks via `@_Mob_Chunk_Transfer` triplets
  `[targetChunkSeed, type, tileIndex+5]` — nether portals use `chunkSeed ± 1000000`, end
  portals `± 100000000`; `Process Mobs` re-spawns any triplet matching the current chunk.

## `@_MOB` row fields (full map, offsets confirmed)

| offset | meaning |
|---|---|
| +0 | type id (0 = empty row, −1 = freed) |
| +1 | has-visual-clone flag |
| +2 | tile index (`round(x) + round(y)*levelWidth`) |
| +3 / +4 | x / y |
| +5 | walk direction (±1) |
| +6 | movement state: 0/1 idle-walk, 2 jump, 3.5 mid-jump, 4 falling |
| +7 | state timer |
| +8 | vertical speed (state 4); dragon: flight-phase counter |
| +9 | pending damage (−5 = flash only) |
| +10 | health |
| +11 | aggro-until timestamp |
| +12 | invulnerable-until timestamp |
| +14 | action timer (attack cooldown / fuse / barter timer) |
| +15 | despawn-at timestamp |
| +17 | name-tagged flag |
| +18 | knockback direction |
| +19 | original type (cure) |
| +20 | misc per-type (villager trade id / barter timer / sniffer state) |

## Per-tick flow — `Process Mob`

1. Rideable types (pig 234 w/ carrot-stick 1166, horses 235/240/248–252/280, strider 236
   w/ 1167, ghast 237, …): pressing **E** with the cursor on the mob mounts it
   (`gameMode = "riding…"`, mob row deleted, camera recentred).
2. **Ender Dragon (type in the end arena)** has bespoke AI: circles toward
   `endPortalY`, perch marker in `+14` (timer+999999), contact damage
   `floor(−random(0,1) × defenseMultiplier)` + knockback 0.04, heals +1 HP (10%/tick,
   cap 207) while any end-crystal block (718) exists, shoots fireball projectile 666 every
   `random(5,6)` s (`@Cooldowns[13]`), edge turnaround at x>140 or `random(0,299)==0`.
3. Generic mobs:
   - Named mobs (`+17`) pause beyond 20×15 tiles (no despawn).
   - Pending damage → `Mob Damaged`; death → sink 0.02/tick, row deleted when the 0.3 s
     death window (`+12`) expires.
   - **Despawn:** un-named hostiles beyond `spawnArea` tiles are deleted immediately;
     otherwise once `+15 < realTimeMs`, each tick has a `random(1,15)==5` chance to despawn
     (bosses 124/159/132/210/312/153 and `@Non-Hostile` exempt).
   - Otherwise `Move Pig(type)` (movement for **all** mobs, despite the name) then
     `Mob Damaged` or `Attack?`.

## Movement — `Move Pig %n` + `Decide Next Move %b %b %n`

`Move Pig` first handles per-type behaviors: piglin bartering (gold ingot → wait
`random(2,4)` s → "piglin bartering" loot table, plus 1/85 chance of item 995 and 1/40 of
679×2–4), piglins turn hostile (108→109) within 7 tiles if you wear no gold armor, campfire
smoke (block 941 above) deals `random(0.5,1)`, sniffer digs (35→34) after `random(3,6)` s
with "sniffer" loot, villagers get trade tables assigned, and "statue" types (139, 25, 97,
35, 110, watched Creaking 210, trading villager) don't move at all.

Then the **state machine** on `+6`:
- **state 4 (falling):** `vy −= 0.02` per step, terminal −0.4, `y += vy`; lands when the
  block below is solid (`Is Block P`).
- **states 0/1 (idle/walk):** `Decide Next Move` flips between them (`round(1−state)` /
  `random(0,1)`); walking moves `x += direction × speed`, direction `+5` flips when blocked
  (`floor(0−mobDirection)`).
- **state 2 (jump):** triggered when the block ahead (`tileIndex + direction`) is solid but
  the two blocks above it are clear — the classic 1-block step-up, checked via
  `Is Block P` at `±levelWidth` offsets. `3.5` is the airborne phase.
- **Gravity check first:** if the block below isn't solid → state 4.
- **Aggro/chase:** `Can See Steve?` (line-of-sight walk over tiles) within range sets the
  direction toward Steve (`+5 = ±1`) and `Follow Steve` closes distance; hostiles only act
  while `+11 > realTimeMs` (see combat doc).
- Mobs can **trigger doors/pressure plates**: `Activate Tile_iv(tileIndex, "o"/"t", …)`.

## Fix cookbook

- **Mob walk speed:** the `x += direction × k` step in `Move Pig` (per-state constants).
- **Gravity/terminal velocity:** `−0.02` / `−0.4` in `Move Pig` state 4 (and the same
  constants in the falling branch).
- **Despawn distance/rate:** `spawnArea` (Stage var) and the `random(1,15)==5` roll in
  `Process Mob`.
- **Clone (render) radius:** the `<9`/`<11` × `<8` camera-distance checks in `Process Mob`.
- **Piglin barter loot:** the `random(1,85)`/`random(1,40)` branches in `Move Pig` and the
  "piglin bartering" loot table.
- **Dragon difficulty:** heal rate (`random(0,9)==0`), fireball cadence (`random(5,6)`),
  contact damage in the dragon section of `Process Mob`.
- **Mob AI tick rate:** `repeat tickCount` in `Process Mobs`.
