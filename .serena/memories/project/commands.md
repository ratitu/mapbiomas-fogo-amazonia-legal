# Comandos e ambientes

Python de trabalho: `/home/ratitu/miniconda3/envs/qgis_env/bin/python` (numpy 2.4.4, Pillow 11.3, cairosvg 2.9, requests 2.33, geopandas 1.0.1, shapely 2.1, matplotlib 3.10.9, contextily 1.6.2, duckdb 1.5.2). `python3` do sistema é 3.12.11 e tem requests/PIL/numpy, mas **use o qgis_env** para qualquer render (cairosvg/geopandas só lá).
`ffmpeg` 5.1.9 disponível. Node/Playwright para o carrossel (`carousel/package.json`, playwright ^1.64.1).

```bash
cd /home/ratitu/Documents/claude/mapbiomas_Fogo_API

# dados / API
python3 fetch_burned_area_legal_amazon.py          # area (ha) por periodo, ao vivo
python3 download_fire_gif.py                       # GIF direto da API

# site (obrigatorio HTTP; file:// quebra fetch de GeoJSON e tiles)
cd website && python3 -m http.server 8765

# validacoes baratas
node --check website/js/app.js
python3 -c "import json;d=json.load(open('website/data/limites_amazonia_legal.geojson'));print('OK',d['type'],len(d['features']))"
$QG/bin/python -m py_compile timelapse/render_timelapse.py design/deckmap.py

# design system + timelapse
$QG/bin/python design/exemplo.py                                  # PNGs de exemplo (sem rede)
$QG/bin/python timelapse/render_timelapse.py --size landscape      # 25 frames 1920x1080
$QG/bin/python timelapse/render_timelapse.py --size portrait --only 24   # 1 frame (debug)
ffmpeg -y -framerate 1 -i timelapse/frames_1920x1080/frame_%03d.png \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 17 -r 1 -movflags +faststart saida.mp4

# carrossel
python3 carousel/build.py && node carousel/export.mjs && node carousel/verify.mjs
```
(qgis env alias: `QG=/home/ratitu/miniconda3/envs/qgis_env/bin`)