# GIFs matplotlib + artefatos de sessão (não documentados no README)

Linhagem dos produtos de GIF/MP4 na raiz — **não** reaproveitar sem motivo, o padrão atual é `timelapse/`:

1. `make_weekly_gif.py` — geopandas + matplotlib, sem basemap → `fogo_amazonia_legal_2026_weekly.gif` (frames em `frames_weekly/`).
2. `make_weekly_gif_esri.py` — idem + `contextily` (basemap Esri) → `..._weekly_esri.gif` (`frames_weekly_esri/`).
3. `make_weekly_gif_esri2.py` — iteração final do MP4 de Reels → `..._weekly_esri_reel2.mp4`.
4. `make_daily_gif.py` — 1 frame = 1 dia → `..._jun_set_daily.gif` (34 MB, pesado).
5. `download_fire_gif.py` — atalho: baixa o GIF pronto da API (`/api/maps/fire/monthly/gif`), sem render local.

Diferenças de design: os matplotlib usam `matplotlib`/`plt` com estilos próprios, **não** o `design/deckmap.py`. Para produto novo, usar o design system.

Outros arquivos de contexto (não são produto): `PROMPT.md`, `promptAPI.md`, `prompt_reel.md`, `learn_API.md`, `session-ses_eb7f.md`, `skills-lock.json`, `.agents/skills/` (skills geospaciais instaladas), `.omo/`, `.playwright-mcp/`, `.serena/`, `.firecrawl/`.