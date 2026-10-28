# Padrão de verificação do projeto (não há testes automatizados)

Não existe pytest/jest/CI de testes. A verificação é **medida**, não inspeção visual — o agente não lê imagens. Precedentes no repo:

- `carousel/verify.mjs`: checa geometria dos slides no Chromium via Playwright (nada estoura 1080×1350, nada cai na zona morta do Instagram, barras verticais na ordem certa com 4 azuis + 4 vermelhos e alturas proporcionais, rótulos dentro do SVG).
- Timelapse/design: MAE pixel a pixel e md5 agregado dos conjuntos de PNGs (MAE 0 = refactor seguro); bbox da marca d'água medido no PNG (margens exatas 40/32); contagem de focos/vértices dentro da caixa do selo (tem que ser 0).
- Website: `node --check website/js/app.js`, `json.load` do GeoJSON simplificado e **Playwright no navegador** (console sem erros, 1 canvas + 4 chips por painel, status de sucesso, tiles Esri/GEE retornando 200). Evidência em `website-verify.png`.
- Vídeo: `ffprobe` (resolução, `r_frame_rate=1/1`, nº de frames) + MAE entre frame decodificado e PNG (~1,4–1,5, só compressão).

Sempre servir site via HTTP: `file://` quebra fetch de GeoJSON e de tiles.