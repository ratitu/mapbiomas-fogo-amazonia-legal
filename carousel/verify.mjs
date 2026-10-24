// Verificação geométrica dos slides — substitui inspeção visual quando o
// modelo não consegue ler imagens.
//
//   node carousel/verify.mjs
//
// Checa: (1) nenhum elemento estoura o frame 1080x1350; (2) nenhum texto cai
// na zona Morta inferior do Instagram; (3) barras do slide 2 são verticais,
// na ordem 2019→2026, com 4 azuis + 4 vermelhos e alturas proporcionais aos
// dados; (4) rótulos de valor existem e ficam dentro do SVG.

import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const W = 1080;
const H = 1350;
const DEAD_ZONE_TOP = H - 250;

const BLUE = "rgb(37, 99, 235)";
const RED = "rgb(220, 38, 38)";

const EXPECTED = [
  { year: 2019, ha: 13403151.45, color: BLUE },
  { year: 2020, ha: 14280715.79, color: BLUE },
  { year: 2021, ha: 9102369.25, color: BLUE },
  { year: 2022, ha: 13388587.40, color: BLUE },
  { year: 2023, ha: 14110379.24, color: RED },
  { year: 2024, ha: 25583085.87, color: RED },
  { year: 2025, ha: 7696586.54, color: RED },
  { year: 2026, ha: 5782625.57, color: RED },
];

const failures = [];
function check(cond, msg) {
  if (!cond) failures.push(msg);
}

function serve() {
  const server = createServer(async (req, res) => {
    const p = new URL(req.url, "http://x").pathname;
    try {
      const body = await readFile(join(HERE, p === "/" ? "/index.html" : p));
      res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      res.end(body);
    } catch {
      res.writeHead(404).end();
    }
  });
  return new Promise((r) => server.listen(0, () => r({ server, port: server.address().port })));
}

const { server, port } = await serve();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.goto(`http://localhost:${port}/index.html`);
await page.evaluate(() => document.fonts.ready);

// ---- (1)+(2) overflow e zona morta, slide a slide
const overflow = await page.evaluate(
  ({ W, H, DEAD_ZONE_TOP }) => {
    const bad = [];
    document.querySelectorAll("section.slide").forEach((slide, i) => {
      const sr = slide.getBoundingClientRect();
      slide.querySelectorAll("*").forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        const top = r.top - sr.top;
        const bottom = r.bottom - sr.top;
        const over = [];
        if (r.left - sr.left < -0.5) over.push("left");
        if (r.right - sr.left > W + 0.5) over.push("right");
        if (top < -0.5) over.push("top");
        if (bottom > H + 0.5) over.push("bottom");
        if (over.length) {
          bad.push(`slide ${i + 1}: <${el.tagName.toLowerCase()}.${el.className}> estoura ${over.join("/")}`);
        }
        const isText = el.children.length === 0 && el.textContent.trim().length > 0;
        if (isText && bottom > DEAD_ZONE_TOP && !el.closest(".tl,.src")) {
          bad.push(`slide ${i + 1}: texto "${el.textContent.trim().slice(0, 28)}…" termina em y=${bottom.toFixed(0)} (zona morta começa em ${DEAD_ZONE_TOP})`);
        }
      });
    });
    return bad;
  },
  { W, H, DEAD_ZONE_TOP },
);
overflow.forEach((m) => failures.push(m));

// ---- (3)+(4) barras do slide 2
const chart = await page.evaluate(() => {
  const svg = document.querySelector("#s2 .chart svg");
  const r = svg.getBoundingClientRect();
  const bars = [...svg.querySelectorAll("rect")].map((el) => {
    const b = el.getBoundingClientRect();
    return {
      w: +b.width.toFixed(1),
      h: +b.height.toFixed(1),
      color: getComputedStyle(el).fill,
      text: el.nextElementSibling?.textContent?.trim() ?? "",
    };
  });
  const cats = [...svg.querySelectorAll("text.cat")].map((t) => t.textContent.trim());
  const vals = [...svg.querySelectorAll("text.val")].map((t) => ({
    text: t.textContent.trim(),
    top: +(t.getBoundingClientRect().top - r.top).toFixed(1),
  }));
  return { bars, cats, vals, svgH: +r.height.toFixed(1) };
});

check(chart.bars.length === 8, `slide 2: esperado 8 barras, achei ${chart.bars.length}`);
chart.bars.forEach((b, i) => {
  const exp = EXPECTED[i];
  if (!exp) return;
  check(b.h > b.w, `slide 2 barra ${i + 1} (${exp.year}): não é vertical (h=${b.h} w=${b.w})`);
  check(b.color === exp.color, `slide 2 barra ${exp.year}: cor ${b.color}, esperado ${exp.color}`);
});
chart.cats.forEach((c, i) => {
  check(c.startsWith(String(EXPECTED[i]?.year)), `slide 2 rótulo ${i + 1}: "${c}" != ano ${EXPECTED[i]?.year}`);
});
// altura proporcional aos dados (tolerância 1%)
const axisMax = Math.max(...EXPECTED.map((e) => e.ha)) * 1.15;
EXPECTED.forEach((e, i) => {
  const want = (e.ha / axisMax) * 540;
  const got = chart.bars[i]?.h ?? 0;
  check(Math.abs(got - want) <= 6, `slide 2 barra ${e.year}: altura ${got}px, esperado ~${want.toFixed(1)}px`);
});
chart.vals.forEach((v, i) => {
  check(v.top >= 0, `slide 2 rótulo "${v.text}": top=${v.top}px, cortado pelo viewBox`);
});

// ---- (5) colisão de texto: nenhum par de <text>/<li>/<div> com caixa se sobrepõe
const collisions = await page.evaluate(() => {
  const bad = [];
  document.querySelectorAll("section.slide").forEach((slide, i) => {
    const boxes = [...slide.querySelectorAll("text, .val, .cat, .axis, .points li, .note, .h2, .kicker, .card, .delta, .cta")]
      .map((el) => ({ el, r: el.getBoundingClientRect() }))
      .filter(({ r }) => r.width > 0 && r.height > 0);
    for (let a = 0; a < boxes.length; a++) {
      for (let b = a + 1; b < boxes.length; b++) {
        const { el: ea, r: ra } = boxes[a];
        const { el: eb, r: rb } = boxes[b];
        if (ea.contains(eb) || eb.contains(ea)) continue;
        const ox = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
        const oy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
        if (ox > 2 && oy > 2) {
          bad.push(
            `slide ${i + 1}: "${ea.textContent.trim().slice(0, 20)}" x "${eb.textContent.trim().slice(0, 20)}" (${ox.toFixed(0)}x${oy.toFixed(0)}px)`,
          );
        }
      }
    }
  });
  return bad;
});
collisions.forEach((m) => failures.push(m));

await browser.close();
server.close();

if (failures.length) {
  console.error(`FALHOU (${failures.length}):`);
  failures.forEach((f) => console.error("  - " + f));
  process.exit(1);
}
console.log("OK — geometria, cores, ordem, alturas proporcionais e zona morta conferem.");
console.log(`   barras: ${chart.bars.map((b) => b.h).join(" / ")} px`);
console.log(`   rótulos: ${chart.vals.map((v) => v.text).join(" · ")}`);
console.log(`   categorias: ${chart.cats.join(" · ")}`);