# Tarefa: carrossel Instagram — Área Queimada na Amazônia Legal (MapBiomas Fogo)

## Objetivo
Entregar um **carrossel de 6 slides (PNG 1080x1350)** com os dados de área queimada
da Amazônia Legal coletados por `fetch_burned_area_legal_amazon.py`, pronto para
publicação no Instagram.

## Entradas (NÃO buscar dados de novo — usar estes)
Fonte: `fetch_burned_area_legal_amazon.py` + `burned_area_legal_amazon.md`.
Endpoint: MapBiomas Fogo `/api/statistics/area/legalAmazon/1/legalAmazon`.

| Ano  | Grupo     | Área queimada (ha)      |
| ---- | --------- | ----------------------- |
| 2019 | BOLSONARO | 13.403.151,45           |
| 2020 | BOLSONARO | 14.280.715,79           |
| 2021 | BOLSONARO | 9.102.369,25            |
| 2022 | BOLSONARO | 13.388.587,40           |
| 2023 | PT        | 14.110.379,24           |
| 2024 | PT        | 25.583.085,87           |
| 2025 | PT        | 7.696.586,54            |
| 2026 | PT        | 5.782.625,57 (Jan–Out)* |

Totais: **BOLSONARO (2019–2022) = 50.174.823,89 ha** · **PT (2023–2026) = 53.172.677,22 ha**
\*2026 parcial — a API é granular por mês e outubro/2026 retorna `null`.

## Estrutura dos slides
1. **Capa** — título, subtítulo, selo "Fonte: MapBiomas Fogo", período coberto.
2. **Slide principal** — gráfico de barras **verticais**, 8 barras (uma por ano),
   em ordem cronológica 2019→2026. Barras 2019–2022 **AZUL**, barras 2023–2026 **VERMELHO**.
   Legenda com dois rótulos: **BOLSONARO** (azul) e **PT** (vermelho).
   Rótulo de valor em cima de cada barra (ex.: `13,4 mi ha`). Eixo Y em milhões de ha.
3. **Totais** — dois blocos grandes lado a lado: total de cada grupo, com variação
   percentual (`PT` +6,0% vs `BOLSONARO`) calculada a partir dos totais acima.
4. **Picos mensais** — gráfico de barras dos **meses com mais queimadas** (top 6),
   derivado da API. Sem dado novo na tabela → **CONSULTE A API**: itere
   `monthStart=m, monthEnd=m` para cada ano 2019–2026 e ranqueie os 6 maiores valores.
   Rótulo no formato `Agosto/2019`.
5. **Locais** — ranking dos **6 estados/regiões com mais queimadas** do período PT   (2023–2026). Obter via API: itere os códigos de
   `/api/territories/search/amazonia` com `grouping` por unidade e
   `/api/statistics/area/{type}/{code}/{grouping}`.
   **Se a API não permitir o recorte por local, NÃO invente números:** produza o slide
   com os dados que conseguir + um bloco "Dados por local: indisponíveis na API pública
   (granularidade territorial). Fonte: IBGE/Monitor Fogo" e registre a limitação.
6. **Encerramento / CTA** — síntese dos achados em 3 frases curtas + handle, crédito
   MapBiomas Fogo + aviso "2026 parcial".

## Requisitos técnicos
- **Entregável**: HTML único `carousel/index.html` com os 6 slides em frames
  fixos 1080x1350 px, + script `carousel/export.mjs` (Playwright) que gera
  `carousel/out/slide-01.png` … `slide-06.png` em 1080x1350, PNG, sem bordas.
- **Sem framework, sem CDN de gráfico**: gráficos desenhados em **SVG inline**
  (barras verticais com `<rect>`, sem biblioteca externa).
- **Idioma da UI e de todo o texto: pt-BR.**
- Números em formato brasileiro (`pt-BR`, separador de milhar `.`, decimal `,`),
  formatados a partir dos valores brutos — nunca hardcodar string formatada.
- **Paleta:** fundo escuro (`#0d1117`-ish), barras `#2563eb` (azul) e `#dc2626`
  (vermelho); texto claro. Contraste AA.
- **Timeline**: barra inferior com 2019–2026, bloco do governo atual destacado.
- Título/legenda de cada slide dentro da área segura do Instagram
  (margem mínima 60px; nada nos 250px inferiores).

## Critérios de aceite
- `node carousel/export.mjs` roda sem erro e gera **6 PNGs 1080x1350**.
- As 8 barras do slide 2 estão presentes, na ordem 2019→2026, com as cores corretas
  (4 azuis, 4 vermelhos) — verificável por `grep` de `fill="#2563eb"` no HTML.
- Os dois totais do slide 3 batem exatamente com 50.174.823,89 e 53.172.677,22.
- Slide 4 e 5 têm fonte de dados citada; nenhum número inventado (ver gotcha 2).
- Aviso "2026 parcial (Jan–Out)" presente onde o dado aparece.

## Gotchas
1. **2026 é parcial** — sempre marcar; comparar 4 anos completos × 3 completos + 1 parcial.
2. **Nunca inventar dado mensal/local.** Se a API não entregar, degradar o slide
   com rótulo explícito de indisponibilidade.
3. Map IDs / tile URLs do GEE são efêmeros — não cachear.
4. Servir via `python3 -m http.server` (nunca `file://`) para o preview/export.