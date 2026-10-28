# API MapBiomas Fogo — comportamento

Base `https://plataforma.monitorfogo.mapbiomas.org/api`; docs em `/api/docs/`.

- `GET /api/statistics/area/legalAmazon/1/legalAmazon?year=&monthStart=&monthEnd=` → `areaHa`. Granularidade **mensal**; um ano por chamada.
- `GET /api/maps/fire/monthly?territoryType=legalAmazon&territoryCode=1&year=&monthStart=&monthEnd=` → devolve URL de tiles do **Google Earth Engine**. `/heatmap/monthly` é a variante com alpha mais denso. `/api/maps/fire/monthly/gif` (params `coordinates` ring fechado, `theme`, `year`, `monthStart`, `monthEnd`) devolve `{"url": ...}` de `videoThumbnails`.
- `GET /api/territories/legalAmazon/1/bounds`; tiles de limite em `/api/territories/shape/tiles/{type}/{code}/{grouping}/{z}/{x}/{y}.mvt`.

**Gotchas**: (1) map ids do GEE **expiram** — nunca cachear/persistir a URL de tiles, buscar ao vivo a cada carregamento; (2) uma chamada por ano (período de 4 anos = 4 chamadas); (3) CORS `*`, então fetch direto no navegador funciona; (4) meses futuros retornam `null` (out/2026 nulo → 2026 "Jan–Out" = Jan–Set).