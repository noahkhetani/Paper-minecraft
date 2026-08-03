# Making changes

## Run it

```bash
cd player
npm install     # once
npm start       # builds from the project and serves at http://127.0.0.1:5050
```

Open the URL and click to start. It has to be served over HTTP, not opened as a `file://`
path. The build lands in `player/dist/`, which is disposable — it's regenerated every build.

## Edit loop

Game logic is in `extracted-sb3-file/project.json` (the Scratch blocks). After editing:

```bash
cd player && npm run build:player
# reload the browser
```

## Where things live

Most changes fall into a few buckets:

- **Gameplay/logic** (damage numbers, spawn rates, mechanics): usually a constant in the
  relevant sprite's blocks or one of the data tables. Start from `docs/data-schemas.md` and
  the per-system docs under `docs/systems/`.
- **Bugs**: find the sprite that owns the behaviour (`docs/architecture.md`), decompile the
  block with `tools/decompile.py`, and trace it.
- **Visuals/assets**: costumes are the PNG/SVG files in `extracted-sb3-file/`, referenced by
  hash in each target's `costumes` list.
- **New features**: bigger ones touch several sprites; the architecture doc shows the seams.

## Reading the blocks

`project.json` is a large block AST, so read it through the decompiler rather than by hand:

```bash
python tools/decompile.py Cursor "Get Damage %b"
python tools/decompile.py Generator "Init Ground Curves"
```

Variables have been renamed from the original cryptic names (`_ScrX` → `cameraX`, etc.); the
full mapping is in `docs/variable-glossary.md`. Renames are applied by id with
`tools/rename_vars.py`, which never changes behaviour.

## Safety net

`tools/rename_vars.py --apply` backs up `project.json` to `project.json.bak` before writing,
and the untouched original is preserved as `paper-minecraft.sb3`.
