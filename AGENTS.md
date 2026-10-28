# AGENTS.md

Guia para agentes de IA que trabalham neste repositório. Este projeto é pequeno e
estático: um script Python de consulta à API e um website MapLibre GL JS sem build.

## Visão geral

**`mapbiomas_Fogo_API`** compara a área queimada na **Amazônia Legal** em dois
períodos (2023–2026 e 2019–2022) usando dados do **MapBiomas Fogo**. Há dois
artefatos independentes:

1. `fetch_burned_area_legal_amazon.py` — script Python que consulta a API e
   imprime a área queimada (ha) por ano e o total por período.
2. `website/` — site estático (HTML/CSS/JS puro) com dois mapas MapLibre GL JS
   sincronizados, sem bundler, sem `package.json`, sem dependências instaláveis.

Repositório **git**, com remoto `github.com:ratitu/mapbiomas-fogo-amazonia-legal`
(branch `main`) e deploy no **GitHub Pages** pelo workflow
`.github/workflows/deploy-pages.yml`, que publica `website-globe/` — o `website/`
não é publicado, roda só local.
Boa parte do trabalho recente — `timelapse/`, `design/`, GIFs/MP4s, legendas e os
GeoJSON brutos — está **untracked**. Nunca commitar/pushar sem pedido explícito.

## Mapa do repositório

| Caminho | O que é |
|---------|---------|
| `fetch_burned_area_legal_amazon.py` | Script de consulta à API (`requests`). Fonte dos números. |
| `burned_area_legal_amazon.md` | Análise/tabelas dos dois períodos (documentação de dados). |
| `Limites_Amazonia_Legal_2024.geojson` | Contorno original da Amazônia Legal (9,5 MB, ~330k coords). **Recurso pesado — não carregar por engano.** |
| `website/index.html` | Página pt-BR; layout de dois painéis `.map-pane[data-period=period1\|period2]`. |
| `website/css/style.css` | Tema escuro, grid 1fr 1fr responsivo, overlays (cabeçalho/legenda/status). |
| `website/js/app.js` | Toda a lógica dos mapas (~331 linhas). **Arquivo central.** |
| `website/data/limites_amazonia_legal.geojson` | Contorno simplificado (197 KB) usado pelo site. |
| `website-verify.png` | Screenshot de verificação (evidência, não fonte). |
| `design/deckmap.py` | **Design system** dos vídeos de mapa: tokens, escala tipográfica, geometria dos dois formatos, camadas, chrome e marca d'água. |
| `design/DESIGN.md` | Especificação do design system (tokens, grades, componentes, regras, verificação). |
| `design/exemplo.py` | Produto de exemplo que reaproveita o design com dados sintéticos (sem rede). |
| `timelapse/render_timelapse.py` | Produto: timelapse semanal dos focos (1 frame = 1 semana), `--size portrait\|landscape`. Consome `design/deckmap.py`. |
| `timelapse/frames/`, `timelapse/frames_1920x1080/` | 25 PNGs por formato (~117 MB). Recurso pesado. |
| `timelapse/focos_amazonia_legal_2026_*.mp4` | Entregáveis finais dos dois formatos. |
| `session-ses_eb7f.md`, `.omo/`, `.playwright-mcp/` | Artefatos de sessão/ferramentas. Não editar. |

## Comandos

Trabalhe a partir de `/home/ratitu/Documents/claude/mapbiomas_Fogo_API`.

```bash
# Rodar o website (obrigatório servir via HTTP; file:// não funciona)
cd website && python3 -m http.server 8765
# abrir http://localhost:8765/index.html

# Validar a sintaxe do JS (não há build/typecheck)
node --check website/js/app.js

# Validar o GeoJSON simplificado
python3 -c "import json;d=json.load(open('website/data/limites_amazonia_legal.geojson'));print('OK', d['type'], len(d['features']))"

# Reproduzir os números (requer requests)
python3 fetch_burned_area_legal_amazon.py

# Re-simplificar o contorno (se precisar regerar o arquivo do site)
/home/ratitu/miniconda3/envs/qgis_env/bin/ogr2ogr -simplify 0.005 \
  /tmp/limites_simplified2.geojson Limites_Amazonia_Legal_2024.geojson

# Design system: produto de exemplo (dados sintéticos, sem rede)
/home/ratitu/miniconda3/envs/qgis_env/bin/python design/exemplo.py

# Timelapse (requer cairosvg + numpy + pillow + requests no env qgis_env)
/home/ratitu/miniconda3/envs/qgis_env/bin/python timelapse/render_timelapse.py --size landscape
/home/ratitu/miniconda3/envs/qgis_env/bin/python timelapse/render_timelapse.py --size portrait --only 24
```

## Design system (vídeos de mapa)

Vídeo/imagem de mapa novo **reaproveita** [design/deckmap.py](design/deckmap.py);
não copie geometria nem cor para dentro do script do produto.

- **Especificação completa:** [design/DESIGN.md](design/DESIGN.md) (tokens,
  escala tipográfica, grades de y por formato, componentes, regras).
