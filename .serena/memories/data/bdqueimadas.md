# Dados INPE BDQueimadas (focos de calor)

`bdqueimadas_2026-05-01_2026-10-27.geojson` (24 MB na raiz, zip de 2,4 MB): FeatureCollection, **59.709 pontos**, CRS84, período 2026/05/01 18:38 → 2026/10/26 20:12.

Props: `DataHora` ("2026/05/01 18:38:00", formato `%Y/%m/%d %H:%M:%S`), `Satelite`, `Pais`, `Estado`, `Municipio`, `Bioma`, `DiaSemChuva`, `Precipitacao`, `RiscoFogo`, `FRP`, `Latitude`, `Longitude`, `RegiaoEspecial`. Geometria = Point; lat/lon também nas props.

Números-chave já auditados (usados nas legendas):
- 25 semanas completas = 59.405 focos; 73 focos antes de 04/05 e 231 depois de 26/10 ficam fora.
- Pico 19–25/10 = 6.199 (10,4%); mínimo 11–17/05 = 297 (21×); média 2.376; mediana 1.028.
- 12 semanas até 26/07 = 8.519 (14,3%); 13 semanas seguintes = 50.886 (85,7%).
- Estados: PA 20.685 · MT 9.354 · TO 8.874 · AM 8.294 · MA 7.003 · AC 2.127 · RO 1.289 · AP 1.042. Biomas: Amazônia 41.220 (69,4%), Cerrado 18.025 (30,3%), Pantanal 160. Todos `AQUA_M-T`.
- FRP: 79,0% < 50 MW, 19,5% entre 50–300, 1,5% > 300; mediana 20,2; máx 3.824,2; soma 2.585.062.

Semanas do timelapse (frames 1–25): 485, 297, 717, 877, 821, 666, 682, 936, 1003, 501, 520, 1014, 1028, 1474, 3023, 4445, 4053, 3677, 3631, 4290, 4514, 4015, 4838, 5699, 6199.