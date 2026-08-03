# 2D Minecraft — clean HTML player

Runs the **actual Scratch game** (`../extracted-sb3-file/`) in the browser as a small,
self-contained set of files — **not** the 46 MB single-file TurboWarp blob and not
turbowarp.org. The game logic stays as the editable Scratch project; this just provides a
clean, regenerable runtime around it.

## Why it's built this way

The game depends on TurboWarp-only extensions (pen, Lily's *, clipping/blending, etc.), so it
can only run on TurboWarp's engine. TurboWarp doesn't publish that engine as editable npm
packages, so the practical clean option is the open-source **TurboWarp packager** used in
"Plain HTML" (zip) mode: it emits a readable `index.html` + a separate runtime `script.js` +
the project under `assets/` (the project is fetched at runtime from `assets/project.json`).
The result is multi-file and project-separate, so the game stays editable and the build is
reproducible.

## Usage

```bash
npm install            # once
npm run build:player   # zips ../extracted-sb3-file -> packages -> dist/
npm run serve          # serves dist/ at http://127.0.0.1:5050
# or:
npm start              # build + serve
```

Open http://127.0.0.1:5050 and click to start. (Must be served over HTTP — it will not run
from a `file://` URL.)

## Edit loop

1. Edit the game in `../extracted-sb3-file/project.json` (renamed variables + comments make
   this readable; see `../docs/`).
2. `npm run build:player`
3. Reload the page.

## Layout

- `scripts/build-player.mjs` — zips the editable project, runs `@turbowarp/packager`
  (target `zip`), extracts the build into `dist/`.
- `scripts/serve.mjs` — dependency-free static server for `dist/`.
- `dist/` — generated build artifact (`index.html`, `script.js`, `assets/`); safe to delete
  and regenerate.

## Status

Verified: boots and plays the unmodified project end-to-end (main menu → New Game → world
generation → in-game with terrain, player, HUD, inventory).
