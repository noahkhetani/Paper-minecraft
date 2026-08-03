# Paper Minecraft

A 2D Minecraft clone built as a Scratch 3.0 / TurboWarp project. This repo holds the editable
project, a small browser player for running it, and documentation for the systems inside it
(world generation, mobs, combat, redstone, and so on).

The game is a heavily modified version of Griffpatch's *Paper Minecraft*. See
[Credits](#credits).

## Running it

The easiest way is the player in [`player/`](player/), which runs the project as a small set
of files instead of one giant exported blob:

```bash
cd player
npm install
npm start        # builds from extracted-sb3-file/ and serves at http://127.0.0.1:5050
```

You can also open `paper-minecraft.sb3` directly in the [TurboWarp](https://turbowarp.org/)
desktop app or website. It relies on several TurboWarp extensions (`pen`, `localstorage`,
Lily's extensions, etc.), so it won't run in vanilla Scratch.

## Layout

| Path | What's in it |
|------|--------------|
| `extracted-sb3-file/` | The editable project: `project.json` (the block AST) plus all costume/sound assets. This is where game changes are made. |
| `paper-minecraft.sb3` | The same project packed as a `.sb3` for loading in TurboWarp. |
| `player/` | A self-contained browser player. Edit the project, run `npm run build:player`, reload. |
| `tools/` | Python helpers: a block decompiler, the variable-rename engine, and the comment injector. |
| `docs/` | Architecture overview and deep-dives into individual systems, each with a "how to change X" section. |

## Editing the game

All logic lives in `extracted-sb3-file/project.json` as Scratch blocks across 52 sprites.
Global state (the world, inventory, mob and recipe tables) lives on the Stage as flat lists
indexed by tile/chunk rather than 2D arrays.

To read a sprite's logic as pseudocode before changing it:

```bash
python tools/decompile.py Generator "Init Ground Curves"
python tools/decompile.py Cursor --hat "update health"
```

Start with [`docs/architecture.md`](docs/architecture.md) for a map of which sprite owns what,
then the per-system docs under [`docs/systems/`](docs/systems/).

## Credits

- Original *Paper Minecraft* by [Griffpatch](https://scratch.mit.edu/users/griffpatch/).
- This modified version credits @ChessProking-tm and Coddenort (per the in-game about screen),
  with additional code from Griffpatch, Gw14sneddon_jack2, Redhorse26_1, Jurassic_World123,
  and jacker114.
- *Minecraft* is a trademark of Mojang Studios. This is an unofficial fan project.