- **O que fica no `deckmap.py`:** paleta, tipografia, `trata_satelite`,
  `camada_limite`, `camada_pontos`, `compor` (chrome dos dois formatos),
  `marca_dagua`, `Spec`.
- **O que fica no produto:** dados, projeção/enquadramento, textos do `Spec`,
  sequência de frames + ffmpeg.
- **Dois formatos = dois desenhos.** Vertical 1080×1920 e horizontal 1920×1080
  têm grades próprias; não derive um do outro por escala.
- **Uma cor de acento só** (`ACCENT`) — ela marca apenas a semana/quadro corrente.
- **Marca d'água:** canto inferior direito, 112 px, margens 40/32, opacidade
  0,92. A caixa do selo precisa estar **vazia** — verifique projetando os pontos
  e os vértices do território antes de fixar a posição.
- **Contrato de não-regressão:** se `deckmap.py` mudar, re-renderize e compare
  pixel a pixel com os PNGs aprovados; MAE tem que ser 0. Foi assim que o
  renderer foi migrado para o módulo (25 frames × 2 formatos, MAE 0,0).

## Convenções de código

- **Idioma da UI:** português (pt-BR). Mantenha textos de interface em pt-BR.
- **Idioma do código:** identificadores e comentários em inglês, salvo os já
  existentes em pt-BR — siga o estilo do trecho que está editando.
- **Formatação:** 2 espaços de indentação; aspas duplas no JS; ponto e vírgula.
- **JS:** JavaScript vanilla, ES2017+ (usa `async/await`, `Promise.allSettled`).
  Sem framework, sem módulos ES (não há `import`/`export`; o script roda global).
- **CSS:** variáveis de tema em `:root` (`--bg`, `--panel`, `--line`, `--text`,
  `--accent`, `--accent-2`, `--p1`, `--p2`); classes no padrão BEM
  (`block__element--modifier`), ex.: `.map-pane__head`, `.map-pane__badge--p1`.
- **Dados:** números de hectares ficam **hardcoded** em `PERIODS` (em `app.js`),
  espelhando o resultado de `fetch_burned_area_legal_amazon.py`. Ao atualizar os
  dados, atualize **os dois lados** e prefira reexecutar o script.

## `app.js` — pontos-chave

- Constantes no topo: `API_BASE`, `TERRITORY`, `BOUNDARY_URL`, `AMZ_BOUNDS`,
  `PERIODS`, `FIRE`.
- `buildStyle()` monta o style v8: fonte raster `esri-sat`, fonte `boundary`
  (GeoJSON), camadas `esri-sat` → `boundary-fill` → `boundary-line`.
- `fetchYearTileUrl(year, monthEnd)` → **uma chamada HTTP por ano**; devolve a URL
  de tiles do GEE.
- `createPane(period, shared)` cria um `maplibregl.Map`, controles e a legenda;
  no evento `load` faz `fitBounds` e chama `loadPeriod`.
- `loadPeriod(...)` busca todos os anos em paralelo (`Promise.allSettled`) e
  adiciona um `raster` por ano, **inserido antes de `boundary-fill`**.
- `setupSync(shared)` sincroniza os dois mapas via eventos `move` com guarda
  `syncing`.
- `boot()` inicializa tudo e liga os controles do cabeçalho.

## Gotchas (importante)

1. **Map IDs do GEE são de curta duração.** Nunca cacheie/persista a URL de tiles
   retornada pela API; sempre busque ao vivo no carregamento.
2. **Ordem das camadas.** Os rasters de fogo são adicionados com
   `map.addLayer(layer, "boundary-fill")` para ficarem **abaixo** do contorno.
   Trocar o `beforeId` muda a hierarquia visual.
3. **Escopo de variáveis no `forEach`.** Em `loadPeriod`, `srcId` e `layerId`
   **devem** ser declarados no topo do callback (antes do `if (r.status ===
   "fulfilled")`). Já houve um bug de `ReferenceError` por declará-los com `const`
   dentro do bloco e usá-los no chip de ano fora dele. Não reintroduza.
4. **Não usar o GeoJSON de 9,5 MB no site.** O site usa a versão simplificada em
   `website/data/`. O arquivo da raiz é a fonte para re-simplificar.
5. **Sempre servir via HTTP.** `file://` quebra o fetch do GeoJSON e das tiles.
6. **Uma chamada por ano.** A API é mensal e cobre um único ano por chamada;
   agregação de vários anos = múltiplas chamadas.

## Verificação (padrão do projeto)

Não há testes automatizados. O padrão de verificação usado foi:

1. `node --check website/js/app.js` (sintaxe).
2. `json.load` no GeoJSON simplificado.
3. Servir via `python3 -m http.server` e abrir no navegador (Playwright MCP):
   - console **sem erros**;
   - **cada painel** com 1 `<canvas>` e **4 chips de ano**;
   - status de sucesso em ambos os painéis;
   - requisições de rede: tiles Esri e tiles do GEE retornando **200**.

Evidência visual fica em `website-verify.png`.
