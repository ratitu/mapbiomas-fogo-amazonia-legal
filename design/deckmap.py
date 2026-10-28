#!/usr/bin/env python3
"""deckmap — sistema de design dos produtos de mapa (vídeo e still).

Este módulo é o *design*, não o produto. Um produto novo (outro dado, outro
recorte, outro período) fornece apenas dados, projeção e enquadramento, e
compõe o quadro com `compor()`.

O que mora aqui:
  - paleta, tipografia e escala tipográfica
  - geometria dos dois formatos: vertical 1080x1920 e horizontal 1920x1080
  - tratamento da imagem de satélite (dessatura, escurece, vinheta)
  - desenho das camadas de mapa (contorno e pontos com bloom aditivo)
  - chrome de dados (número-herói, tira de barras, escala, fontes)
  - marca d'água

O que NÃO mora aqui: leitura de dados, mercator, enquadramento, tiles.

Referência completa (tokens, grades, regras): design/DESIGN.md
Exemplo executável: design/exemplo.py
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Sequence

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --------------------------------------------------------------------- tokens
INK = (242, 239, 233)          # texto principal
DIM = (170, 170, 165)          # texto secundário
ACCENT = (255, 178, 44)        # destaque / valor da semana corrente
HOT = (255, 96, 48)            # acento quente (reserva)
RED_LO = (205, 40, 38)         # intensidade baixa
RED_HI = (255, 72, 48)         # intensidade alta
PANEL = (7, 9, 12)             # painel opaco do formato horizontal
RULE = (30, 34, 40)            # divisória de 1 px

SPLIT = 640                    # horizontal: largura do painel de texto

MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
         "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

FONT_DIR = Path("/usr/share/fonts/truetype/roboto/hinted")
F_BOLD = FONT_DIR / "RobotoCondensed-Bold.ttf"
F_MED = FONT_DIR / "RobotoCondensed-Medium.ttf"
F_REG = FONT_DIR / "Roboto-Regular.ttf"

# escala tipográfica por formato (px, na resolução final)
TIPO = {
    "portrait": dict(eyebrow=26, data=46, hero=196, nota=27, small=21, micro=20, acum=27),
    "landscape": dict(eyebrow=19, data=46, hero=132, nota=26, small=19, micro=18, acum=34),
}

LOGO_PADRAO = Path(__file__).resolve().parent.parent / "logo-no-background.svg"
LOGO_PX = 112                  # lado do selo
LOGO_MX, LOGO_MY = 40, 32      # margens direita / inferior
LOGO_ALPHA = 0.92

_LOGO_CACHE: dict[tuple, Image.Image] = {}
_FONTE_CACHE: dict[tuple, ImageFont.FreeTypeFont] = {}


# --------------------------------------------------------------------- util
def milhar(n) -> str:
    """1234567 -> '1.234.567' (padrão pt-BR)."""
    return f"{int(n):,}".replace(",", ".")


def rotulo_semana(ini: date, fim: date) -> str:
    """'19 – 25 OUT 2026' ou '27 JUL – 02 AGO 2026' quando vira o mês."""
    if ini.month == fim.month:
        return f"{ini.day:02d} – {fim.day:02d} {MESES[fim.month - 1]} {fim.year}"
    return (f"{ini.day:02d} {MESES[ini.month - 1]} – "
            f"{fim.day:02d} {MESES[fim.month - 1]} {fim.year}")


def _fonte(caminho: Path, tamanho: int):
    chave = (str(caminho), tamanho)
    if chave not in _FONTE_CACHE:
        _FONTE_CACHE[chave] = ImageFont.truetype(str(caminho), tamanho)
    return _FONTE_CACHE[chave]


def fontes(orient: str) -> dict:
    t = TIPO[orient]
    return {
        "eyebrow": _fonte(F_MED, t["eyebrow"]),
        "data": _fonte(F_BOLD, t["data"]),
        "hero": _fonte(F_BOLD, t["hero"]),
        "nota": _fonte(F_MED, t["nota"]),
        "small": _fonte(F_REG, t["small"]),
        "micro": _fonte(F_MED, t["micro"]),
        "acum": _fonte(F_BOLD, t["acum"]),
    }


def texto(d, xy, s, font, fill, spacing=0, anchor="la"):
    """Texto com letter-spacing opcional (o tracking é mais aberto nos rótulos)."""
    if spacing == 0:
        d.text(xy, s, font=font, fill=fill, anchor=anchor)
        return
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill, anchor=anchor)
        x += d.textlength(ch, font=font) + spacing


def gradiente_v(d, box, c0, c1):
    """Degradê vertical de RGBA — usado nos scrims de topo/rodapé."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        k = (y - y0) / max(1, (y1 - y0 - 1))
        d.line([(x0, y), (x1, y)],
               fill=tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(4)))


