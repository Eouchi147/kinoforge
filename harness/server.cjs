// Tiny static server for the render harness. Serves /home/claude/vp (or ROOT) so scenes can import
// /harness/kit/*.js and /harness/node_modules/three/... as ES modules over http (file:// blocks modules).
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = process.env.KF_ROOT || path.resolve(__dirname, '..');
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.glsl': 'text/plain', '.txt': 'text/plain',
  '.hdr': 'application/octet-stream', '.bin': 'application/octet-stream', '.gltf': 'model/gltf+json', '.glb': 'model/gltf-binary',
};

function start(port = 0) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      try {
        const url = new URL(req.url, 'http://x');
        let p = decodeURIComponent(url.pathname);
        if (p.endsWith('/')) p += 'index.html';
        const file = path.join(ROOT, p);
        if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
        fs.stat(file, (err, st) => {
          if (err || !st.isFile()) { res.writeHead(404); return res.end('not found: ' + p); }
          res.writeHead(200, { 'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*' });
          fs.createReadStream(file).pipe(res);
        });
      } catch (e) { res.writeHead(500); res.end(String(e)); }
    });
    server.listen(port, '127.0.0.1', () => resolve({ server, port: server.address().port }));
  });
}

module.exports = { start, ROOT };
if (require.main === module) {
  start(Number(process.argv[2] || 8765)).then(({ port }) => console.log(`serving ${ROOT} on http://127.0.0.1:${port}/`));
}
