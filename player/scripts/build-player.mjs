/**
 * Build the clean HTML player.
 *
 * Pipeline:
 *   1. Zip the *editable* project from ../extracted-sb3-file/ into an in-memory .sb3.
 *   2. Feed it to @turbowarp/packager with target "zip" (Plain HTML — separate files,
 *      NOT the 46 MB single-file blob). The packager inlines the TurboWarp engine + the 11
 *      extensions, so the output is self-contained and offline-capable.
 *   3. Extract the resulting zip into ./dist/ so any static server can serve index.html.
 *
 * Edit loop: change extracted-sb3-file/project.json -> `npm run build:player` -> reload.
 */
import fs from 'node:fs';
import path from 'node:path';
import pkg from '@turbowarp/packager';
import JSZip from '@turbowarp/jszip';

const { Packager, loadProject } = pkg;

const PLAYER_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, '$1'), '..');
const ROOT = path.resolve(PLAYER_DIR, '..');
const EXTRACTED = path.join(ROOT, 'extracted-sb3-file');
const OUT = path.join(PLAYER_DIR, 'dist');

async function buildSb3FromExtracted() {
  const zip = new JSZip();
  let n = 0;
  for (const name of fs.readdirSync(EXTRACTED)) {
    const full = path.join(EXTRACTED, name);
    if (fs.statSync(full).isFile()) {
      zip.file(name, fs.readFileSync(full));
      n++;
    }
  }
  console.log(`  added ${n} files to in-memory .sb3`);
  return zip.generateAsync({ type: 'uint8array' });
}

async function main() {
  console.log('1/4  Zipping editable project from extracted-sb3-file/ ...');
  const sb3 = await buildSb3FromExtracted();

  console.log('2/4  Loading project into packager (fetches extensions) ...');
  let lastPct = -1;
  const project = await loadProject(sb3, (type, a, b) => {
    if (type === 'assets' && b) {
      const pct = Math.floor((a / b) * 100);
      if (pct !== lastPct && pct % 25 === 0) {
        console.log(`     assets ${pct}%`);
        lastPct = pct;
      }
    }
  });

  console.log('3/4  Packaging (target=zip, Plain HTML) ...');
  const packager = new Packager();
  packager.project = project;
  packager.options.target = 'zip';
  const result = await packager.package();
  console.log(`     -> ${result.filename} (${result.type}, ${(result.data.length / 1e6).toFixed(1)} MB)`);

  console.log('4/4  Extracting build into dist/ ...');
  const outZip = await JSZip.loadAsync(result.data);
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });
  const names = Object.keys(outZip.files);
  for (const name of names) {
    const entry = outZip.files[name];
    const dest = path.join(OUT, name);
    if (entry.dir) {
      fs.mkdirSync(dest, { recursive: true });
      continue;
    }
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, await entry.async('nodebuffer'));
  }
  console.log(`Done. Wrote ${names.length} files to ${OUT}`);
  console.log('Top-level output:', fs.readdirSync(OUT).join(', '));
}

main().catch((e) => {
  console.error('BUILD FAILED:', e);
  process.exit(1);
});
