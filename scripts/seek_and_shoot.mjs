// Seek-and-shoot K-line frames from a logged-in YouTube session via CDP.
// Usage: node shot.mjs <videoId> <outDir> <t1,t2,...>   (times in seconds)
// Saves <outDir>/<t>.jpg per anchor. Prints one JSON line per anchor.
import { writeFileSync, mkdirSync } from 'node:fs';

const [videoId, outDir, anchorsCsv] = process.argv.slice(2);
const anchors = anchorsCsv.split(',').map(Number);
mkdirSync(outDir, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const created = await fetch(
  'http://127.0.0.1:9222/json/new?' +
    encodeURIComponent('https://www.youtube.com/watch?v=' + videoId + '&t=' + anchors[0] + 's'),
  { method: 'PUT' }
).then((r) => r.json());
const ws = new WebSocket(created.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let seq = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
};
const send = (method, params = {}) =>
  new Promise((res) => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });

async function evaluate(expression, awaitPromise = false, timeout = 20000) {
  const r = await send('Runtime.evaluate', {
    expression, awaitPromise, returnByValue: true, timeout,
  });
  if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 300));
  return r.result?.result?.value;
}

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });

// wait for the player (some videos stall cold: nudge with a click + play())
let ok = false;
for (let i = 0; i < 40 && !ok; i++) {
  await sleep(1500);
  ok = await evaluate(`!!document.querySelector('video') && document.querySelector('video').readyState >= 1`).catch(() => false);
  if (!ok && i % 6 === 5) {
    const pt = await evaluate(`(() => { const v = document.querySelector('video'); if (!v) return null; const r = v.getBoundingClientRect(); return { x: r.x + r.width / 2, y: Math.max(10, r.y + r.height / 2) }; })()`).catch(() => null);
    if (pt) {
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: pt.x, y: pt.y, button: 'left', clickCount: 1 }).catch(() => {});
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: pt.x, y: pt.y, button: 'left', clickCount: 1 }).catch(() => {});
    }
    await evaluate(`document.querySelector('video')?.play().catch(() => {})`).catch(() => {});
  }
}
if (!ok) { console.log(JSON.stringify({ error: 'player-not-ready' })); process.exit(1); }

// theater mode (wide player) + force hd1080 + park the mouse so controls fade
await evaluate(`(() => {
  const b = document.querySelector('.ytp-size-button'); if (b) b.click();
  const p = document.querySelector('#movie_player');
  try { p.setPlaybackQualityRange('hd1080', 'hd1080'); } catch (e) {}
  return true;
})()`).catch(() => {});
await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 1599, y: 4 }).catch(() => {});
await sleep(1200);

async function clearAd() {
  for (let i = 0; i < 12; i++) {
    const ad = await evaluate(`!!document.querySelector('.ad-showing')`).catch(() => false);
    if (!ad) return true;
    await evaluate(`(() => { const b = document.querySelector('.ytp-skip-ad-button, .ytp-ad-skip-button-modern, .ytp-skip-ad-button__text'); if (b) { b.click(); return 'clicked'; } return 'wait'; })()`).catch(() => {});
    await sleep(2500);
  }
  return false;
}

for (const t of anchors) {
  try {
    await clearAd();
    const got = await evaluate(`(async () => {
      const v = document.querySelector('video');
      v.muted = true;
      const seeked = new Promise((res) => {
        const to = setTimeout(() => res(false), 9000);
        v.addEventListener('seeked', () => { clearTimeout(to); res(true); }, { once: true });
      });
      v.currentTime = ${t};
      const s = await seeked;
      for (let i = 0; i < 20 && v.readyState < 3; i++) await new Promise(r => setTimeout(r, 500));
      v.play().catch(() => {});
      return { seeked: s, ready: v.readyState, dur: v.duration };
    })()`, true, 30000);
    // a seek can trigger a mid-roll ad AFTER the first clearAd pass:
    // if one is showing now, wait it out and re-seek before capturing
    const adNow = await evaluate(`!!document.querySelector('.ad-showing')`).catch(() => false);
    if (adNow) {
      await clearAd();
      await evaluate(`(async () => {
        const v = document.querySelector('video');
        const seeked = new Promise((res) => {
          const to = setTimeout(() => res(false), 9000);
          v.addEventListener('seeked', () => { clearTimeout(to); res(true); }, { once: true });
        });
        v.currentTime = ${t};
        await seeked;
        v.play().catch(() => {});
        return true;
      })()`, true, 30000).catch(() => {});
    }
    await sleep(2400); // let controls fade
    const rect = await evaluate(`(() => { const r = document.querySelector('video').getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })()`);
    const shot = await send('Page.captureScreenshot', {
      format: 'jpeg', quality: 82,
      clip: { x: rect.x, y: rect.y, width: rect.width, height: rect.height, scale: 1 },
    });
    const buf = Buffer.from(shot.result.data, 'base64');
    writeFileSync(`${outDir}/${t}.jpg`, buf);
    console.log(JSON.stringify({ t, bytes: buf.length, ...got }));
  } catch (e) {
    console.log(JSON.stringify({ t, error: String(e).slice(0, 200) }));
  }
}
await send('Page.close').catch(() => {});
ws.close();
process.exit(0);
