/**
 * Minimal static server for the built player in ./dist (no dependencies).
 * The packaged "zip" build fetches ./assets/project.json at runtime, so it must be served
 * over HTTP — it will not run from a file:// URL.
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const PLAYER_DIR = path.resolve(
  path.dirname(new URL(import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, '$1'),
  '..',
);
const DIR = path.join(PLAYER_DIR, 'dist');
const PORT = Number(process.env.PORT) || 5050;

const TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.otf': 'font/otf',
  '.ttf': 'font/ttf',
};

if (!fs.existsSync(DIR)) {
  console.error('dist/ not found — run `npm run build:player` first.');
  process.exit(1);
}

http
  .createServer((req, res) => {
    let p = decodeURIComponent((req.url || '/').split('?')[0]);
    if (p === '/') p = '/index.html';
    const fp = path.join(DIR, p);
    if (!fp.startsWith(DIR) || !fs.existsSync(fp) || fs.statSync(fp).isDirectory()) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(fp)] || 'application/octet-stream' });
    fs.createReadStream(fp).pipe(res);
  })
  .listen(PORT, '127.0.0.1', () => {
    console.log(`Player running at http://127.0.0.1:${PORT}`);
  });
