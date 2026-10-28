# Design system — mapas animados do canal

Especificação do visual usado nos vídeos de fogo (vertical 1080×1920 e
horizontal 1920×1080). O código que implementa tudo isto está em
[`deckmap.py`](deckmap.py); o produto que consome o sistema é
[`timelapse/render_timelapse.py`](../timelapse/render_timelapse.py).

Regra de ouro: **isto aqui é o design, não o produto.** Produto novo = dados +
projeção + enquadramento + textos. Geometria, cor, tipografia e chrome ficam
neste sistema.

---

## Princípios

1. **O mapa é a imagem, o dado é o herói.** O satélite é fundo: dessaturado,
   escurecido e com vinheta. Nada compete com os pontos.
2. **Dois formatos, dois desenhos.** O vertical e o horizontal não são o mesmo
   layout escalado — são composições próprias, com tipografia e ancoragem
   diferentes. Não tente derivar um do outro por proporção.
3. **Uma cor de acento só.** `ACCENT` marca exclusivamente "a semana que está na
   tela". Todo o resto é `INK`/`DIM` com alfa. Se duas coisas ficam amarelas, o
   quadro perde a leitura.
4. **O chrome nunca cobre o dado.** Scrim no vertical, painel opaco no
   horizontal, marca d'água em zona comprovadamente vazia.
5. **Legibilidade vem do fundo, não do texto.** Sem contorno, sem sombra em
   letra, sem caixa. Se o texto não lê, o conserto é o scrim/painel.
6. **Mapa inteiro, sempre.** Sem zoom por frame: o enquadramento é fixo e
   calculado para caber o território inteiro em todos os quadros.

---

## Tokens

### Cor

| Token | Hex | RGB | Uso |
|---|---|---|---|
| `INK` | `#F2EFE9` | 242,239,233 | texto principal, barras do passado |
| `DIM` | `#AAAAA5` | 170,170,165 | rótulos, legendas, fontes |
| `ACCENT` | `#FFB22C` | 255,178,44 | semana corrente, "nota do herói" |
| `HOT` | `#FF6030` | 255,96,48 | acento quente (reserva) |
| `RED_LO` | `#CD2826` | 205,40,38 | intensidade baixa |
| `RED_HI` | `#FF4830` | 255,72,48 | intensidade alta |
| `PANEL` | `#07090C` | 7,9,12 | painel opaco (horizontal) |
| `RULE` | `#1E2228` | 30,34,40 | divisória de 1 px |

Alfas fixos do chrome (255 = opaco):

| Elemento | Cor | Alfa |
|---|---|---|
| scrim superior (vertical) | preto | 200 → 0 em 700 px |
| scrim inferior (vertical) | preto | 40 → 225 de 1320 a H |
| eyebrow | `INK` | 190 |
| data (linha do período) | branco | 245 |
| número-herói | `INK` | 255 |
| nota do herói | `ACCENT` | 245 |
| título da série | `DIM` | 200 |
| acumulado | `INK` | 235 / 240 |
| barra corrente | `ACCENT` | 255 |
| barras do passado | `INK` | 110 |
| barras do futuro | `INK` | 38 |
| eixo da série | `INK` | 60 |
| rótulos de mês | `DIM` | 170 |
| linhas de fonte | `DIM` | 135 (vertical) · 130 (horizontal) |
| preenchimento do contorno | branco | 12 |
| linha do contorno | branco | 155 |

### Tipografia

Família única: **Roboto Condensed** (Bold / Medium) + **Roboto** Regular.
Diretório: `/usr/share/fonts/truetype/roboto/hinted`.

| Token | Vertical 1080 | Horizontal 1920 | Fonte | Uso |
|---|---|---|---|---|
| `eyebrow` | 26 | 19 | Condensed Medium | sobretítulo, tracking 3.2 / 3.0 |
| `data` | 46 | 46 | Condensed Bold | período ("19 – 25 OUT 2026") |
| `hero` | 196 | 132 | Condensed Bold | número da semana |
| `nota` | 27 | 26 | Condensed Medium | rótulo do herói, "ACUMULADO" |
| `small` | 21 | 19 | Roboto Regular | faixas da escala |
| `micro` | 20 | 18 | Condensed Medium | rótulos técnicos, fontes |
| `acum` | 27 | 34 | Condensed Bold | valor do acumulado |

