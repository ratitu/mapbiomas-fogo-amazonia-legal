#!/usr/bin/env python3
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image

# Paths
GEOJSON = Path('bdqueimadas_2026-05-01_2026-10-27.geojson')
BOUNDARY = Path('Limites_Amazonia_Legal_2024.geojson')
OUT_DIR = Path('frames_daily')
OUT_GIF = Path('fogo_amazonia_legal_2026_jun_set_daily.gif')

OUT_DIR.mkdir(exist_ok=True)

# Load boundary
boundary = gpd.read_file(BOUNDARY)
if boundary.crs is None:
    boundary = boundary.set_crs(epsg=4326)
else:
    boundary = boundary.to_crs(epsg=4326)

# Load fire points
with open(GEOJSON) as f:
    data = json.load(f)

points = []
for feat in data['features']:
    p = feat.get('properties') or {}
    s = p.get('DataHora', '')
    try:
        dt = datetime.strptime(s, '%Y/%m/%d %H:%M:%S')
    except:
        continue
    geom = feat.get('geometry')
    if not geom or geom.get('type') != 'Point':
        continue
    coords = geom['coordinates']
    points.append({
        'geometry': Point(coords[0], coords[1]),
        'date': dt.date(),
        'frp': p.get('FRP', 0)
    })

gdf = gpd.GeoDataFrame(points, crs='EPSG:4326')

# Get bounds
bounds = boundary.total_bounds
pad = 2
xmin, ymin, xmax, ymax = bounds[0]-pad, bounds[1]-pad, bounds[2]+pad, bounds[3]+pad

# Generate frames for Jun 1 to Sep 30
start = date(2026, 6, 1)
end = date(2026, 9, 30)
frames = []

for i, d in enumerate([start + timedelta(days=x) for x in range((end-start).days+1)]):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
    fig.patch.set_facecolor('#0e0b08')
    ax.set_facecolor('#1a1612')
    
    # Plot boundary
    boundary.plot(ax=ax, facecolor='#e5a853', alpha=0.03, edgecolor='#f59e0b', linewidth=0.8)
    
    # Plot fires for this day
    day_gdf = gdf[gdf['date'] == d]
    if len(day_gdf) > 0:
        day_gdf.plot(ax=ax, color='#ff3300', markersize=3, alpha=0.8, marker='o')
        day_gdf.plot(ax=ax, color='#ff6600', markersize=8, alpha=0.25, marker='o')
    
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_axis_off()
    
    # Title
    ax.text(0.02, 0.98, f'Focos de calor - {d.strftime("%d/%m/%Y")}', 
            transform=ax.transAxes, color='#f3ecd8', fontsize=14,
            fontweight='bold', va='top')
    
    ax.text(0.02, 0.02, f'BDQueimadas INPE | {len(day_gdf)} focos', 
            transform=ax.transAxes, color='#9a8f7a', fontsize=8, va='bottom')
    
    plt.tight_layout(pad=0)
    fname = OUT_DIR / f'frame_{i:03d}.png'
    fig.savefig(fname, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    frames.append(Image.open(fname))
    if i % 10 == 0:
        print(f'{d}: {len(day_gdf)} focos')

# Save GIF at 1 frame per second
if frames:
    frames[0].save(OUT_GIF, save_all=True, append_images=frames[1:], 
                   duration=1000, loop=0, optimize=False)
    print(f'Saved {OUT_GIF} with {len(frames)} frames')
else:
    print('No frames')
