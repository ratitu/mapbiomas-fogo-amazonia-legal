# Task: Heatmap of Burned Area in Legal Amazon

Using the MapBiomas Fogo API, visualize the fire heatmap for the months of June, July, August, and September 2026 within the boundaries of the Legal Amazon in the current QGIS session.

## 1. API Information
- **Base URL:** `https://plataforma.monitorfogo.mapbiomas.org/api`
- **Heatmap Endpoint:** `GET /maps/fire-heatmap/monthly`
- **Documentation:** [MapBiomas Fogo API Docs](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Mapas/get_api_maps_fire_heatmap_monthly)

## 2. Requirements
- **Target Months:** 06/2026, 07/2026, 08/2026, and 09/2026.
- **Geospatial Boundary:** Use the limits of the file `Limites_Amazonia_Legal_2024.geojson`. If it is already open in the QGIS session, use the active layer as the boundary reference. Otherwise, load it from the root directory.
- **Action:** Load the resulting heatmaps directly into the current QGIS session as individual layers.
- **Styling:** Use a suitable heatmap color ramp (intensity of fire) as suggested by the API or standard fire monitoring practices.

## 3. Reference Data
- The project context is in `/home/ratitu/Documents/claude/mapbiomas_Fogo_API`.
- Consult `fetch_burned_area_legal_amazon.py` for general API interaction patterns.
- Consult `website/js/app.js` for examples of how to handle Google Earth Engine (GEE) tile URLs returned by the MapBiomas API.

## 4. Execution Guidance
- Ensure the QGIS Python environment has `requests` installed (it should be, given `fetch_burned_area_legal_amazon.py` runs).
- Map IDs from the API are temporary; do not cache them.
- If the API returns a Tile URL, add it to QGIS as an XYZ Layer or WMS/WMTS layer depending on the format.
