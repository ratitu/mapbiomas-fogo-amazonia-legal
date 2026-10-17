# Burned Area within Legal Amazon (MapBiomas Fogo)

This document records the total burned area (hectares) within the Legal Amazon limits for the requested periods, calculated using the MapBiomas Fogo API. The boundary reference used is `Limites_Amazonia_Legal_2024.geojson`.

## Period 1: 2023-01-01 to 2026-10-16

Yearly burned area (ha) as reported by MapBiomas Fogo territorial statistics for Legal Amazon (type=legalAmazon, code=1, grouping=legalAmazon):

| Year | Months included | Burned area (ha) |
|------|----------------|-------------------|
| 2023 | Jan–Dec | 14,110,379.24 |
| 2024 | Jan–Dec | 25,583,085.87 |
| 2025 | Jan–Dec | 7,696,586.54 |
| 2026 | Jan–Oct | 5,782,625.57 |

**Total (2023-01-01 to 2026-10-16): 53,172,677.22 ha**

> Note: The API is month-granular (year/monthStart/monthEnd), not day-granular. October 2026 data currently returns `null` (not yet loaded), so the Jan–Oct 2026 value equals Jan–Sep.

## Period 2: 2019-01-01 to 2022-12-31

| Year | Months included | Burned area (ha) |
|------|----------------|-------------------|
| 2019 | Jan–Dec | 13,403,151.45 |
| 2020 | Jan–Dec | 14,280,715.79 |
| 2021 | Jan–Dec | 9,102,369.25 |
| 2022 | Jan–Dec | 13,388,587.40 |

**Total (2019-01-01 to 2022-12-31): 50,174,823.89 ha**

## Data source (MapBiomas Fogo API)

- Base URL: https://plataforma.monitorfogo.mapbiomas.org/api
- Docs: https://plataforma.monitorfogo.mapbiomas.org/api/docs/
- Endpoint used: `/api/statistics/area/{type}/{code}/{grouping}` (returns `areaHa`)
- Query params (month granularity): `year`, `monthStart`, `monthEnd`
- Territorial params (Legal Amazon):
  - type = `legalAmazon`
  - code = `1`
  - grouping = `legalAmazon`
- Confirmation: `/api/territories/search/amazonia` (code 1 for Legal Amazon)
- Values above were obtained by aggregating monthly/yearly results from the statistics endpoint to match the requested periods.

## Notes

- Boundary reference file: `Limites_Amazonia_Legal_2024.geojson` (for context; totals above use API territorial statistics for Legal Amazon).
- 2026 is partial (through October; October data not yet available). All other years are full calendar years.
- Units: hectares (ha).

## Reproducibility

A script to reproduce/inspect values is provided in `fetch_burned_area_legal_amazon.py`. It fetches live from the API (year/monthStart/monthEnd) for each period and re-computes the totals. Re-run it to refresh values:

```
cd /home/ratitu/Documents/claude/mapbiomas_Fogo_API
python3 fetch_burned_area_legal_amazon.py
```
