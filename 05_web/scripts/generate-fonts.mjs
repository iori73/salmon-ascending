// Self-host 源ノ明朝 (Source Han Serif JP, = Noto Serif JP, OFL) + EB Garamond as
// text-subset woff2. Re-run after editing body copy: `npm run fonts`.
//
// Strategy: collect every glyph that appears in app/** and components/** source,
// add a safety base set (all kana, JP punctuation, ASCII), then fetch an exactly-
// subset woff2 per weight from Google Fonts' `text=` endpoint and save it locally.
// No python / harfbuzz needed.

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUT_DIR = path.join(ROOT, "public", "fonts");
const CSS_OUT = path.join(ROOT, "app", "fonts.css");
const UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";

// ── 1. Collect glyphs ────────────────────────────────────────────────
async function walk(dir) {
  const out = [];
  for (const e of await fs.readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...(await walk(p)));
    else if (/\.(tsx|ts|jsx|mdx)$/.test(e.name)) out.push(p);
  }
  return out;
}

function baseSet() {
  const chars = new Set();
  // ASCII printable
  for (let c = 0x20; c <= 0x7e; c++) chars.add(String.fromCodePoint(c));
  // Hiragana + Katakana (full) so future kana edits never tofu
  for (let c = 0x3041; c <= 0x309f; c++) chars.add(String.fromCodePoint(c));
  for (let c = 0x30a0; c <= 0x30ff; c++) chars.add(String.fromCodePoint(c));
  // Common JP punctuation / symbols used editorially
  for (const ch of "、。，．・：；！？「」『』（）〔〕［］｛｝〈〉《》【】—–―…‥〜～→←↑↓▼▲△▽※＊／＝＋－×÷°′″℃％　々〆ヶ") {
    chars.add(ch);
  }
  return chars;
}

async function collectChars() {
  const files = [...(await walk(path.join(ROOT, "app"))), ...(await walk(path.join(ROOT, "components")))];
  const chars = baseSet();
  for (const f of files) {
    const txt = await fs.readFile(f, "utf8");
    for (const ch of txt) {
      const cp = ch.codePointAt(0);
      // keep CJK ideographs, kana, fullwidth, and CJK symbols/punct
      if (
        (cp >= 0x3000 && cp <= 0x30ff) || // CJK punct + kana
        (cp >= 0x3400 && cp <= 0x9fff) || // CJK ideographs (ext A + main)
        (cp >= 0xf900 && cp <= 0xfaff) || // compat ideographs
        (cp >= 0xff00 && cp <= 0xffef) || // fullwidth forms
        (cp >= 0x2000 && cp <= 0x206f) // general punctuation (— … etc.)
      ) {
        chars.add(ch);
      }
    }
  }
  return [...chars].sort();
}

// ── 2. Fetch + save subset woff2 ─────────────────────────────────────
async function fetchCss(family, axis, text) {
  const url = `https://fonts.googleapis.com/css2?family=${family}:${axis}&text=${encodeURIComponent(
    text
  )}&display=swap`;
  const res = await fetch(url, { headers: { "User-Agent": UA } });
  if (!res.ok) throw new Error(`CSS fetch failed ${res.status} for ${family} ${axis}`);
  return res.text();
}

function woff2UrlsFromCss(css) {
  // returns [{style, weight, url}]
  const faces = [];
  const blocks = css.split("@font-face").slice(1);
  for (const b of blocks) {
    const style = /font-style:\s*(\w+)/.exec(b)?.[1] ?? "normal";
    const weight = /font-weight:\s*(\d+)/.exec(b)?.[1] ?? "400";
    const url = /url\(([^)]+)\)\s*format\('woff2'\)/.exec(b)?.[1];
    if (url) faces.push({ style, weight, url });
  }
  return faces;
}

async function download(url, dest) {
  const res = await fetch(url, { headers: { "User-Agent": UA } });
  if (!res.ok) throw new Error(`download failed ${res.status} ${url}`);
  const buf = Buffer.from(await res.arrayBuffer());
  await fs.writeFile(dest, buf);
  return buf.length;
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const cjkChars = (await collectChars()).join("");
  console.log(`collected ${cjkChars.length} unique characters`);

  const latin =
    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~—–…‘’“”ÀÉàéèêïôûœ&";

  const cssFaces = [];

  // Noto Serif JP (= 源ノ明朝): Light / Regular / SemiBold
  for (const w of [300, 400, 600]) {
    const css = await fetchCss("Noto+Serif+JP", `wght@${w}`, cjkChars);
    const [face] = woff2UrlsFromCss(css);
    if (!face) throw new Error(`no woff2 for Noto Serif JP ${w}`);
    const file = `noto-serif-jp-${w}.woff2`;
    const size = await download(face.url, path.join(OUT_DIR, file));
    console.log(`  ${file}  ${(size / 1024).toFixed(1)} KB`);
    cssFaces.push(
      `@font-face{font-family:'Noto Serif JP';font-style:normal;font-weight:${w};font-display:swap;src:url('/fonts/${file}') format('woff2');}`
    );
  }

  // EB Garamond: Regular / Medium / Italic
  const ebCss = await fetchCss("EB+Garamond", "ital,wght@0,400;0,500;1,400", latin);
  for (const face of woff2UrlsFromCss(ebCss)) {
    const tag = `${face.style === "italic" ? "italic" : "n"}${face.weight}`;
    const file = `eb-garamond-${tag}.woff2`;
    const size = await download(face.url, path.join(OUT_DIR, file));
    console.log(`  ${file}  ${(size / 1024).toFixed(1)} KB`);
    cssFaces.push(
      `@font-face{font-family:'EB Garamond';font-style:${face.style};font-weight:${face.weight};font-display:swap;src:url('/fonts/${file}') format('woff2');}`
    );
  }

  const header =
    "/* AUTO-GENERATED by scripts/generate-fonts.mjs — do not edit by hand. */\n/* Run `npm run fonts` to regenerate after editing body copy. */\n";
  await fs.writeFile(CSS_OUT, header + cssFaces.join("\n") + "\n");
  console.log(`wrote ${CSS_OUT}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
