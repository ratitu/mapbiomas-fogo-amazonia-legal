# website/ — MapLibre duplo (estático, sem build)

- `website/index.html` + `css/style.css` + `js/app.js` (~330 linhas) + `data/limites_amazonia_legal.geojson` (197 KB, versão simplificada com `ogr2ogr -simplify 0.005` a partir do arquivo de 9,5 MB da raiz).
- `app.js`: constantes no topo `API_BASE`, `TERRITORY`, `BOUNDARY_URL`, `AMZ_BOUNDS`, `PERIODS`, `FIRE`.
  - `PERIODS` guarda hectares **hardcoded** espelhando a API: P1 2023–2026 = 53.172.677,22 ha (2023: 14.110.379,24 · 2024: 25.583.085,87 · 2025: 7.696.586,54 · 2026: 5.782.625,57); P2 2019–2022 = 50.174.823,93 ha.
  - `buildStyle()` monta style v8: fonte raster `esri-sat` + GeoJSON `boundary`; ordem `esri-sat` → `boundary-fill` → `boundary-line`.
  - `fetchYearTileUrl(year, monthEnd)`: **uma chamada por ano**; rasters inseridos com `map.addLayer(layer, "boundary-fill")` para ficar **abaixo** do contorno.
  - `loadPeriod` usa `Promise.allSettled`; `setupSync(shared)` sincroniza pan/zoom com guarda `syncing`.
- Armadilha já vivida: em `loadPeriod`, `srcId`/`layerId` **precisam** ser declarados no topo do callback do `forEach` (antes do `if (r.status === "fulfilled")`), senão dá `ReferenceError` no chip do ano.
- UI pt-BR, tema escuro via variáveis CSS em `:root` (`--bg`, `--panel`, `--line`, `--text`, `--accent`, `--accent-2`, `--p1`, `--p2`), classes BEM (`.map-pane__head`, `.map-pane__badge--p1`).