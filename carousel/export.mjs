// Exporta os 6 slides do carrossel para PNG 1080x1350 (feed Instagram).
//
//   node carousel/export.mjs
//
// Serve o index.html via HTTP local (nunca file:// — gotcha do projeto) e
// captura cada <section class="slide"> com Playwright/Chromium.

import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(HERE, "out");
const PORT = 0; // 0 = o kernel escolhe uma porta livre
const W = 1080;
const H = 1350;
const SLIDES = 6;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
};

function serve() {
  const server = createServer(async (req, res) => {
    const url = new URL(req.url, "http://localhost");
    const rel = url.pathname === "/" ? "/index.html" : url.pathname;
    const file = join(HERE, rel);
    if (!file.startsWith(HERE)) {
      res.writeHead(403).end("forbidden");
      return;
    }
    try {
      const body = await readFile(file);
      const ext = file.slice(file.lastIndexOf("."));
      res.writeHead(200, { "content-type": MIME[ext] ?? "application/octet-stream" });
      res.end(body);
    } catch {
      res.writeHead(404).end("not found");
    }
  });
  return new Promise((resolve) =>
    server.listen(PORT, () => resolve({ server, port: server.address().port })),
  );
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  const { server, port } = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
  });

  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });

  await page.goto(`http://localhost:${port}/index.html`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);

  const slides = page.locator("section.slide");
  const found = await slides.count();
  if (found !== SLIDES) {
    throw new Error(`esperava ${SLIDES} slides, encontrei ${found}`);
  }

  for (let i = 0; i < SLIDES; i++) {
    const n = String(i + 1).padStart(2, "0");
    const target = join(OUT_DIR, `slide-${n}.png`);
    await slides.nth(i).screenshot({ path: target });
    console.log(`ok  out/slide-${n}.png  (${W}x${H})`);
  }

  if (errors.length) {
    console.error("\nerros de console:");
    for (const e of errors) console.error("  " + e);
    throw new Error(`${errors.length} erro(s) de console`);
  }

  await browser.close();
  server.close();
  console.log(`\n${SLIDES} PNGs gerados em ${OUT_DIR}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});