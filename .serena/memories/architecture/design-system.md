# design/deckmap.py — sistema de design dos vídeos de mapa

Fonte única do visual. **Produto novo importa, não copia.** Spec escrita em `design/DESIGN.md`; exemplo executável em `design/exemplo.py`.

- Exporta tokens (`INK` #F2EFE9, `DIM` #AAAAA5, `ACCENT` #FFB22C, `HOT` #FF6030, `RED_LO` #CD2826, `RED_HI` #FF4830, `PANEL` #07090C, `RULE` #1E2228, `SPLIT`=640), escala tipográfica `TIPO` por formato, `milhar()`, `rotulo_semana()`, `texto()` (letter-spacing), `gradiente_v()`, `ramp()`.
- Camadas de mapa: `trata_satelite()` (dessatura 0.78/0.22, `clip^1.02*0.86`, canais [0.92,1.03,0.96], vinheta 1−0.30·d^1.9 centrada no assunto), `camada_limite()`, `camada_pontos()` (bloom screen + núcleo esbranquiçado, tamanho por intensidade).
- Chrome: `Spec` (dataclass com eyebrow/data/valor/serie/idx/acumulado/escala/fontes), `barras()`, `legenda_escala()`, `ui_portrait()`, `ui_landscape()`, `compor(img, spec, orient)`, `marca_dagua()`.
- **Dois formatos = dois desenhos** (1080×1920 e 1920×1080 têm grades de y próprias; não derive um do outro por escala). `ACCENT` marca só o frame corrente.
- Marca d'água: `logo-no-background.svg` no canto inferior direito, 112 px, margens 40/32, alpha 0.92, sombra difusa; a caixa do selo **tem que estar vazia** (verificar projetando pontos + vértices).
- Contrato de não-regressão: mexeu no `deckmap.py` → re-renderizar e exigir **MAE 0** contra os PNGs aprovados. Na migração do renderer para o módulo: 25 frames × 2 formatos byte-idênticos (md5 portrait `1c0bc2f8…`, landscape `f696f156…`).
- Armadilhas de PIL: `ImageDraw.Draw(img,"RGBA")` **não** faz blend (escreve cru) — scrim/painel em camada transparente separada + `alpha_composite`. Trabalhe em `SUP=2` e reduza com LANCZOS.