#!/usr/bin/env python3
"""Gera carousel/index.html — carrossel Instagram 6 slides (1080x1350) sobre área
queimada na Amazônia Legal (MapBiomas Fogo).

Todos os números são gravados como floats crus e formatados em pt-BR na
geração — nenhuma string formatada é hardcoded no HTML.

Uso:  python3 carousel/build.py
Saída: carousel/index.html (estático, SVG inline, sem CDN)
"""

from pathlib import Path
from typing import List, Sequence, Tuple

OUT = Path(__file__).with_name("index.html")

W, H = 1080, 1350
PAD = 60

BG = "#0d1117"
PANEL = "#161b22"
LINE = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#2563eb"
RED = "#dc2626"
BLUE_SOFT = "#1e40af"
RED_SOFT = "#991b1b"

FONT = "'Inter','Manrope','DejaVu Sans',Arial,sans-serif"

YEARS_2019_2022 = "BOLSONARO"
YEARS_2023_2026 = "PT"

# ---------------------------------------------------------------- dados brutos
# Fonte: fetch_burned_area_legal_amazon.py + burned_area_legal_amazon.md
# (MapBiomas Fogo — /api/statistics/area/legalAmazon/1/legalAmazon)
YEARS: List[Tuple[int, float, str]] = [
    (2019, 13403151.45, YEARS_2019_2022),
    (2020, 14280715.79, YEARS_2019_2022),
    (2021, 9102369.25, YEARS_2019_2022),
    (2022, 13388587.40, YEARS_2019_2022),
    (2023, 14110379.24, YEARS_2023_2026),
    (2024, 25583085.87, YEARS_2023_2026),
    (2025, 7696586.54, YEARS_2023_2026),
    (2026, 5782625.57, YEARS_2023_2026),
]
PARTIAL_YEAR = 2026  # Jan–Out (a API retorna null para out/2026)

TOTAL_BLUE = 50174823.89
TOTAL_RED = 53172677.22

# Top 6 meses — /api/statistics/area/legalAmazon/1/legalAmazon?monthStart=m&monthEnd=m
MONTH_NAMES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
TOP_MONTHS: List[Tuple[int, int, float]] = [
    (2024, 9, 8989008.68),
    (2020, 9, 5382428.34),
    (2022, 9, 4761175.25),
    (2024, 10, 4490096.25),
    (2019, 9, 4211313.20),
    (2024, 8, 4094085.53),
]

# Top 6 estados no período PT — /api/statistics/area/state/{code}/state
STATE_NAMES = {
    "PA": "Pará", "MT": "Mato Grosso", "TO": "Tocantins",
    "MA": "Maranhão", "RR": "Roraima", "AM": "Amazonas",
    "RO": "Rondônia", "AP": "Amapá", "AC": "Acre",
}
TOP_STATES: List[Tuple[str, float]] = [
    ("PA", 13102126.85),
    ("MT", 12472799.97),
    ("TO", 7500663.70),
    ("MA", 6359448.07),
    ("RR", 5626073.96),
    ("AM", 4287204.95),
]
STATES_SUM = 53979818.15  # soma dos 9 estados da Amazônia Legal

SOURCE = "Fonte: MapBiomas Fogo — Amazônia Legal (type=legalAmazon, code=1)"


# --------------------------------------------------------------- formatação
def br(n: float, dec: int = 2) -> str:
    """Número no formato brasileiro: 1.234.567,89"""
    s = f"{n:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def mi(n: float, dec: int = 1) -> str:
    """Milhões de hectares no formato brasileiro: 13,4"""
    return f"{n / 1e6:.{dec}f}".replace(".", ",")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------- componentes
def timeline() -> str:
    seg_w, gap = 86, 8
    usable = W - 2 * PAD
    x0 = PAD
    cells = []
    for i, (year, _ha, group) in enumerate(YEARS):
        x = x0 + i * (seg_w + gap)
        fill = BLUE if group == YEARS_2019_2022 else RED
        cells.append(
            f'<rect x="{x}" y="0" width="{seg_w}" height="10" rx="5" fill="{fill}" '
            f'opacity="{1 if year >= 2023 else 0.55}"/>'
            f'<text x="{x + seg_w / 2:.1f}" y="30" class="tl-y">{year}</text>'
        )
    caption_x = x0 + 8 * (seg_w + gap) + 10
    return (
        f'<div class="tl"><svg width="{W}" height="38" viewBox="0 0 {W} 38">'
        + "".join(cells)
        + f'<text x="{caption_x}" y="30" class="tl-n">2019–2026</text>'
        "</svg></div>"
    )


def footer() -> str:
    return f'<div class="src">{esc(SOURCE)}</div>'

