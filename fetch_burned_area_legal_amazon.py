#!/usr/bin/env python3
"""
Fetch burned area totals for Legal Amazon using MapBiomas Fogo API (LIVE fetch).

API docs: https://plataforma.monitorfogo.mapbiomas.org/api/docs/
Endpoint: GET /api/statistics/area/{type}/{code}/{grouping}
Query params: year, monthStart, monthEnd (month granularity)
Returns areaHa.

Legal Amazon params:
- type = "legalAmazon"
- code = "1"  (from /api/territories/search/amazonia)
- grouping = "legalAmazon"

This script fetches yearly burned area (ha) for:
1) Period 1: 2023-01-01 to 2026-10-16
   - 2023, 2024, 2025: full years (monthStart=1, monthEnd=12)
   - 2026: Jan through Oct (monthStart=1, monthEnd=10; API is month-granular,
     Oct 2026 data currently returns null, so Jan-Oct == Jan-Sep)
2) Period 2: 2019-01-01 to 2022-12-31 (full years)
"""

from typing import Dict, Tuple
import requests

API_BASE = "https://plataforma.monitorfogo.mapbiomas.org/api"
ENDPOINT = f"{API_BASE}/statistics/area/legalAmazon/1/legalAmazon"

# (year, monthStart, monthEnd) tuples for each period
PERIOD1 = [
    (2023, 1, 12),
    (2024, 1, 12),
    (2025, 1, 12),
    (2026, 1, 10),  # through 2026-10-16 (API month granularity; Oct data null)
]
PERIOD2 = [
    (2019, 1, 12),
    (2020, 1, 12),
    (2021, 1, 12),
    (2022, 1, 12),
]


def fetch_area(year: int, month_start: int, month_end: int) -> float:
    """Fetch areaHa for a given year and month range from the API."""
    params = {"year": year, "monthStart": month_start, "monthEnd": month_end}
    resp = requests.get(ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    area = data.get("areaHa")
    # API returns null for months with no data yet (e.g. Oct 2026)
    return float(area) if area is not None else 0.0


def fetch_period(spec: list) -> Dict[str, float]:
    """Fetch all yearly values for a period, return {year_str: area_ha}."""
    results: Dict[str, float] = {}
    for year, ms, me in spec:
        results[str(year)] = fetch_area(year, ms, me)
    return results


def main() -> None:
    p1_years = fetch_period(PERIOD1)
    p2_years = fetch_period(PERIOD2)

    p1_total = sum(p1_years.values())
    p2_total = sum(p2_years.values())

    print("Legal Amazon burned area (ha) — MapBiomas Fogo (live fetch)")
    print("=" * 60)
    print(f"\nEndpoint: {ENDPOINT}")
    print("Params: type=legalAmazon, code=1, grouping=legalAmazon")
    print("\n--- Period 1: 2023-01-01 to 2026-10-16 ---")
    for year, ha in p1_years.items():
        suffix = " (Jan-Oct, Oct data null)" if year == "2026" else ""
        print(f"{year}: {ha:,.2f} ha{suffix}")
    print("-" * 40)
    print(f"Total: {p1_total:,.2f} ha")
    print("\n--- Period 2: 2019-01-01 to 2022-12-31 ---")
    for year, ha in p2_years.items():
        print(f"{year}: {ha:,.2f} ha")
    print("-" * 40)
    print(f"Total: {p2_total:,.2f} ha")
    print("\nNotes:")
    print("- API is month-granular (year/monthStart/monthEnd), not day-granular")
    print("- 2026-10 data returns null (not yet loaded); Jan-Oct == Jan-Sep")
    print("- Boundary ref: Limites_Amazonia_Legal_2024.geojson")
    print("- See burned_area_legal_amazon.md for details")


if __name__ == "__main__":
    main()
