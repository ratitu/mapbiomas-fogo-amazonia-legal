![Swagger UI](<Base64-Image-Removed>)Explore

## MapBiomas Fogo API  ```  1.0.0  ```    ``` OAS3 ```

API para consulta de dados do MapBiomas Fogo

[Contact the developer](mailto:contato@geodatin.com)

### [Metadados](https://plataforma.monitorfogo.mapbiomas.org/api/docs/\#/Metadados)

GET[/api/territories/translations](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Metadados/get_api_territories_translations)
Traduções dos tipos de território

GET[/api/land-covers/translations](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Metadados/get_api_land_covers_translations)
Traduções das classes de uso e cobertura

### [Territórios do IBGE](https://plataforma.monitorfogo.mapbiomas.org/api/docs/\#/Territ%C3%B3rios%20do%20IBGE)

GET[/api/territories/search/{searchTerm}](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Territ%C3%B3rios%20do%20IBGE/get_api_territories_search__searchTerm_)
Buscar um território por nome ou código

GET[/api/territories/{type}/{code}/groupings](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Territ%C3%B3rios%20do%20IBGE/get_api_territories__type___code__groupings)
Obter possíveis subdivisões de um território

GET[/api/territories/{type}/{code}/bounds](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Territ%C3%B3rios%20do%20IBGE/get_api_territories__type___code__bounds)
Obter shape dos limites de um território

GET[/api/territories/{type}/{code}/land-covers](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Territ%C3%B3rios%20do%20IBGE/get_api_territories__type___code__land_covers)
Obter classes de uso e cobertura de um território

GET[/api/territories/shape/tiles/{type}/{code}/{grouping}/{z}/{x}/{y}.mvt](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Territ%C3%B3rios%20do%20IBGE/get_api_territories_shape_tiles__type___code___grouping___z___x___y__mvt)
Obter tiles do shape de um território

GET[/api/territories/grouping/tiles/{type}/{code}/{grouping}/{z}/{x}/{y}.mvt](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Territ%C3%B3rios%20do%20IBGE/get_api_territories_grouping_tiles__type___code___grouping___z___x___y__mvt)
Obter tiles das divisões de um território

### [Estatísticas](https://plataforma.monitorfogo.mapbiomas.org/api/docs/\#/Estat%C3%ADsticas)

GET[/api/statistics/years](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Estat%C3%ADsticas/get_api_statistics_years)
Anos disponíveis

GET[/api/statistics/{year}/months](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Estat%C3%ADsticas/get_api_statistics__year__months)
Meses disponíveis

GET[/api/statistics/area/{type}/{code}/{grouping}](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Estat%C3%ADsticas/get_api_statistics_area__type___code___grouping_)
Área queimada em hectares

GET[/api/statistics/land-cover/{type}/{code}/{grouping}](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Estat%C3%ADsticas/get_api_statistics_land_cover__type___code___grouping_)
Área queimada por classe de uso e cobertura do solo

GET[/api/statistics/time-series/{type}/{code}/{grouping}](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Estat%C3%ADsticas/get_api_statistics_time_series__type___code___grouping_)
Série temporal da área queimada

GET[/api/statistics/ranking/{type}/{code}/{grouping}](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Estat%C3%ADsticas/get_api_statistics_ranking__type___code___grouping_)
Ranking de área queimada dos territórios

GET[/api/statistics/ranking/{type}/{code}/{grouping}/raw](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Estat%C3%ADsticas/get_api_statistics_ranking__type___code___grouping__raw)
Ranking bruto de área queimada dos territórios

### [Mapas](https://plataforma.monitorfogo.mapbiomas.org/api/docs/\#/Mapas)

GET[/api/maps/fire/monthly](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Mapas/get_api_maps_fire_monthly)
Raster da área queimada

GET[/api/maps/fire/heatmap/monthly](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Mapas/get_api_maps_fire_heatmap_monthly)
Heatmap da área queimada

GET[/api/maps/fire/monthly/gif](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Mapas/get_api_maps_fire_monthly_gif)
Gif das cicatrizes de fogo

GET[/api/maps/territories/{type}](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Mapas/get_api_maps_territories__type_)
Limites territoriais

GET[/api/maps/land-cover](https://plataforma.monitorfogo.mapbiomas.org/api/docs/#/Mapas/get_api_maps_land_cover)
Raster de uso e cobertura do solo