def ramp(t: float):
    """Cor da rampa de intensidade em t ∈ [0, 1]."""
    return tuple(int(RED_LO[i] + (RED_HI[i] - RED_LO[i]) * t) for i in range(3))


# --------------------------------------------------------------- camada mapa
def trata_satelite(img: Image.Image, W: int, H: int, cx: float, cy: float,
                   sup: int = 1) -> Image.Image:
    """Dessatura, escurece e aplica vinheta — o satélite vira fundo, não assunto.

    cx, cy: centro do assunto em px do quadro final (a vinheta acompanha o
    assunto, não o centro geométrico).
    """
    a = np.asarray(img, dtype=np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    a = a * 0.78 + (lum[..., None] * 0.22)              # dessaturação leve
    a = np.clip(a, 0, 1) ** 1.02 * 0.86                 # escurece sem achatar
    a = a * np.array([0.92, 1.03, 0.96], dtype=np.float32)  # puxa o verde
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

    yy, xx = np.mgrid[0:H * sup, 0:W * sup]
    vx, vy = cx * sup, cy * sup
    cxn = max(vx, W * sup - vx)
    cyn = max(vy, H * sup - vy)
    d = np.sqrt(((xx - vx) / cxn) ** 2 + ((yy - vy) / cyn) ** 2) / math.sqrt(2)
    vig = 1.0 - 0.30 * np.clip(d, 0, 1) ** 1.9
    arr = np.asarray(out, dtype=np.float32) * vig[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def camada_limite(img: Image.Image, aneis_px: Sequence[np.ndarray], W: int) -> Image.Image:
    """Contorno do território: preenchimento 8% + linha branca 155/255.

    aneis_px: lista de arrays (N, 2) já em px (espaço supersampleado).
    """
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lw = max(3, round(3 * W / 1080))
    for pts_arr in aneis_px:
        pts = [tuple(map(float, p)) for p in pts_arr]
        d.polygon(pts, fill=(255, 255, 255, 12))
        d.line(pts + [pts[0]], fill=(255, 255, 255, 155), width=lw, joint="curve")
    out = img.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def camada_pontos(img: Image.Image, X, Y, t, sup: int = 1) -> Image.Image:
    """Pontos de calor: bloom aditivo (screen) + núcleo quente, tamanho por intensidade.

    X, Y: px (espaço supersampleado). t: intensidade normalizada ∈ [0, 1].
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    t = np.clip(np.asarray(t, dtype=float), 0, 1)
    rgb = np.array(RED_LO, dtype=np.float32) + (
        np.array(RED_HI, dtype=np.float32) - np.array(RED_LO, dtype=np.float32)) * t[:, None]

    # brilho
    glow = Image.new("RGB", img.size, (0, 0, 0))
    dg = ImageDraw.Draw(glow)
    for x, y, c, tt in zip(X, Y, rgb, t):
        r = 7.5 + 4.5 * tt
        dg.ellipse((x - r, y - r, x + r, y + r),
                   fill=(int(c[0] * 0.70), int(c[1] * 0.34), int(c[2] * 0.34)))
    glow = glow.filter(ImageFilter.GaussianBlur(10 * sup))
    ga = np.asarray(glow, dtype=np.float32) * 1.05

    base = np.asarray(img.convert("RGB"), dtype=np.float32)
    out = 255.0 - (255.0 - base) * (255.0 - ga) / 255.0      # screen

    # núcleo
    core = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(core)
    for x, y, c, tt in zip(X, Y, rgb, t):
        r = 2.7 + 2.2 * tt
        w = 0.15 + 0.35 * tt
        cc = [v * (1 - w) + 255 * w for v in c]
        dc.ellipse((x - r, y - r, x + r, y + r),
                   fill=(int(cc[0]), int(cc[1]), int(cc[2]), 240))
    core = core.filter(ImageFilter.GaussianBlur(0.8 * sup))
    ca = np.asarray(core, dtype=np.float32)
    alpha = ca[..., 3:4] / 255.0
    out = out * (1 - alpha) + ca[..., :3] * alpha

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------- chrome
def barras(d, serie: Sequence[tuple[date, float]], idx: int,
           x0: float, x1: float, base_y: float, top_y: float, f_micro):
    """Tira de barras: passado em cinza, semana corrente em ACCENT, futuro quase nulo."""
    n = len(serie)
    passo = (x1 - x0) / n
    vmax = max(v for _, v in serie)
    for i, (_, v) in enumerate(serie):
        h = max(5.0, (base_y - top_y) * (v / vmax))
        bx = x0 + i * passo
        bw = passo * 0.58
        if i == idx:
            col = ACCENT + (255,)
        elif i < idx:
            col = INK + (110,)
        else:
            col = INK + (38,)
        d.rectangle((bx, base_y - h, bx + bw, base_y), fill=col)
    d.line((x0, base_y + 1, x1, base_y + 1), fill=INK + (60,), width=1)

    for lbl, i in ((MESES[serie[0][0].month - 1], 0),
                   (MESES[serie[len(serie) // 2][0].month - 1], len(serie) // 2),
                   (MESES[serie[-1][0].month - 1], len(serie) - 1)):
        bx = x0 + (i + 0.29) * passo
        d.text((bx, base_y + 10), lbl, font=f_micro, fill=DIM + (170,), anchor="ma")


def legenda_escala(d, X0, y, f_micro, f_small, titulo: str,
                   itens: Sequence[tuple[str, tuple]] = ()):
    """Rótulo de escala com amostras de cor e faixas."""
    texto(d, (X0, y), titulo, f_micro, DIM + (200,), spacing=2.6)
    x = X0
    for lbl, col in itens:
        d.ellipse((x - 2, y + 30, x + 15, y + 47), fill=col + (240,))
        d.text((x + 24, y + 27), lbl, font=f_small, fill=DIM + (220,))
        x += 24 + d.textlength(lbl, font=f_small) + 34


@dataclass
class Spec:
    """Conteúdo de um quadro. Nada aqui é específico de fogo."""
    eyebrow: str
    data: str                       # já formatado: rotulo_semana(...)
    valor: str                      # número-herói, já formatado: milhar(...)
    valor_nota: str = "focos detectados\nna semana"
    serie_titulo: str = "FOCOS POR SEMANA"
    serie: Sequence[tuple[date, float]] = field(default_factory=tuple)
    idx: int = 0
    acumulado: str = ""
    acumulado_titulo: str = "ACUMULADO NO PERÍODO"
    escala_titulo: str = "ESCALA DE INTENSIDADE (FRP)"
    escala: Sequence[tuple[str, tuple]] = field(default_factory=tuple)
    fontes: Sequence[str] = field(default_factory=tuple)


def ui_portrait(img: Image.Image, spec: Spec, W: int = 1080, H: int = 1920) -> Image.Image:
    """Vertical: o dado manda. Scrim no topo e no rodapé, tira de barras larga."""
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(scrim)
    gradiente_v(ds, (0, 0, W, 700), (0, 0, 0, 200), (0, 0, 0, 0))
    gradiente_v(ds, (0, 1320, W, H), (0, 0, 0, 40), (0, 0, 0, 225))
    img = Image.alpha_composite(img, scrim)

    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ui)
    f = fontes("portrait")

    texto(d, (78, 96), spec.eyebrow, f["eyebrow"], INK + (190,), spacing=3.2)
    d.text((78, 140), spec.data, font=f["data"], fill=(255, 255, 255, 245))

    d.text((74, 214), spec.valor, font=f["hero"], fill=INK + (255,))
    largura = d.textlength(spec.valor, font=f["hero"])
    d.multiline_text((78 + largura + 22, 296), spec.valor_nota, font=f["nota"],
                     fill=ACCENT + (245,), spacing=6)

    legenda_escala(d, 78, 1420, f["micro"], f["small"], spec.escala_titulo, spec.escala)

    texto(d, (78, 1500), spec.serie_titulo, f["micro"], DIM + (200,), spacing=2.6)
    d.text((W - 78, 1500), f"ACUMULADO {spec.acumulado}", font=f["nota"],
           fill=INK + (235,), anchor="ra")

    barras(d, spec.serie, spec.idx, 78, W - 78, 1732, 1560, f["micro"])

    for i, linha in enumerate(spec.fontes):
        texto(d, (78, 1806 + i * 24), linha, f["micro"], DIM + (135,), spacing=1.6)

    return Image.alpha_composite(img, ui)


def ui_landscape(img: Image.Image, spec: Spec, W: int = 1920, H: int = 1080) -> Image.Image:
    """Horizontal: coluna de texto à esquerda, mapa à direita."""
    # 1) painel opaco em camada própria (texto com alpha por cima abriria buraco nele)
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dp = ImageDraw.Draw(panel)
    dp.rectangle((0, 0, SPLIT, H), fill=PANEL + (255,))
    for i in range(70):                                   # sombra na emenda
        a = int(95 * (1 - i / 70) ** 2.2)
        dp.line((SPLIT + i, 0, SPLIT + i, H), fill=(0, 0, 0, a))
    dp.rectangle((SPLIT - 1, 0, SPLIT - 1, H - 1), fill=RULE + (255,))
    img = Image.alpha_composite(img, panel)

    # 2) texto e gráficos por cima do painel já composto
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ui)
    f = fontes("landscape")
    X0 = 80

    texto(d, (X0, 72), spec.eyebrow, f["eyebrow"], INK + (190,), spacing=3.0)
    d.text((X0, 104), spec.data, font=f["data"], fill=(255, 255, 255, 245))

    d.text((X0 - 4, 176), spec.valor, font=f["hero"], fill=INK + (255,))
    d.multiline_text((X0, 346), spec.valor_nota, font=f["nota"],
                     fill=ACCENT + (245,), spacing=8)

    d.line((X0, 492, X0 + 520, 492), fill=INK + (38,), width=1)
    texto(d, (X0, 520), spec.serie_titulo, f["micro"], DIM + (200,), spacing=2.6)
    barras(d, spec.serie, spec.idx, X0, X0 + 520, 736, 560, f["micro"])

    texto(d, (X0, 792), spec.acumulado_titulo, f["micro"], DIM + (200,), spacing=2.4)
    d.text((X0 - 2, 814), spec.acumulado, font=f["acum"], fill=INK + (240,))

    legenda_escala(d, X0, 902, f["micro"], f["small"], spec.escala_titulo, spec.escala)

    for i, linha in enumerate(spec.fontes):
        texto(d, (X0, 1002 + i * 24), linha, f["micro"], DIM + (130,), spacing=1.4)

    return Image.alpha_composite(img, ui)


def compor(img: Image.Image, spec: Spec, orient: str = "portrait") -> Image.Image:
    """Aplica o chrome do formato pedido. img deve ser RGBA no tamanho final."""
    W, H = img.size
    if orient == "landscape":
        return ui_landscape(img, spec, W, H)
    return ui_portrait(img, spec, W, H)


# ---------------------------------------------------------------- marca d'água
def carrega_logo(svg: Path = LOGO_PADRAO, px: int = LOGO_PX,
                 alpha: float = LOGO_ALPHA) -> Image.Image:
    """Rasteriza o SVG em 4x, corta no bbox do alpha e reduz (selo sem margem vazia)."""
    chave = (str(svg), px, alpha)
    if chave in _LOGO_CACHE:
        return _LOGO_CACHE[chave]
    buf = io.BytesIO()
    cairosvg.svg2png(url=str(svg), write_to=buf, output_width=px * 4, output_height=px * 4)
    buf.seek(0)
    im = Image.open(buf).convert("RGBA")
    bbox = im.split()[3].getbbox()
    if bbox:
        im = im.crop(bbox)
    k = min(px / im.width, px / im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    im.putalpha(im.split()[3].point(lambda v: round(v * alpha)))
    _LOGO_CACHE[chave] = im
    return im


def marca_dagua(img: Image.Image, svg: Path = LOGO_PADRAO, px: int = LOGO_PX,
                mx: int = LOGO_MX, my: int = LOGO_MY) -> Image.Image:
    """Selo no canto inferior direito, com sombra difusa para não sumir no satélite."""
    logo = carrega_logo(svg, px)
    W, H = img.size
    x = W - mx - logo.width
    y = H - my - logo.height
    sombra = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    sombra.putalpha(logo.split()[3]
                    .filter(ImageFilter.GaussianBlur(max(2.0, px * 0.07)))
                    .point(lambda v: round(v * 0.65)))
    img.alpha_composite(sombra, (x, y + round(px * 0.045)))
    img.alpha_composite(logo, (x, y))
    return img