Regras de texto: **só três pesos**. Rótulo técnico é MAIÚSCULA com tracking
(1.4–3.2). Número é `milhar()` (ponto de milhar, pt-BR). Data é
`rotulo_semana()`: `19 – 25 OUT 2026`, com travessão – e mês abreviado.

---

## Geometria

### Vertical — 1080×1920

Composição em três blocos: topo (identidade + herói), rodapé (série, escala,
fontes). O mapa é a área toda, com scrim nos extremos.

| Elemento | x | y | Obs |
|---|---|---|---|
| scrim superior | 0 → 1080 | 0 → 700 | preto 200 → 0 |
| eyebrow | 78 | 96 | tracking 3.2 |
| data | 78 | 140 | 46 px |
| número-herói | 74 | 214 | 196 px |
| nota do herói | 78 + largura + 22 | 296 | alinhada à direita do número |
| escala | 78 | 1420 | |
| título da série | 78 | 1500 | tracking 2.6 |
| acumulado (texto) | W − 78 | 1500 | âncora à direita |
| série de barras | 78 → W − 78 | base 1732 · topo 1560 | |
| rótulos de mês | — | 1742 | sob a base |
| fontes | 78 | 1806 | passo de 24 px entre linhas |
| marca d'água | W − 40 − 112 | H − 32 − 112 | ver § Marca d'água |

### Horizontal — 1920×1080

Coluna de texto opaca à esquerda (0 → 640) e mapa no painel direito.

| Elemento | x | y | Obs |
|---|---|---|---|
| painel | 0 → 640 | 0 → 1080 | `PANEL` opaco |
| sombra da emenda | 640 → 710 | — | 70 linhas, alfa `95·(1−i/70)^2.2` |
| divisória | 639 | 0 → 1079 | `RULE`, 1 px |
| eyebrow | 80 | 72 | tracking 3.0 |
| data | 80 | 104 | |
| número-herói | 76 | 176 | |
| nota do herói | 80 | 346 | 2 linhas, leading 8 |
| divisória fina | 80 → 600 | 492 | `INK` 38 |
| título da série | 80 | 520 | |
| série de barras | 80 → 600 | base 736 · topo 560 | |
| rótulo do acumulado | 80 | 792 | tracking 2.4 |
| valor do acumulado | 78 | 814 | 34 px |
| escala | 80 | 902 | |
| fontes | 80 | 1002 | passo 24 px |

Mapa: eixo maior de 900 px (margem de 90 px em cima e embaixo), centralizado no
painel direito (`SCREEN_CX = 640 + (W−640)/2 = 1280`, `SCREEN_CY = 540`).

---

## Componentes

### Cabeçalho
Sobretítulo (eyebrow) + período. O sobretítulo é o assunto e o recorte; o
período é a unidade temporal do quadro. Nunca inverta a hierarquia: o
sobretítulo é 190/255 de alfa, o período é branco quase cheio.

### Número-herói
O valor da semana em 196 px (vertical) / 132 px (horizontal). A nota do herói
fica **à direita** no vertical (empilhada, 3 linhas, `ACCENT`) e **abaixo** no
horizontal (2 linhas). É a única mancha de acento do quadro.

### Série de barras
Todas as semanas do período, sempre. Barra corrente em `ACCENT`; passado em
`INK` 110; futuro em `INK` 38 — o futuro visível dá a noção de "onde estamos na
temporada". Largura da barra = 58% do passo; altura mínima 5 px (semana zero
continua visível). Três rótulos de mês: primeira, do meio e última semana,
âncora `ma` deslocada 0.29 do passo.

### Escala
Rótulo técnico + três amostras de cor com faixa. As cores vêm de `ramp(t)`, a
mesma função que colore os pontos — a legenda não pode divergir do dado.

### Fontes
Uma linha no vertical, duas no horizontal (o rodapé do vertical já está cheio).
Sempre em `DIM` 130–135, `micro`, tracking 1.4–1.6. Crédito é obrigatório para
os dados e para a base de imagem.

### Marca d'água
Selo circular do canal no canto inferior direito: 112 px, margens 40 (direita) e
32 (inferior), opacidade 0.92, sombra preta difusa (blur `0.07·px`, alfa 0.65,
deslocada `0.045·px` para baixo). O SVG é rasterizado a 4× com cairosvg e
cortado no bbox do alfa — o selo fica sem a margem vazia do arquivo original.