def vbars(rows: Sequence[Tuple[str, float, str]], plot_h: int,
          value_fmt) -> str:
    """Barras verticais em SVG. rows = (rótulo, valor, cor).

    Retorna o conteúdo de um <svg> com viewBox de `svg_w` x `svg_h`.
    Gutter à esquerda reserva espaço para os rótulos do eixo Y; `top` reserva
    espaço para o rótulo de valor da barra mais alta.
    """
    n = len(rows)
    maxv = max(r[1] for r in rows)
    # teto do eixo = 15% acima do máximo, para o rótulo da barra mais alta
    # caber acima da barra sem ser cortado pelo viewBox do SVG
    axis_max = maxv * 1.15
    step = axis_max / 4
    gutter, top = 76, 44
    svg_w = W - 2 * PAD
    svg_h = top + plot_h + 52
    plot_w = svg_w - gutter
    base = top + plot_h

    out = []
    for i in range(5):
        v = step * i
        gy = base - (v / axis_max) * plot_h
        if i > 0:
            out.append(
                f'<line x1="{gutter}" y1="{gy:.1f}" x2="{svg_w}" y2="{gy:.1f}" '
                f'stroke="{LINE}" stroke-width="1" opacity="0.5"/>'
            )
        out.append(
            f'<text x="0" y="{gy + 7:.1f}" class="axis">{mi(v)}</text>'
        )

    slot = plot_w / n
    bw = slot * 0.58
    for i, (label, val, color) in enumerate(rows):
        bh = max(2.0, (val / axis_max) * plot_h)
        x = gutter + i * slot + (slot - bw) / 2
        y = base - bh
        cx = gutter + i * slot + slot / 2
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'rx="6" fill="{color}"/>'
        )
        out.append(
            f'<text x="{cx:.1f}" y="{y - 16:.1f}" class="val" text-anchor="middle">'
            f"{esc(value_fmt(val))}</text>"
        )
        out.append(
            f'<text x="{cx:.1f}" y="{base + 42}" class="cat" '
            f'text-anchor="middle">{esc(label)}</text>'
        )

    return (
        f'<svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">'
        + "".join(out)
        + "</svg>"
    )


def legend(items: Sequence[Tuple[str, str]]) -> str:
    cells = []
    x = 0
    for label, color in items:
        cells.append(
            f'<rect x="{x}" y="-15" width="22" height="22" rx="5" fill="{color}"/>'
            f'<text x="{x + 34}" y="2" class="lg">{esc(label)}</text>'
        )
        x += 200
    return f'<svg width="{W - 2 * PAD}" height="30" viewBox="0 0 {W - 2 * PAD} 30">' + "".join(cells) + "</svg>"


# ------------------------------------------------------------------ slides
def slide_cover() -> str:
    return f"""
<section class="slide" id="s1">
  <div class="pad cover">
    <div class="kicker">Amazônia Legal</div>
    <h1 class="title">Serie historica<br>de queimadas<br>na Amazônia Legal</h1>
    <p class="sub">Área queimada por ano, em milhões de hectares — comparando os
    últimos 8 anos da Amazônia Legal.</p>
    <div class="hero">
      <div class="hero-n">{mi(TOTAL_RED + TOTAL_BLUE, 0)} mi</div>
      <div class="hero-l">hectares queimados no total</div>
    </div>
    <div class="note">2026 é parcial — dados de janeiro a outubro.</div>
  </div>
  {timeline()}
</section>"""


def slide_bars() -> str:
    rows = [
        (str(y) + ("*" if y == PARTIAL_YEAR else ""), ha,
         BLUE if g == YEARS_2019_2022 else RED)
        for y, ha, g in YEARS
    ]
    plot_h = 540
    return f"""
<section class="slide" id="s2">
  <div class="pad">
    <div class="kicker">01 · Ano a ano</div>
    <h2 class="h2">Área queimada por ano</h2>
    <div class="legend">{legend([(YEARS_2019_2022, BLUE), (YEARS_2023_2026, RED)])}</div>
    <div class="chart">{vbars(rows, plot_h, lambda v: mi(v) + " mi")}</div>
    <div class="note">Milhões de hectares no eixo Y. <strong>* 2026:</strong> janeiro a
    outubro (a API é granular por mês). Pico do período: <strong>2024</strong>,
    com {mi(25583085.87)} mi ha.</div>
  </div>
  {timeline()}
</section>"""


