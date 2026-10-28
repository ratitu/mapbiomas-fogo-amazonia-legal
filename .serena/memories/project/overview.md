# mapbiomas_Fogo_API — visão geral

Não é um app só: é um **hub de produtos** sobre fogo na Amazônia Legal (INPE BDQueimadas + MapBiomas Fogo). Cada produto é independente e tem seu próprio pipeline.

Produtos e artefatos (raiz do repo = /home/ratitu/Documents/claude/mapbiomas_Fogo_API):
- **Dados/API**: `fetch_burned_area_legal_amazon.py` (área queimada em ha), `download_fire_gif.py` (GIF direto da API), `burned_area_legal_amazon.md`, `README.md`.
- **Site estático MapLibre** (`website/`): dois mapas sincronizados (Período 1 × Período 2), rasters de cicatriz ao vivo da API. É o artefato documentado no README.
- **Site "globe"** (`website-globe/` + raiz `index.html`/`assets/`): build Vite/React de um visualizador MapLibre Globe. **Só o build está no repo — o source não.** Publicado no GitHub Pages.
- **GIFs/MP4s matplotlib** (`make_daily_gif.py`, `make_weekly_gif.py`, `..._esri.py`, `..._esri2.py`): linhagem antiga, gera `fogo_amazonia_legal_2026_*.gif/.mp4`.
- **Timelapse semanal** (`timelapse/`): renderer PIL de alta qualidade, 1 frame = 1 semana, dois formatos (1080×1920 e 1920×1080). Usa o design system.
- **Design system** (`design/`): `deckmap.py` (código) + `DESIGN.md` (spec) + `exemplo.py` (produto de exemplo). Fonte única do visual dos vídeos.
- **Carrossel Instagram** (`carousel/`): Python gera HTML (6 slides 1080×1350, SVG inline), `export.mjs` exporta PNG via Playwright, `verify.mjs` valida geometria.

Tamanho: ~250 MB (timelapse 153 MB, GIF diário 34 MB, GeoJSON INPE 24 MB, .git 12 MB). Tudo é dado/derivado; nada de build de app no fluxo principal.

O repositório **é** git (remoto GitHub) — ver mem:project/git-deploy.