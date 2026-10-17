/* ------------------------------------------------------------------
 * Fogo na Amazônia Legal — comparação de dois períodos
 * MapLibre GL JS + Esri World Imagery + MapBiomas Fogo
 * ------------------------------------------------------------------ */

const API_BASE = "https://plataforma.monitorfogo.mapbiomas.org/api";
const TERRITORY = { type: "legalAmazon", code: 1, grouping: "legalAmazon" };
const BOUNDARY_URL = "data/limites_amazonia_legal.geojson";

/* View inicial — caixa da Amazônia Legal */
const AMZ_BOUNDS = [
  [-74.0, -18.1],
  [-44.0, 5.3],
];

/* ------------------------------------------------------------------
 * Dados dos períodos (MapBiomas Fogo — área queimada, hectares)
 * ------------------------------------------------------------------ */
const PERIODS = {
  period1: {
    id: "period1",
    years: [2023, 2024, 2025, 2026],
    /* último mês com dado consolidado por ano */
    lastMonth: { 2023: 12, 2024: 12, 2025: 12, 2026: 10 },
    yearArea: {
      2023: 14110379.24,
      2024: 25583085.87,
      2025: 7696586.54,
      2026: 5782625.57,
    },
    total: 53172677.22,
  },
  period2: {
    id: "period2",
    years: [2019, 2020, 2021, 2022],
    lastMonth: { 2019: 12, 2020: 12, 2021: 12, 2022: 12 },
    yearArea: {
      2019: 13403151.45,
      2020: 14280715.8,
      2021: 9102369.26,
      2022: 13388587.42,
    },
    total: 50174823.93,
  },
};

/* Cor única do fogo (cicatriz), em cima da imagem de satélite */
const FIRE = {
  rasterOpacity: 0.92,
  lineColor: "#00e5ff",
  fillColor: "#00e5ff",
};

/* ------------------------------------------------------------------
 * Helpers
 * ------------------------------------------------------------------ */
const nf = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const nfCompact = new Intl.NumberFormat("pt-BR", {
  notation: "compact",
  maximumFractionDigits: 2,
});

function formatHa(v) {
  return nf.format(Math.round(v));
}
function formatHaCompact(v) {
  return nfCompact.format(v) + " ha";
}

function buildStyle() {
  return {
    version: 8,
    sources: {
      "esri-sat": {
        type: "raster",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        ],
        tileSize: 256,
        maxzoom: 19,
        attribution:
          "Imagem: Esri, Maxar, Earthstar Geographics, GIS User Community",
      },
      boundary: {
        type: "geojson",
        data: BOUNDARY_URL,
      },
    },
    layers: [
      { id: "esri-sat", type: "raster", source: "esri-sat" },
      {
        id: "boundary-fill",
        type: "fill",
        source: "boundary",
        paint: {
          "fill-color": FIRE.fillColor,
          "fill-opacity": 0.03,
        },
      },
      {
        id: "boundary-line",
        type: "line",
        source: "boundary",
        paint: {
          "line-color": FIRE.lineColor,
          "line-width": 1.3,
          "line-opacity": 0.85,
        },
      },
    ],
  };
}

/* Names of the burned-area layers, per period, in add order */
const burnedLayers = { period1: [], period2: [] };

/* ------------------------------------------------------------------
 * Fetch tile template for one year from MapBiomas Fogo
 * ------------------------------------------------------------------ */
async function fetchYearTileUrl(year, monthEnd) {
  const params = new URLSearchParams({
    territoryType: TERRITORY.type,
    territoryCode: String(TERRITORY.code),
    year: String(year),
    monthStart: "1",
    monthEnd: String(monthEnd),
  });
  const url = `${API_BASE}/maps/fire/monthly?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} em ${year}`);
  const json = await res.json();
  if (!json || !json.url) throw new Error(`Sem URL de tiles para ${year}`);
  return json.url;
}

/* ------------------------------------------------------------------
 * Build one pane (map + legend) for a period
 * ------------------------------------------------------------------ */
function createPane(period, shared) {
  const mapEl = document.getElementById(`map-${period.id}`);
  const legendEl = document.getElementById(`legend-${period.id}`);
  const statusEl = document.getElementById(`status-${period.id}`);
  const statEl = document.getElementById(`stat-${period.id}`);

  statEl.textContent = formatHa(period.total);
  statEl.title = `${formatHa(period.total)} hectares`;

  const map = new maplibregl.Map({
    container: mapEl,
    style: buildStyle(),
    center: [-59.0, -6.4],
    zoom: 3.4,
    attributionControl: { compact: true },
    maxZoom: 14,
  });

  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: "metric" }), "bottom-right");

  shared.maps[period.id] = map;

  /* Legend skeleton */
  legendEl.innerHTML = `<div class="legend-title">Área queimada</div>
    <div class="legend-row"><span class="legend-swatch" style="background:#ff5a3c"></span> Cicatriz de fogo</div>
    <div class="legend-title" style="margin-top:.35rem">Anos (clique para filtrar)</div>
    <div class="legend-years" id="years-${period.id}"></div>`;

  map.on("load", () => {
    map.fitBounds(AMZ_BOUNDS, { padding: 16, animate: false });
    loadPeriod(period, map, statusEl);
  });

  return map;
}