def slide_totals() -> str:
    delta = (TOTAL_RED - TOTAL_BLUE) / TOTAL_BLUE * 100
    delta_txt = f"+{delta:.1f}".replace(".", ",")
    return f"""
<section class="slide" id="s3">
  <div class="pad">
    <div class="kicker">02 · Totais</div>
    <h2 class="h2">Somando os 4 anos de cada governo</h2>
    <div class="cards">
      <div class="card card--blue">
        <div class="card-tag">{esc(YEARS_2019_2022)} · 2019–2022</div>
        <div class="card-n">{mi(TOTAL_BLUE)}</div>
        <div class="card-u">milhões de hectares</div>
        <div class="card-ha">{br(TOTAL_BLUE)} ha</div>
      </div>
      <div class="card card--red">
        <div class="card-tag">{esc(YEARS_2023_2026)} · 2023–2026</div>
        <div class="card-n">{mi(TOTAL_RED)}</div>
        <div class="card-u">milhões de hectares</div>
        <div class="card-ha">{br(TOTAL_RED)} ha</div>
      </div>
    </div>
    <div class="delta">
      <span class="delta-n">{delta_txt}</span>
      <span class="delta-l">de área queimada no governo {esc(YEARS_2023_2026)}<br>
      em relação a {esc(YEARS_2019_2022)}</span>
    </div>
    <div class="note">Atenção: 2026 está incompleto (jan–out). Mesmo assim, o total
    do governo {esc(YEARS_2023_2026)} já supera o do governo anterior.</div>
  </div>
  {timeline()}
</section>"""


def slide_months() -> str:
    rows = []
    for y, m, ha in TOP_MONTHS:
        color = BLUE if y <= 2022 else RED
        rows.append((f"{MONTH_NAMES[m - 1][:3]}/{y}", ha, color))
    plot_h = 500
    return f"""
<section class="slide" id="s4">
  <div class="pad">
    <div class="kicker">03 · Picos mensais</div>
    <h2 class="h2">Quando mais queimou</h2>
    <div class="legend">{legend([(YEARS_2019_2022, BLUE), (YEARS_2023_2026, RED)])}</div>
    <div class="chart">{vbars(rows, plot_h, lambda v: mi(v) + " mi")}</div>
    <div class="note"><strong>Todos os 6 picos caem entre agosto e outubro</strong> —
    o maior foi {esc(MONTH_NAMES[TOP_MONTHS[0][1] - 1])}/{TOP_MONTHS[0][0]},
    com {br(TOP_MONTHS[0][2])} ha.</div>
  </div>
  {timeline()}
  {footer()}
</section>"""


def slide_states() -> str:
    rows = []
    for uf, ha in TOP_STATES:
        rows.append((STATE_NAMES[uf][:7], ha, RED))
    plot_h = 480
    return f"""
<section class="slide" id="s5">
  <div class="pad">
    <div class="kicker">04 · Onde queimou</div>
    <h2 class="h2">Estados mais atingidos · 2023–2026</h2>
    <div class="chart">{vbars(rows, plot_h, lambda v: mi(v) + " mi")}</div>
  {timeline()}
  {footer()}
</section>"""


def slide_end() -> str:
    delta = (TOTAL_RED - TOTAL_BLUE) / TOTAL_BLUE * 100
    delta_txt = f"+{delta:.1f}".replace(".", ",")
    pa_mt = mi(13102126.85 + 12472799.97)
    return f"""
<section class="slide" id="s6">
  <div class="pad">
    <div class="kicker">05 · Resumo</div>
    <h2 class="h2">O que os números mostram</h2>
    <ol class="points">
      <li><strong>{mi(TOTAL_RED)} mi ha</strong> queimados em 2023–2026 —
      {delta_txt}% sobre os {mi(TOTAL_BLUE)} mi ha de 2019–2022.</li>
      <li><strong>2024</strong> foi o pior ano isolado: {mi(25583085.87)} mi ha,
      quase o dobro de qualquer outro ano.</li>
      <li>O fogo é <strong>concentrado no fim doano seco</strong>:
      6 dos 6 maiores meses ocorrem entre agosto e outubro.</li>
      <li><strong>Pará e Mato Grosso</strong> concentram a queima —
      {mi(13102126.85 + 12472799.97)} mi ha combinados no período.</li>
    </ol>
    <div class="cta">
      <div class="cta-l">Dados obtidos pela API do MapBiomas Fogo</div>
      <div class="cta-s">https://plataforma.monitorfogo.mapbiomas.org/api/docs/</div>
    </div>
    <div class="note">Dados: MapBiomas Fogo. 2026 parcial (jan–out). Áreas em hectares.</div>
  </div>
  {timeline()}
</section>"""


