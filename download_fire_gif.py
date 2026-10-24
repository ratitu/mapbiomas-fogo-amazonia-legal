#!/usr/bin/env python3
"""
Download an animated GIF of fire scars (cicatrizes de fogo) for the Legal Amazon
using the MapBiomas Fogo API (LIVE fetch).

API docs: https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Mapas/get_api_maps_fire_monthly_gif
Endpoint: GET /api/maps/fire/monthly/gif
Returns JSON {"url": "<Google Earth Engine videoThumbnails URL>"} which serves
the GIF directly. Both URLs are short-lived — always fetch fresh.

Query params:
- coordinates (required): JSON string of a closed [lon, lat] ring
- theme       (required): "light" | "dark"
- year        (required): 2019..2026
- monthStart  (required): 1..12
- monthEnd    (required): 1..12
- landCover   (optional): MapBiomas land-cover class id

The Legal Amazon boundary (Limites_Amazonia_Legal_2024.geojson) is a
MultiPolygon with ~330k coordinates — far too large for a URL. This script
extracts the largest polygon's exterior ring and simplifies it (Douglas-
Peucker via shapely, default tolerance 0.2 deg) before sending. The API
rejects URLs larger than ~4 KB (HTTP 414), so on 414 the script automatically
re-simplifies more aggressively.

Usage:
  python3 download_fire_gif.py                     # 2024, Jan-Dec, dark theme
  python3 download_fire_gif.py --year 2023 -o fogo2023.gif
  python3 download_fire_gif.py --year 2025 --month-start 6 --month-end 11
Requires: requests, shapely.
"""

import argparse
import json
import sys
from pathlib import Path

import requests
from shapely.geometry import shape

API_BASE = "https://plataforma.monitorfogo.mapbiomas.org/api"
GIF_ENDPOINT = f"{API_BASE}/maps/fire/monthly/gif"
GEOJSON_PATH = Path(__file__).parent / "Limites_Amazonia_Legal_2024.geojson"


def load_boundary_ring(geojson_path: Path, tolerance: float) -> list:
    """Load the GeoJSON and return a simplified, closed [lon, lat] ring.

    The Legal Amazon is a MultiPolygon (86 parts); the largest part carries
    essentially all of the area, so its exterior is used. Shapely's simplify
    (Douglas-Peucker) reduces the ~326k-point exterior to a few hundred
    points, small enough to fit in a URL query string.
    """
    with open(geojson_path, encoding="utf-8") as f:
        gj = json.load(f)
    geom = shape(gj["features"][0]["geometry"])
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda p: p.area)
    simplified = geom.simplify(tolerance, preserve_topology=True)
    ring = [[round(x, 5), round(y, 5)] for x, y in simplified.exterior.coords]
    # Guarantee the ring is closed (first == last), as the API requires.
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return ring


def request_gif_url(
    ring: list,
    year: int,
    month_start: int,
    month_end: int,
    theme: str = "dark",
    land_cover: int | None = None,
    timeout: int = 60,
) -> str:
    """Ask the API for a GIF URL (Google Earth Engine, short-lived)."""
    params = {
        "coordinates": json.dumps(ring),
        "theme": theme,
        "year": year,
        "monthStart": month_start,
        "monthEnd": month_end,
    }
    if land_cover is not None:
        params["landCover"] = land_cover
    resp = requests.get(GIF_ENDPOINT, params=params, timeout=timeout)
    resp.raise_for_status()
    url = resp.json().get("url")
    if not url:
        raise RuntimeError(f"API response has no 'url': {resp.text[:200]}")
    return url


def request_gif_url_adaptive(
    ring: list,
    year: int,
    month_start: int,
    month_end: int,
    theme: str = "dark",
    land_cover: int | None = None,
    timeout: int = 60,
) -> str:
    """Like request_gif_url, but retries with fewer points on HTTP 414.

    The API rejects request URIs larger than roughly 4 KB (observed:
    131 points OK, 266 points -> 414). If the server responds 414, the ring
    is simplified more aggressively until it fits.
    """
    current = ring
    while True:
        try:
            return request_gif_url(
                current, year, month_start, month_end, theme, land_cover, timeout
            )
        except requests.exceptions.HTTPError as exc:
            resp = exc.response
            if resp is None or resp.status_code != 414 or len(current) <= 5:
                raise
            print(f"  URL too large (HTTP 414); simplifying "
                  f"{len(current)} -> ~{len(current) // 2} points")
            current = simplify_ring(current, tolerance_scale(len(current)))


def tolerance_scale(num_points: int) -> float:
    """Pick a Douglas-Peucker tolerance that roughly halves the point count."""
    return 0.2 * (2 ** max(0, (131 // max(num_points, 1)).bit_length()))


def simplify_ring(ring: list, tolerance: float) -> list:
    """Re-simplify a [lon, lat] ring from an existing (already simplified) ring."""
    from shapely.geometry import LineString

    simplified = LineString(ring).simplify(tolerance, preserve_topology=True)
    result = [[round(x, 5), round(y, 5)] for x, y in simplified.coords]
    if result[0] != result[-1]:
        result.append(result[0])
    return result


def download_gif(url: str, output: Path, timeout: int = 120) -> int:
    """Download the GIF bytes from the GEE URL. Returns size in bytes."""
    with requests.get(url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        total = 0
        with open(output, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                f.write(chunk)
                total += len(chunk)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download MapBiomas Fogo fire-scar GIF for the Legal Amazon."
    )
    parser.add_argument("--year", type=int, default=2024, help="2019-2026 (default: 2024)")
    parser.add_argument("--month-start", type=int, default=1, help="1-12 (default: 1)")
    parser.add_argument("--month-end", type=int, default=12, help="1-12 (default: 12)")
    parser.add_argument("--theme", choices=("light", "dark"), default="dark")
    parser.add_argument("--land-cover", type=int, default=None,
                        help="Optional MapBiomas land-cover class id (e.g. 3 = forest)")
    parser.add_argument("--simplify", type=float, default=0.2,
                        help="Douglas-Peucker tolerance in degrees (default: 0.2; "
                             "the API rejects URLs larger than ~4 KB)")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output file (default: fogo_amazonia_legal_<year>.gif)")
    args = parser.parse_args()

    output = args.output or Path(f"fogo_amazonia_legal_{args.year}.gif")

    print(f"Boundary: {GEOJSON_PATH.name}")
    ring = load_boundary_ring(GEOJSON_PATH, args.simplify)
    print(f"  simplified ring: {len(ring)} points (tolerance {args.simplify} deg)")

    print(f"Requesting GIF: year={args.year}, months {args.month_start}-{args.month_end}, "
          f"theme={args.theme}")
    gif_url = request_gif_url_adaptive(
        ring,
        year=args.year,
        month_start=args.month_start,
        month_end=args.month_end,
        theme=args.theme,
        land_cover=args.land_cover,
    )

    print(f"Downloading {output} ...")
    size = download_gif(gif_url, output)
    print(f"Saved {output} ({size / 1_048_576:.2f} MB)")

    if size == 0:
        sys.exit("ERROR: downloaded file is empty")


if __name__ == "__main__":
    main()
