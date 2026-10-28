#!/usr/bin/env python3
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import contextily as cx
import numpy as np

# Paths
GEOJSON = Path('bdqueimadas_2026-05-01_2026-10-27.geojson')
BOUNDARY = Path('Limites_Amazonia_Legal_2024.geojson')
OUT_DIR = Path('frames_weekly_esri2')
OUT_GIF = Path('fogo_amazonia_legal_2026_weekly_esri.gif')

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
    })

gdf = gpd.GeoDataFrame(points, crs='EPSG:4326')

# Project to Web Mercator for contextily
boundary_web = boundary.to_crs(epsg=3857)
gdf_web = gdf.to_crs(epsg=3857)

# Get bounds
bounds = boundary_web.total_bounds
pad = 500000
xmin, ymin, xmax, ymax = bounds[0]-pad, bounds[1]-pad, bounds[2]+pad, bounds[3]+pad

# Generate weeks
start = date(2026, 5, 1)
end = date(2026, 10, 26)
start_monday = start - timedelta(days=start.weekday())
frames = []
i = 0

week_start = start_monday
while week_start <= end:
    week_end = week_start + timedelta(days=6)
    week_gdf = gdf_web[(gdf['date'] >= week_start) & (gdf['date'] <= min(week_end, end))]
    
    fig, ax = plt.subplots(figsize=(12, 12), dpi=100)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    
    # Add basemap
    try:
        cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery, zoom=5, attribution=False)
    except Exception as e:
        print('err', e)
        try:
            cx.add_basemap(ax, source='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', zoom=5, attribution=False)
        except:
            pass
    
    boundary_web.plot(ax=ax, facecolor='none', edgecolor='#ffcc00', linewidth=1.5, alpha=0.95)
    
    if len(week_gdf) > 0:
        week_gdf.plot(ax=ax, color='#ffff00', markersize=6, alpha=0.95, marker='o')
        week_gdf.plot(ax=ax, color='#ff0000', markersize=12, alpha=0.3, marker='o')
    
    ax.axis('off')
    
    ax.text(0.02, 0.98, f'Semana {week_start.strftime("%d/%m/%Y")} - {min(week_end, end).strftime("%d/%m/%Y")}', 
            transform=ax.transAxes, color='white', fontsize=16, fontweight='bold', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.7, edgecolor='white'))
    ax.text(0.02, 0.02, f'BDQueimadas INPE | {len(week_gdf)} focos | ESRI World Imagery', 
            transform=ax.transAxes, color='white', fontsize=10, va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fname = OUT_DIR / f'frame_{i:03d}.png'
    fig.savefig(fname, facecolor='black', bbox_inches='tight', pad_inches=0, dpi=100)
    plt.close(fig)
    frames.append(Image.open(fname))
    print(f'Semana {week_start}: {len(week_gdf)} focos')
    i += 1
    week_start += timedelta(days=7)
    if week_start > end + timedelta(days=7):
        break

if frames:
    frames[0].save(OUT_GIF, save_all=True, append_images=frames[1:], duration=1000, loop=0, optimize=False)
    print(f'Saved {OUT_GIF} with {len(frames)} frames')
else:
    print('No frames')