# ------------------------------------------------------------------- CSS/HTML
CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000;font-family:{FONT};-webkit-font-smoothing:antialiased}}
.slide{{position:relative;width:{W}px;height:{H}px;overflow:hidden;
  background:radial-gradient(1200px 700px at 20% -10%,#16202e 0%,{BG} 62%);
  color:{TEXT};display:flex;flex-direction:column}}
.pad{{padding:{PAD}px {PAD}px 300px;flex:1;display:flex;flex-direction:column}}
.cover{{justify-content:center;padding-bottom:320px}}
.kicker{{font-size:26px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;
  color:{RED};margin-bottom:22px}}
#s1 .kicker{{color:{MUTED}}}
.title{{font-size:96px;line-height:1.02;font-weight:800;letter-spacing:-.03em}}
.sub{{font-size:31px;line-height:1.45;color:{MUTED};margin-top:34px;max-width:840px}}
.h2{{font-size:56px;line-height:1.1;font-weight:800;letter-spacing:-.02em;margin-bottom:8px}}
.chips{{display:flex;gap:16px;margin-top:44px;flex-wrap:wrap}}
.chip{{font-size:26px;font-weight:700;padding:12px 24px;border-radius:999px}}
.chip--blue{{background:rgba(37,99,235,.18);color:#93b4fb;border:2px solid {BLUE}}}
.chip--red{{background:rgba(220,38,38,.18);color:#fca5a5;border:2px solid {RED}}}
.hero{{margin-top:60px;padding:38px 40px;background:{PANEL};
  border:2px solid {LINE};border-radius:26px;align-self:flex-start}}
.hero-n{{font-size:118px;font-weight:800;line-height:.95;letter-spacing:-.04em}}
.hero-l{{font-size:28px;color:{MUTED};margin-top:14px}}
.legend{{margin:26px 0 6px}}
.chart{{margin-top:6px}}
text{{fill:{TEXT};font-family:{FONT}}}
.axis{{font-size:20px;fill:{MUTED}}}
.val{{font-size:26px;font-weight:800}}
.cat{{font-size:28px;font-weight:700;fill:{TEXT}}}
.lg{{font-size:28px;font-weight:700}}
.note{{margin-top:auto;padding-top:26px;font-size:23px;line-height:1.5;color:{MUTED}}}
.note strong{{color:{TEXT}}}
.cards{{display:flex;gap:24px;margin-top:44px}}
.card{{flex:1;padding:38px 32px;border-radius:24px;background:{PANEL};
  border:2px solid {LINE}}}
.card--blue{{border-color:{BLUE};background:linear-gradient(180deg,rgba(37,99,235,.16),{PANEL} 62%)}}
.card--red{{border-color:{RED};background:linear-gradient(180deg,rgba(220,38,38,.16),{PANEL} 62%)}}
.card-tag{{font-size:24px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:{MUTED}}}
.card-n{{font-size:104px;font-weight:800;line-height:1;letter-spacing:-.04em;margin-top:22px}}
.card-u{{font-size:26px;color:{MUTED};margin-top:10px}}
.card-ha{{font-size:21px;color:{MUTED};margin-top:16px;font-variant-numeric:tabular-nums}}
.delta{{margin-top:34px;padding:30px 36px;border-radius:22px;background:{PANEL};
  border-left:8px solid {RED};display:flex;align-items:center;gap:30px}}
.delta-n{{font-size:82px;font-weight:800;color:{RED};line-height:1;letter-spacing:-.03em}}
.delta-l{{font-size:27px;line-height:1.4;color:{MUTED}}}
.points{{margin-top:38px;list-style:none;counter-reset:p}}
.points li{{counter-increment:p;font-size:29px;line-height:1.45;color:{MUTED};
  padding:26px 0 26px 74px;border-bottom:1px solid {LINE};position:relative}}
.points li::before{{content:counter(p);position:absolute;left:0;top:24px;
  font-size:30px;font-weight:800;color:{RED}}}
.points strong{{color:{TEXT}}}
.cta{{margin-top:36px;padding:32px 36px;border-radius:22px;
  background:linear-gradient(120deg,rgba(37,99,235,.2),rgba(220,38,38,.2));
  border:2px solid {LINE}}}
.cta-l{{font-size:36px;font-weight:800}}
.cta-s{{font-size:27px;color:{MUTED};margin-top:10px}}
.tl{{position:absolute;left:0;right:0;bottom:250px}}
.tl text{{fill:{MUTED}}}
.tl-y{{font-size:20px;font-weight:700}}
.tl-n{{font-size:20px;fill:{MUTED}}}
.src{{font-size:19px;color:#6e7681;margin-top:16px}}
"""


def build() -> str:
    slides = "".join([
        slide_cover(), slide_bars(), slide_totals(),
        slide_months(), slide_states(), slide_end(),
    ])
    return (
        "<!doctype html>\n"
        '<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        f'<title>Área queimada na Amazônia Legal — {esc(YEARS_2019_2022)} vs {esc(YEARS_2023_2026)}</title>\n'
        f"<style>{CSS}</style>\n</head>\n<body>\n{slides}\n</body>\n</html>\n"
    )


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"OK -> {OUT}  ({len(OUT.read_text(encoding='utf-8'))} bytes)")
    print(f"BOLSONARO: {br(TOTAL_BLUE)} ha | PT: {br(TOTAL_RED)} ha")
