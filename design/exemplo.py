#!/usr/bin/env python3
"""Exemplo mínimo de um produto novo usando o design system.

Não é fogo, não é Amazônia, não é satélite: é só um dado semanal qualquer
passando pelo mesmo chrome. Serve como ponto de partida — copie este arquivo
e troque a parte de dados.

    python design/exemplo.py
    -> design/exemplo_portrait.png   (1080x1920)
    -> design/exemplo_landscape.png  (1920x1080)
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from design import deckmap as DM  # noqa: E402

AQUI = Path(__file__).resolve().parent
FORMATOS = {"portrait": (1080, 1920), "landscape": (1920, 1080)}

# ---------------------------------------------------------------- 1. os dados
# Série semanal sintética: 25 semanas, crescimento acelerado no fim.
rng = np.random.default_rng(7)
semanas = [date(2026, 5, 4) + timedelta(days=7 * i) for i in range(25)]
valores = np.round(180 * np.exp(np.linspace(0, 3.1, 25)) * rng.uniform(0.65, 1.35, 25))
serie = list(zip(semanas, valores))
idx = 24


def spec(i: int, orient: str) -> DM.Spec:
    """Conteúdo de um quadro — o produto só monta isto."""
    ini = semanas[i]
    fim = ini + timedelta(days=6)
    return DM.Spec(
        eyebrow="ÁREA QUEIMADA · RECORTE SUL",
        data=DM.rotulo_semana(ini, fim),
        valor=DM.milhar(valores[i]),
        valor_nota="hectares\nafetados\nna semana" if orient == "portrait"
                   else "hectares afetados\nna semana",
        serie_titulo="ÁREA POR SEMANA · MAI → OUT",
        serie=serie,
        idx=i,
        acumulado=DM.milhar(int(valores[: i + 1].sum())),
        acumulado_titulo="ACUMULADO NO PERÍODO",
        escala_titulo="ESCALA DE INTENSIDADE",
        escala=[("baixa", DM.ramp(0.25)), ("média", DM.ramp(0.65)), ("alta", DM.ramp(1.0))],
        fontes=("DADOS: SÉRIE SINTÉTICA DE EXEMPLO",) if orient == "portrait"
               else ("DADOS: SÉRIE SINTÉTICA DE EXEMPLO", "DESIGN: design/deckmap.py"),
    )


# ------------------------------------------------------- 2. o "mapa" (fake)
def fundo(W: int, H: int, cx: float, cy: float, sup: int = 2) -> Image.Image:
    """Fundo qualquer passando pelo mesmo tratamento de satélite do design."""
    Ws, Hs = W * sup, H * sup
    yy, xx = np.mgrid[0:Hs, 0:Ws].astype(np.float32)
    a = 0.55 + 0.25 * np.sin(xx / (Ws / 6.0)) * np.cos(yy / (Hs / 5.0))
    img = np.dstack([a * 62, a * 74, a * 58]).astype(np.uint8)
    return DM.trata_satelite(Image.fromarray(img), W, H, cx, cy, sup)


def pontos(img: Image.Image, W: int, H: int, i: int, box, sup: int = 2) -> Image.Image:
    """Alguns pontos com intensidade variável — a camada de mapa do design."""
    r = np.random.default_rng(100 + i)
    n = int(120 + 380 * (valores[i] / valores.max()))
    x0, x1, y0, y1 = box
    X = r.uniform(x0, x1, n) * W * sup
    Y = r.uniform(y0, y1, n) * H * sup
    t = r.uniform(0.05, 1.0, n)
    return DM.camada_pontos(img, X, Y, t, sup)


# ------------------------------------------------------------------ 3. saída
for orient, (W, H) in FORMATOS.items():
    cx = cy = 0.5
    caixa = (0.06, 0.94, 0.10, 0.90)
    if orient == "landscape":
        cx = DM.SPLIT + (W - DM.SPLIT) / 2 / W      # centro do painel de mapa
        caixa = (DM.SPLIT / W + 0.03, 0.97, 0.10, 0.90)
    base = fundo(W, H, cx * W, cy * H)
    base = pontos(base, W, H, idx, caixa).resize((W, H), Image.LANCZOS).convert("RGBA")
    img = DM.compor(base, spec(idx, orient), orient)
    img = DM.marca_dagua(img)
    out = AQUI / f"exemplo_{orient}.png"
    img.convert("RGB").save(out)
    print(f"{out.name}: {W}x{H} · {DM.milhar(valores[idx])} no quadro {idx + 1}/25")