**Regra:** a caixa do selo precisa estar vazia. Verifique antes de fixar a
posição (ver § Verificação). No produto de fogo, a caixa cobre 0 dos 59.709
pontos e 0 vértices do contorno nas duas orientações.

---

## Camadas de mapa

**Contorno do território** — `camada_limite()`: preenchimento branco 12/255,
linha branca 155/255 com espessura `max(3, 3·W/1080)`, junta curva. É o que dá
leitura de "onde é" sem precisar de rótulo.

**Pontos** — `camada_pontos()`: tamanho e cor por intensidade normalizada `t`
(log, teto em 400 MW no produto de fogo). Brilho: raio `7.5 + 4.5t`, cor
`(r·0.70, g·0.34, b·0.34)`, blur `10·sup`, mistura `screen` com ganho 1.05.
Núcleo: raio `2.7 + 2.2t`, albedo `w = 0.15 + 0.35t` puxando para branco, alfa
240, blur `0.8·sup`.

**Satélite** — `trata_satelite()`: `0.78·cor + 0.22·luminância` (dessatura),
`clip^1.02 · 0.86` (escurece sem achatar), canais `[0.92, 1.03, 0.96]` (puxa
verde), vinheta `1 − 0.30·d^1.9` centrada no assunto — não no centro do quadro.

Trabalhe sempre em 2× (`SUP = 2`) e reduza no fim com LANCZOS. É o que deixa
ponto e linha suaves sem perder o tamanho aparente.

---

## Como criar um produto novo

```python
from design import deckmap as DM

spec = DM.Spec(
    eyebrow="ÁREA QUEIMADA · RECORTE SUL",
    data=DM.rotulo_semana(ini, fim),      # "19 – 25 OUT 2026"
    valor=DM.milhar(n),                   # "6.199"
    valor_nota="hectares\nafetados\nna semana",
    serie_titulo="ÁREA POR SEMANA · MAI → OUT",
    serie=[(data_semana, valor), ...],    # todas as semanas do período
    idx=i,                                # semana corrente
    acumulado=DM.milhar(acumulado),
    escala_titulo="ESCALA DE INTENSIDADE",
    escala=[("baixa", DM.ramp(.25)), ("média", DM.ramp(.65)), ("alta", DM.ramp(1.))],
    fontes=("DADOS: ...", "BASE: ..."),
)

img = base.convert("RGBA")                     # mapa já desenhado, tamanho final
img = DM.compor(img, spec, orient)             # "portrait" | "landscape"
img = DM.marca_dagua(img)
img.convert("RGB").save(destino)
```

Passos: (1) dados → série semanal; (2) projeção e enquadramento (mapa inteiro no
quadro); (3) `DM.trata_satelite` no fundo; (4) `DM.camada_limite` e
`DM.camada_pontos`; (5) `DM.compor` + `DM.marca_dagua`; (6) sequência de PNGs →
ffmpeg `-framerate 1 -crf 17 -pix_fmt yuv420p`.

Exemplo executável, com dados sintéticos e sem rede:
[`exemplo.py`](exemplo.py) → `design/exemplo_portrait.png` e
`design/exemplo_landscape.png`.

---

## Verificação

Antes de publicar um produto novo:

1. **Uma olhada por formato.** Renderize um quadro (`--only N`) e abra. O que
   não foi visto, não foi aprovado.
2. **Caixa do selo vazia.** Projete os pontos e os vértices do território e
   confirme que nenhum cai no retângulo da marca d'água.
3. **Nada de texto colidindo.** No vertical, a linha de fontes termina antes de
   `W − 40 − 112`; o rótulo de mês "OUT" termina acima de `H − 32 − 112`.
4. **Geometria conferida por medida.** Meça o bbox do selo no PNG: deve dar
   margens exatas de 40 e 32.
5. **Frames idênticos após refatorar o sistema.** Se mexer em `deckmap.py`,
   re-renderize e compare pixel a pixel com os PNGs aprovados (MAE deve ser 0).
6. **Vídeo.** `ffprobe` confere resolução, `r_frame_rate=1/1` e número de
   frames; o MAE entre frame decodificado e PNG fica ~1,4–1,5 (só compressão).
