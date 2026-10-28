# timelapse/ — produto de vídeo (focos semanais)

`render_timelapse.py` (272 linhas) = **só produto**: dados, mercator, tiles Esri, enquadramento, sequência de frames. Todo o visual vem de `design/deckmap.py` (`from design import deckmap as DM`; exige `sys.path.insert(0, str(ROOT))` porque o script vive em `timelapse/`).

- Entrada: `bdqueimadas_2026-05-01_2026-10-27.geojson` (raiz) + `limites_amazonia_legal.geojson` (raiz, 9,5 MB).
- `--size portrait|landscape` define `W,H,ORIENT,SCREEN_CX,SCREEN_CY,FRAMES`; `--only N` renderiza 1 semana; `--rebase` refaz o basemap (tiles Esri z8, cache em `timelapse/cache/`, 31 MB).
- Saída: `timelapse/frames/` (1920×1080, 64 MB) e `timelapse/frames_1920x1080/` (1080×1920, 53 MB) — **os nomes das pastas estão invertidos em relação à orientação**: `frames/` = horizontal, `frames_1920x1080/` = vertical. 25 frames cada.
- Entregáveis: `timelapse/focos_amazonia_legal_2026_1080x1920.mp4` e `..._1920x1080.mp4` (1 fps, CRF 17). Não regerar sem necessidade — os PNGs atuais são byte-idênticos aos usados na codificação.
- Enquadramento fixo: vertical usa `s = W*0.926/(ax1-ax0)`; horizontal `s = 900/(ay1-ay0)` (90 px de margem) e painel de texto de 640 px à esquerda.