/* ------------------------------------------------------------------
 * Load all years of a period and add them as raster layers
 * ------------------------------------------------------------------ */
async function loadPeriod(period, map, statusEl) {
  setStatus(statusEl, "Carregando dados de fogo…");

  const results = await Promise.allSettled(
    period.years.map(async (year) => {
      const monthEnd = period.lastMonth[year] || 12;
      const url = await fetchYearTileUrl(year, monthEnd);
      return { year, url };
    })
  );

  let ok = 0;
  const yearsBox = document.getElementById(`years-${period.id}`);

  results.forEach((r, i) => {
    const year = period.years[i];
    const srcId = `fire-${period.id}-${year}`;
    const layerId = `${srcId}-layer`;
    if (r.status === "fulfilled") {
      try {
        map.addSource(srcId, {
          type: "raster",
          tiles: [r.value.url],
          tileSize: 256,
        });
        map.addLayer(
          {
            id: layerId,
            type: "raster",
            source: srcId,
            paint: {
              "raster-opacity": FIRE.rasterOpacity,
              "raster-fade-duration": 0,
            },
          },
          "boundary-fill"
        );
        burnedLayers[period.id].push(layerId);
        ok++;
      } catch (e) {
        console.warn(`Falha ao adicionar camada ${year}:`, e);
      }
    } else {
      console.warn(`Falha ao carregar tiles ${year}:`, r.reason);
    }

    /* year chip */
    if (yearsBox) {
      const chip = document.createElement("label");
      chip.className = "year-chip";
      chip.innerHTML = `<input type="checkbox" checked data-layer="${layerId}" />
        <span>${year}</span>
        <span class="year-chip__area">${formatHaCompact(period.yearArea[year] || 0)}</span>`;
      const cb = chip.querySelector("input");
      cb.addEventListener("change", () => {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(
            layerId,
            "visibility",
            cb.checked ? "visible" : "none"
          );
        }
      });
      yearsBox.appendChild(chip);
    }
  });

  if (ok === 0) {
    setStatus(
      statusEl,
      "Não foi possível carregar os tiles de fogo. Verifique a conexão com a API do MapBiomas.",
      true
    );
  } else {
    setStatus(statusEl, `${ok} ano(s) carregado(s) sobre a imagem de satélite.`);
    setTimeout(() => hideStatus(statusEl), 3500);
  }
}

/* ------------------------------------------------------------------
 * Status helpers
 * ------------------------------------------------------------------ */
function setStatus(el, msg, isError = false) {
  el.textContent = msg;
  el.classList.add("is-visible");
  el.classList.toggle("is-error", isError);
}
function hideStatus(el) {
  el.classList.remove("is-visible");
}

/* ------------------------------------------------------------------
 * Map synchronisation
 * ------------------------------------------------------------------ */
function setupSync(shared) {
  let syncing = false;
  const handler = (srcId) => () => {
    if (!shared.sync || syncing) return;
    const src = shared.maps[srcId];
    const dst = shared.maps[srcId === "period1" ? "period2" : "period1"];
    if (!src || !dst) return;
    syncing = true;
    dst.jumpTo({
      center: src.getCenter(),
      zoom: src.getZoom(),
      bearing: src.getBearing(),
      pitch: src.getPitch(),
    });
    syncing = false;
  };
  shared.maps.period1.on("move", handler("period1"));
  shared.maps.period2.on("move", handler("period2"));
}

/* ------------------------------------------------------------------
 * Boot
 * ------------------------------------------------------------------ */
function boot() {
  const shared = { maps: {}, sync: true };

  const p1 = createPane(PERIODS.period1, shared);
  const p2 = createPane(PERIODS.period2, shared);

  /* boundary visibility toggle (applies to both maps) */
  const boundaryToggle = document.getElementById("toggle-boundary");
  boundaryToggle.addEventListener("change", () => {
    const vis = boundaryToggle.checked ? "visible" : "none";
    [p1, p2].forEach((m) => {
      ["boundary-fill", "boundary-line"].forEach((id) => {
        if (m.getLayer(id)) m.setLayoutProperty(id, "visibility", vis);
      });
    });
  });

  /* sync toggle */
  const syncToggle = document.getElementById("toggle-sync");
  syncToggle.addEventListener("change", () => {
    shared.sync = syncToggle.checked;
  });

  /* reset */
  document.getElementById("reset-view").addEventListener("click", () => {
    [p1, p2].forEach((m) => m.fitBounds(AMZ_BOUNDS, { padding: 16, duration: 600 }));
  });

  setupSync(shared);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
