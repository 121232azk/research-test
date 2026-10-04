/**
 * Simple static file server for local development.
 * Serves the project root at http://localhost:3001
 */
import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 3001;
const ROOT = path.resolve();
console.log('[DEV SERVER] Root:', ROOT);
console.log('[DEV SERVER] index.html exists:', fs.existsSync(path.join(ROOT, 'index.html')));

// MIME type mapping
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.eot': 'application/vnd.ms-fontdata',
};

const server = http.createServer((req, res) => {
  const urlPath = req.url && req.url.split('?')[0];
  console.log('[DEV SERVER] Request for:', urlPath);

  if (!urlPath) {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('404 Not Found');
    return;
  }

  let filePath = path.join(ROOT, urlPath);
  if (urlPath === '/') filePath = path.join(ROOT, 'index.html');

  fs.stat(filePath, (err, stats) => {
    if (err) {
      console.log('[DEV SERVER] File not found:', filePath);
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found');
      return;
    }

    if (!stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found');
      return;
    }

    console.log('[DEV SERVER] Serving:', filePath);

    const ext = path.extname(filePath).toLowerCase();
    const mime = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, { 'Content-Type': mime });
    const stream = fs.createReadStream(filePath);
    stream.on('error', (err) => {
      console.log('[DEV SERVER] Stream error:', err.message);
      res.writeHead(500);
      res.end();
    });
    stream.pipe(res);
  });
});

server.listen(PORT, () => {
  console.log(`\n🚀 Server running at http://localhost:${PORT}`);
  console.log('Press Ctrl+C to stop.\n');
});
