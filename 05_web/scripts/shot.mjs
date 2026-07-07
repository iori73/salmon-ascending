// Full-page screenshot via Chrome DevTools Protocol (no deps; Node 25 global WebSocket/fetch).
// Usage: node scripts/shot.mjs <url> <outPath> [widthPx]
import { spawn } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [, , url, out, widthArg] = process.argv;
const width = Number(widthArg || 1280);
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9300 + Math.floor((Date.now() % 600));

const profile = mkdtempSync(join(tmpdir(), "cdp-shot-"));
const chrome = spawn(CHROME, [
  "--headless=new",
  "--disable-gpu",
  "--hide-scrollbars",
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`,
  `--window-size=${width},1000`,
  "about:blank",
]);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 50; i++) {
    try {
      const targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
      const page = targets.find((t) => t.type === "page");
      if (page?.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(100);
  }
  throw new Error("chrome devtools endpoint not ready");
}

function cdp(ws) {
  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) {
      pending.get(msg.id)(msg);
      pending.delete(msg.id);
    }
  });
  return (method, params = {}) =>
    new Promise((resolve) => {
      const myId = ++id;
      pending.set(myId, (m) => resolve(m.result));
      ws.send(JSON.stringify({ id: myId, method, params }));
    });
}

const wsUrl = await getWsUrl();
const ws = new WebSocket(wsUrl);
await new Promise((r) => (ws.onopen = r));
const send = cdp(ws);

await send("Page.enable");
// Fixed viewport so vh-based sections (min-h-screen) keep their real height.
await send("Emulation.setDeviceMetricsOverride", {
  width,
  height: 900,
  deviceScaleFactor: 2,
  mobile: false,
});
if (process.env.PRINT) await send("Emulation.setEmulatedMedia", { media: "print" });
await send("Page.navigate", { url });
await sleep(1800); // fonts + layout settle
const { cssContentSize } = await send("Page.getLayoutMetrics");
const fullH = Math.ceil(cssContentSize.height);
const { data } = await send("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: { x: 0, y: 0, width, height: fullH, scale: 1 },
});
writeFileSync(out, Buffer.from(data, "base64"));
console.log(`wrote ${out}  (${width}×${fullH})`);
ws.close();
chrome.kill();
process.exit(0);
