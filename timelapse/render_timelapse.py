#!/usr/bin/env python3
"""Timelapse 1080x1920 dos focos de calor na Amazonia Legal (1 frame = 1 semana).

Fontes (as mesmas camadas abertas na sessao do QGIS):
  - bdqueimadas_2026-05-01_2026-10-27.geojson   (pontos, DataHora + FRP)
  - limites_amazonia_legal.geojson              (contorno)
  - Esri World Imagery (tiles XYZ)              (mapa base)

Saida: timelapse/frames/frame_XXX.png  ->  ffmpeg -framerate 1
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(__file__).resolve().parent
CACHE = WORK / "cache"
FRAMES = WORK / "frames"

sys.path.insert(0, str(ROOT))
from design import deckmap as DM  # noqa: E402  (sistema de design)


W, H = 1080, 1920           # definidos de novo em main() conforme --size
ORIENT = "portrait"         # "portrait" (1080x1920) | "landscape" (1920x1080)
SUP = 2                     # supersampling interno para linhas/pontos suaves
ZOOM = 8                    # nivel dos tiles do mapa base
SPLIT = 640                 # landscape: largura do painel de texto
SCREEN_CX, SCREEN_CY = W / 2, H / 2   # centro da Amazonia na tela
TILE_URL = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
R = 6378137.0

# ---------------------------------------------------------------- mercator
def merc_x(lon):
    return np.radians(np.asarray(lon, dtype=float)) * R


def merc_y(lat):
    lat = np.clip(np.asarray(lat, dtype=float), -85.0, 85.0)
    return np.log(np.tan(np.pi / 4.0 + np.radians(lat) / 2.0)) * R

def carrega_focos(path: Path):
    feats = json.load(open(path))["features"]
    lon, lat, frp, when = [], [], [], []
    for f in feats:
        p = f["properties"]
        lon.append(p["Longitude"])
        lat.append(p["Latitude"])
        frp.append(float(p["FRP"] or 0.0))
        when.append(dt.datetime.strptime(p["DataHora"], "%Y/%m/%d %H:%M:%S"))
    return (np.asarray(lon), np.asarray(lat),
            np.asarray(frp), np.asarray(when, dtype="datetime64[s]"))


def carrega_limite(path: Path):
    gj = json.load(open(path))
    rings = []
    for feat in gj["features"]:
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            rings.append(np.asarray(poly[0], dtype=float))
    return rings


# ---------------------------------------------------------------- basemap
def _tile_xy(lon, lat, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def _get_tile(z, x, y):
    dst = CACHE / "tiles" / str(z) / str(x) / f"{y}.jpg"
    if dst.exists() and dst.stat().st_size > 0:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        try:
            r = requests.get(TILE_URL.format(z=z, x=x, y=y), timeout=30,
                             headers={"User-Agent": "fogo-timelapse/1.0"})
            if r.status_code == 200 and r.content:
                dst.write_bytes(r.content)
                return dst
        except Exception:
            pass
    raise RuntimeError(f"tile {z}/{x}/{y} falhou")


def monta_basemap(ext, out_path: Path):
    """ext = (xmin, ymin, xmax, ymax) em metros mercator."""
    xmin, ymin, xmax, ymax = ext
    tx0, ty0 = _tile_xy(math.degrees(xmin / R), math.degrees(2 * math.atan(math.exp(ymax / R)) - math.pi / 2), ZOOM)
    tx1, ty1 = _tile_xy(math.degrees(xmax / R), math.degrees(2 * math.atan(math.exp(ymin / R)) - math.pi / 2), ZOOM)
    x0, x1 = int(math.floor(tx0)) - 1, int(math.floor(tx1)) + 1
    y0, y1 = int(math.floor(ty0)) - 1, int(math.floor(ty1)) + 1
    cols, rows = x1 - x0 + 1, y1 - y0 + 1
    print(f"  tiles z{ZOOM}: {cols}x{rows} = {cols * rows}")

    jobs = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
    with ThreadPoolExecutor(max_workers=16) as ex:
        list(ex.map(lambda p: _get_tile(ZOOM, *p), jobs))

    mosaic = Image.new("RGB", (cols * 256, rows * 256))
    for x, y in jobs:
        mosaic.paste(Image.open(CACHE / "tiles" / str(ZOOM) / str(x) / f"{y}.jpg").convert("RGB"),
                     ((x - x0) * 256, (y - y0) * 256))

    # recorte exato da janela
    world_px = 256 * 2 ** ZOOM
    ppm = world_px / (2 * math.pi * R)       # pixels por metro
    left = (xmin + math.pi * R) * ppm - x0 * 256
    top = (math.pi * R - ymax) * ppm - y0 * 256
    right = (xmax + math.pi * R) * ppm - x0 * 256
    bottom = (math.pi * R - ymin) * ppm - y0 * 256
    crop = mosaic.crop((round(left), round(top), round(right), round(bottom)))
    crop = crop.resize((W * SUP, H * SUP), Image.LANCZOS)

    # tratamento do satelite = design (dessatura, escurece, vinheta no assunto)
    img = DM.trata_satelite(crop, W, H, SCREEN_CX, SCREEN_CY, SUP)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"  basemap {img.size} -> {out_path}")
    return img


# ---------------------------------------------------------------- desenho
def px(lon, lat, ext, s, sup=1):
    xmin, ymin, xmax, ymax = ext
    X = (merc_x(lon) - xmin) * s * sup
    Y = (ymax - merc_y(lat)) * s * sup
    return X, Y


# texto do produto (o design e a geometria ficam em design/deckmap.py)
NOTA = {
    "portrait": "focos\ndetectados\nna semana",
    "landscape": "focos detectados\nna semana",
}
FONTES = {
    "portrait": ("FOCOS: INPE BDQUEIMADAS · LIMITE: MAPBIOMAS/IBGE · BASE: ESRI WORLD IMAGERY",),
    "landscape": ("FOCOS: INPE BDQUEIMADAS · LIMITE: MAPBIOMAS/IBGE",
                  "BASE: ESRI WORLD IMAGERY · 1 FRAME = 1 SEMANA"),
}


def spec_do_frame(ini, fim, n, semanas, idx, acumulado) -> DM.Spec:
    """Traduz o dado deste produto para o conteudo que o design espera."""
    return DM.Spec(
        eyebrow="FOCOS DE INCÊNDIO · AMAZÔNIA LEGAL",
        data=DM.rotulo_semana(ini, fim),
        valor=DM.milhar(n),
        valor_nota=NOTA[ORIENT],
        serie_titulo="FOCOS POR SEMANA · MAI → OUT",
        serie=[(m, v) for m, _, v in semanas],
        idx=idx,
        acumulado=DM.milhar(acumulado),
        escala_titulo="ESCALA DE INTENSIDADE (FRP)",
        escala=[("< 50 MW", DM.ramp(0.35)), ("50–300", DM.ramp(0.78)),
                ("> 300", DM.ramp(1.0))],
        fontes=FONTES[ORIENT],
    )


def render_frame(dest: Path, base: Image.Image, rings, ext, s,
                 lon, lat, frp, semanas, idx, acumulado):
    ini, fim, n = semanas[idx]

    # camadas de mapa: contorno + pontos (estilo em deckmap)
    aneis = [np.column_stack(px(ring[:, 0], ring[:, 1], ext, s, SUP)) for ring in rings]
    img = DM.camada_limite(base.convert("RGB").copy(), aneis, W)
    t = np.clip(np.log1p(frp) / math.log1p(400.0), 0, 1)
    img = DM.camada_pontos(img, *px(lon, lat, ext, s, SUP), t, SUP)

    # chrome + marca d'agua
    img = img.resize((W, H), Image.LANCZOS).convert("RGBA")
    img = DM.compor(img, spec_do_frame(ini, fim, n, semanas, idx, acumulado), ORIENT)
    img = DM.marca_dagua(img)

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dest, quality=95)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", choices=["portrait", "landscape"], default="portrait",
                    help="portrait = 1080x1920 · landscape = 1920x1080")
    ap.add_argument("--only", type=int, default=None, help="renderiza apenas uma semana (debug)")
    ap.add_argument("--rebase", action="store_true", help="refaz o mapa base")
    args = ap.parse_args()

    global W, H, ORIENT, SCREEN_CX, SCREEN_CY, FRAMES
    ORIENT = args.size
    if ORIENT == "landscape":
        W, H = 1920, 1080
        FRAMES = WORK / "frames_1920x1080"
        SCREEN_CX = SPLIT + (W - SPLIT) / 2       # mapa centralizado no painel direito
        SCREEN_CY = H / 2
    else:
        W, H = 1080, 1920
        FRAMES = WORK / "frames"
        SCREEN_CX, SCREEN_CY = W / 2, H / 2

    print("carregando dados...")
    lon, lat, frp, when = carrega_focos(ROOT / "bdqueimadas_2026-05-01_2026-10-27.geojson")
    rings = carrega_limite(ROOT / "limites_amazonia_legal.geojson")
    print(f"  {len(lon):,} focos · {len(rings)} anel(is) de limite")

    bx0 = min(r[:, 0].min() for r in rings); bx1 = max(r[:, 0].max() for r in rings)
    by0 = min(r[:, 1].min() for r in rings); by1 = max(r[:, 1].max() for r in rings)
    ax0, ax1 = float(merc_x(bx0)), float(merc_x(bx1))
    ay0, ay1 = float(merc_y(by0)), float(merc_y(by1))
    cx, cy = (ax0 + ax1) / 2, (ay0 + ay1) / 2
    if ORIENT == "landscape":
        s = 900.0 / (ay1 - ay0)                   # 90 px de margem em cima/embaixo
    else:
        s = (W * 0.926) / (ax1 - ax0)             # 37 px de margem de cada lado
    ext = (cx - SCREEN_CX / s, cy - (H - SCREEN_CY) / s,
           cx + (W - SCREEN_CX) / s, cy + SCREEN_CY / s)
    aw, ah = (ax1 - ax0) * s, (ay1 - ay0) * s
    print(f"  amazonia: {aw:.0f} x {ah:.0f} px "
          f"(x {int(SCREEN_CX - aw / 2)}–{int(SCREEN_CX + aw / 2)}, "
          f"y {int(SCREEN_CY - ah / 2)}–{int(SCREEN_CY + ah / 2)})")

    base_path = CACHE / f"basemap_{W}x{H}_z{ZOOM}.png"
    if args.rebase or not base_path.exists():
        print("montando mapa base...")
        base = monta_basemap(ext, base_path)
    else:
        base = Image.open(base_path)
        print(f"  basemap em cache {base.size}")

    # semanas completas (segunda a domingo)
    dias = when.astype("datetime64[D]").astype("O")
    segundas = sorted({(d - dt.timedelta(days=d.weekday())) for d in dias})
    semanas = []
    for m in segundas:
        f = m + dt.timedelta(days=6)
        if m < dt.date(2026, 5, 4) or f > dt.date(2026, 10, 25):
            continue
        mask = (when >= np.datetime64(m)) & (when < np.datetime64(f + dt.timedelta(days=1)))
        semanas.append((m, f, int(mask.sum()), mask))
    print(f"  {len(semanas)} semanas: {semanas[0][0]} .. {semanas[-1][1]}")

    alvo = range(len(semanas)) if args.only is None else [args.only]
    acum = 0
    for i, (ini, fim, n, mask) in enumerate(semanas):
        if i in alvo:
            dest = FRAMES / f"frame_{i + 1:03d}.png"
            render_frame(dest, base, rings, ext, s, lon[mask], lat[mask], frp[mask],
                         [(a, b, c) for a, b, c, _ in semanas], i, acum + n)
            print(f"  frame {i + 1:03d}  {ini}..{fim}  {n:5d} focos  acum {acum + n:6d}")
        acum += n

    print("ok")


if __name__ == "__main__":
    sys.exit(main())
