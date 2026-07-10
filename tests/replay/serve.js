// Minimal static file server with correct HTTP Range support, to faithfully
// mimic the production (nginx) server for the Emscripten virtual-fs.
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = process.env.ROOT || process.cwd();
const PORT = parseInt(process.env.PORT || '8232', 10);

const MIME = {
  '.html': 'text/html', '.js': 'text/javascript', '.wasm': 'application/wasm',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.dat': 'application/octet-stream', '.zip': 'application/zip',
  '.css': 'text/css', '.ico': 'image/x-icon',
};

http.createServer((req, res) => {
  try {
    const urlPath = decodeURIComponent(req.url.split('?')[0]);
    let filePath = path.join(ROOT, urlPath);
    if (!filePath.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
    let stat;
    try { stat = fs.statSync(filePath); } catch { res.writeHead(404); return res.end('Not found'); }
    if (stat.isDirectory()) { filePath = path.join(filePath, 'index.html'); try { stat = fs.statSync(filePath); } catch { res.writeHead(404); return res.end(); } }

    const type = MIME[path.extname(filePath).toLowerCase()] || 'application/octet-stream';
    const range = req.headers.range;
    const baseHeaders = { 'Content-Type': type, 'Accept-Ranges': 'bytes' };

    if (range) {
      const m = /bytes=(\d*)-(\d*)/.exec(range);
      let start = m && m[1] ? parseInt(m[1], 10) : 0;
      let end = m && m[2] ? parseInt(m[2], 10) : stat.size - 1;
      if (isNaN(start)) start = 0;
      if (isNaN(end) || end >= stat.size) end = stat.size - 1;
      if (start > end || start >= stat.size) { res.writeHead(416, { 'Content-Range': `bytes */${stat.size}` }); return res.end(); }
      res.writeHead(206, { ...baseHeaders, 'Content-Range': `bytes ${start}-${end}/${stat.size}`, 'Content-Length': end - start + 1 });
      if (req.method === 'HEAD') return res.end();
      fs.createReadStream(filePath, { start, end }).pipe(res);
    } else {
      res.writeHead(200, { ...baseHeaders, 'Content-Length': stat.size });
      if (req.method === 'HEAD') return res.end();
      fs.createReadStream(filePath).pipe(res);
    }
  } catch (e) {
    res.writeHead(500); res.end(String(e));
  }
}).listen(PORT, '127.0.0.1', () => console.log(`serving ${ROOT} on http://127.0.0.1:${PORT}`));
