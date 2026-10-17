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

**Não é um repositório git.**

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
```

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
