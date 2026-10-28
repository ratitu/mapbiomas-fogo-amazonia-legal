# Fogo na Amazônia Legal — MapBiomas Fogo

Comparação da **área queimada na Amazônia Legal** em dois períodos, num website com
dois mapas lado a lado (MapLibre GL JS) sobre imagem de satélite Esri, com as
cicatrizes de fogo do MapBiomas Fogo carregadas ao vivo da API oficial.

- **Período 1:** 2023-01-01 a 2026-10-16 (2026 parcial) — **53.172.677,22 ha**
- **Período 2:** 2019-01-01 a 2022-12-31 — **50.174.823,93 ha**

## O que é

O projeto reúne dois componentes:

1. **Análise de dados** (`fetch_burned_area_legal_amazon.py` +
   `burned_area_legal_amazon.md`) — consulta a API do MapBiomas Fogo e calcula a
   área queimada total (hectares) de cada período dentro do limite da Amazônia Legal.
2. **Website interativo** (`website/`) — visualizador MapLibre GL JS com dois mapas
   sincronizados (Período 1 × Período 2) mostrando os rasters de cicatriz de fogo
   sobre imagem de satélite, mais o contorno da Amazônia Legal.

## Área queimada (hectares)

Fonte: MapBiomas Fogo — estatística territorial da Amazônia Legal
(`type=legalAmazon`, `code=1`, `grouping=legalAmazon`).

### Período 1 — 2023-01-01 a 2026-10-16

| Ano  | Meses    | Área queimada (ha) |
|------|----------|--------------------|
| 2023 | Jan–Dez  | 14.110.379,24      |
| 2024 | Jan–Dez  | 25.583.085,87      |
| 2025 | Jan–Dez  | 7.696.586,54       |
| 2026 | Jan–Out  | 5.782.625,57       |

**Total: 53.172.677,22 ha**

> A API tem granularidade **mensal** (não diária). Os dados de outubro/2026 ainda
> retornam `null`, portanto o valor de 2026 (Jan–Out) equivale a Jan–Set.

### Período 2 — 2019-01-01 a 2022-12-31

| Ano  | Meses    | Área queimada (ha) |
|------|----------|--------------------|
| 2019 | Jan–Dez  | 13.403.151,45      |
| 2020 | Jan–Dez  | 14.280.715,80      |
| 2021 | Jan–Dez  | 9.102.369,26       |
| 2022 | Jan–Dez  | 13.388.587,42      |

**Total: 50.174.823,93 ha**

Os valores acima são os usados no website (`website/js/app.js`). O arquivo
`burned_area_legal_amazon.md` traz a mesma análise com pequenas diferenças de
arredondamento no Período 2 (total 50.174.823,89 ha), resultantes de execuções
distintas da consulta à API.

## Estrutura do repositório

```
mapbiomas_Fogo_API/
├── README.md                              # este arquivo
├── AGENTS.md                              # guia para agentes/automação
├── burned_area_legal_amazon.md            # análise descritiva dos dois períodos
├── fetch_burned_area_legal_amazon.py      # script que consulta a API (área/ha)
├── Limites_Amazonia_Legal_2024.geojson    # contorno oficial (9,5 MB, alta resolução)
├── website/                               # visualizador MapLibre GL JS
│   ├── index.html                         # layout de dois mapas (pt-BR)
│   ├── css/style.css                      # tema escuro, grid responsivo
│   ├── js/app.js                          # lógica dos mapas + fetch da API
│   └── data/
│       └── limites_amazonia_legal.geojson # contorno simplificado (197 KB)
└── website-verify.png                     # screenshot de verificação
```

## Como rodar o website

O site é **estático**, mas precisa ser servido por HTTP (o navegador exige isso
para carregar o GeoJSON e chamar a API). Qualquer servidor estático serve:

```bash
cd website
python3 -m http.server 8765
```

Depois abra <http://localhost:8765/index.html>.

> Abrir `index.html` diretamente via `file://` **não funciona** — o fetch do
> GeoJSON e das tiles falha por restrições de origem.

## Como reproduzir os números

```bash
cd /home/ratitu/Documents/claude/mapbiomas_Fogo_API
python3 fetch_burned_area_legal_amazon.py
```

O script consulta a API ao vivo (parâmetros `year`, `monthStart`, `monthEnd` para
cada período) e recalcula os totais. Requer `requests`.

## API do MapBiomas Fogo

- Base: `https://plataforma.monitorfogo.mapbiomas.org/api`
- Documentação: `https://plataforma.monitorfogo.mapbiomas.org/api/docs/`

Endpoints usados/relevantes:

| Endpoint | Uso |
|----------|-----|
| `GET /api/statistics/area/legalAmazon/1/legalAmazon?year=&monthStart=&monthEnd=` | Área queimada em hectares (`areaHa`) por período |
| `GET /api/maps/fire/monthly?territoryType=legalAmazon&territoryCode=1&year=&monthStart=&monthEnd=` | Raster de cicatriz de fogo (retorna URL de tiles do Google Earth Engine) |
| `GET /api/maps/fire/heatmap/monthly?...` | Igual ao anterior, com alpha mais denso |
| `GET /api/territories/legalAmazon/1/bounds` | Bounding box da Amazônia Legal |
| `GET /api/territories/shape/tiles/{type}/{code}/{grouping}/{z}/{x}/{y}.mvt` | Tiles vetoriais de limites |

### Comportamento importante das tiles

- O endpoint `/api/maps/fire/monthly` retorna uma **URL de template de tiles do
  Google Earth Engine** que é **de curta duração**: os *map ids* expiram. Por
  isso o website **busca a URL ao vivo a cada carregamento** de página — não
  armazena/cacheia a URL.
- A API tem granularidade **mensal e uma chamada por ano**. Para cobrir um
  período de vários anos, o site faz **uma chamada por ano** (4 no Período 1,
  4 no Período 2).
- A API responde com `Access-Control-Allow-Origin: *`, então o `fetch` direto no
  navegador funciona.

## Funcionalidades do website

- Dois mapas MapLibre GL JS **sincronizados** (pan/zoom), Período 1 × Período 2.
- Base de satélite **Esri World Imagery** (`World_Imagery/MapServer`).
- Rasters de cicatriz de fogo carregados **ao vivo** do MapBiomas Fogo.
- Contorno da **Amazônia Legal** (ciano) desenhado **acima** das camadas de fogo.
- Chips por ano para **ligar/desligar** cada camada de fogo individualmente.
- Painel com total de hectares de cada período.
- Legenda, mensagens de status, toggle de contorno, toggle de sincronização e
  botão "Recentralizar".

## Créditos e fontes

- Dados de fogo: [MapBiomas Fogo](https://plataforma.monitorfogo.mapbiomas.org/)
- Imagem de satélite: Esri, Maxar, Earthstar Geographics, GIS User Community
- Limite: `Limites_Amazonia_Legal_2024.geojson`
- Mapa: [MapLibre GL JS](https://maplibre.org/) 4.7.1

## Notas

- Unidade: **hectares (ha)**.
- 2026 é parcial (até outubro).
- O repositório **é** git: remoto `github.com:ratitu/mapbiomas-fogo-amazonia-legal`,
  branch `main`, publicado no **GitHub Pages** pelo workflow
  `.github/workflows/deploy-pages.yml` a partir de `website-globe/` — o `website/`
  não é publicado. Apenas uma parte do projeto está versionada — os vídeos, o
  design system e os dados brutos estão fora do controle de versão.
