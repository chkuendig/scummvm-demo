// Event-recorder replay regression test.
//
// Seeds the golden recording (ftdemo.r00, Full Throttle DOS demo) into
// IndexedDB, boots ScummVM in --record-mode=playback, and asserts that the
// recorder's built-in screenshot comparison passes: the recording stores
// framebuffer MD5s, and on replay the engine logs
//   playback:action="Check screenshot" ... result = success|fail
// PASS requires at least one "success" and zero "fail" within the window.
//
// Requires: a --enable-eventrecorder build served (with its data dir) by
// serve.js on 127.0.0.1:8232, game data reachable via /data/games (CDN
// baseUrl), and playwright + chromium installed.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REC = path.join(__dirname, 'ftdemo.r00');
const URL_BASE = process.env.SCUMMVM_URL || 'http://127.0.0.1:8232';
const TIMEOUT_S = parseInt(process.env.REPLAY_TIMEOUT_S || '600', 10);

(async () => {
  const recB64 = fs.readFileSync(REC).toString('base64');
  const browser = await chromium.launch({
    headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

  let successes = 0, failures = 0, loaded = false;
  const log = [];
  const allConsole = [];   // ring buffer of everything, dumped on failure
  page.on('console', (m) => {
    const t = m.text();
    allConsole.push(t.slice(0, 200));
    if (allConsole.length > 400) allConsole.shift();
    if (/playback:action/.test(t)) log.push(t.slice(0, 160));
    if (/"Load File" result=success/.test(t)) loaded = true;
    if (/Check screenshot.*result = success/.test(t)) successes++;
    if (/Check screenshot.*result = fail/.test(t)) failures++;
  });
  page.on('pageerror', (e) => allConsole.push('PAGEERROR: ' + e.message.slice(0, 200)));
  page.on('requestfailed', (r) => allConsole.push('REQFAIL: ' + r.url().slice(0, 150) + ' ' + (r.failure() || {}).errorText));
  page.on('crash', () => { console.error('PAGE CRASHED'); process.exit(1); });

  // Seed IndexedDB from a same-origin HTML page (a non-HTML resource such as
  // favicon.ico has no IndexedDB access and throws SecurityError).
  await page.route('**/__seed', (r) =>
    r.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><html><body>seed</body></html>' }));
  await page.goto(`${URL_BASE}/__seed`, { waitUntil: 'load', timeout: 60000 });
  const seeded = await page.evaluate((b64) => new Promise((res) => {
    const bin = atob(b64);
    const buf = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    const rq = indexedDB.open('/home/web_user', 21);
    rq.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('FILE_DATA')) {
        const s = db.createObjectStore('FILE_DATA');
        s.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
    rq.onerror = () => res('open-error');
    rq.onsuccess = (e) => {
      const db = e.target.result;
      const tx = db.transaction(['FILE_DATA'], 'readwrite');
      const s = tx.objectStore('FILE_DATA');
      const now = new Date();
      s.put({ timestamp: now, mode: 16877 }, '/home/web_user');
      s.put({ timestamp: now, mode: 16877 }, '/home/web_user/saves');
      s.put({ timestamp: now, mode: 33188, contents: buf }, '/home/web_user/saves/ftdemo.r00');
      tx.oncomplete = () => res('ok');
      tx.onerror = () => res('tx-error');
    };
  }), recB64);
  if (seeded !== 'ok') { console.error(`SEED FAILED: ${seeded}`); process.exit(1); }

  await page.goto(
    `${URL_BASE}/scummvm.html#--debugflags=eventrec%20--debuglevel=1%20--record-mode=playback` +
    `%20--record-file-name=ftdemo.r00%20--path=/data/games/ft-dos-demo-en%20scumm:ft`,
    { waitUntil: 'load', timeout: 120000 });

  const deadline = Date.now() + TIMEOUT_S * 1000;
  while (Date.now() < deadline) {
    await page.waitForTimeout(5000);
    if (failures > 0) break;              // fail fast
    if (successes >= 1 && loaded) break;  // enough evidence of a working replay
  }
  await page.screenshot({ path: 'replay-final.png' }).catch(() => {});
  await browser.close();

  console.log('--- playback log ---');
  log.slice(0, 40).forEach((l) => console.log(l));
  console.log(`loaded=${loaded} screenshot checks: success=${successes} fail=${failures}`);
  if (!loaded || failures > 0 || successes < 1) {
    console.log('--- full console (last 400 lines) ---');
    allConsole.forEach((l) => console.log('| ' + l));
  }
  if (!loaded) { console.error('FAIL: recording never loaded'); process.exit(1); }
  if (failures > 0) { console.error('FAIL: screenshot mismatch during replay'); process.exit(1); }
  if (successes < 1) { console.error('FAIL: no screenshot check passed within timeout'); process.exit(1); }
  console.log('PASS: replay reproduced the recorded session');
})();
