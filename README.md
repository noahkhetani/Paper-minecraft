# paper minecraft v2 - optimised

this is paper minecraft v2 with the one giant html file split into a bunch of
smaller files so it loads better and is easier to deal with. play at:
https://paper-minecraft-v2-by-noahmu.netlify.app/

## the files

- **index.html** - entry point, links all the styles + scripts
- **style.css** - the ui + loading screen styling
- **engine.js** - core engine (turbowarp runtime + base85 decoding)
- **data1.js / data2.js / data3.js** - game data + assets, split into 3 chunks
  (each under 20mb)
- **loader.js** - stitches the chunks back together and boots the game

## running it

just open `index.html` in any modern browser.

## why it's split

the original was one 46mb html file. to keep everything under the 20mb limit i
pulled the base85-encoded data chunks out into separate js files. each one
self-executes and injects its data back into the runtime in order, so the game
plays exactly like the original.
