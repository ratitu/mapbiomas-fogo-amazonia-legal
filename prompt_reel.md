## Objetivo
Criar um Reel para Instagram divulgando a animação de focos de queimadas na Amazônia Legal.

## Arquivo Fonte
- Caminho: `/home/ratitu/Documents/claude/mapbiomas_Fogo_API/fogo_amazonia_legal_2026_weekly_esri.gif`
- Origem dos dados: BDQueimadas INPE
- Cobertura: Pontos de calor detectados na Amazônia Legal

## Requisitos Técnicos
- Formato de saída: MP4 (H.264)
- Dimensões: 1080x1920px (Vertical 9:16 - Instagram Reel)
- Duração: Manter o ritmo original da animação (1 frame por semana). Não acelerar.
- Converter diretamente do GIF, priorizando nitidez dos focos e do basemap ESRI.
- Otimizado para publicação no Instagram (sem marcas d'água desnecessárias)

## Elementos Visuais
- **Título principal:** "Pontos de queimadas detectados na Amazônia Legal de 01/05/2026 até 26/10/2026"
  - Posicionar na parte superior do vídeo
  - Texto branco com contorno preto ou fundo semitransparente para garantir legibilidade sobre o basemap
  - Fonte bold, tamanho legível para mobile
- **Crédito:** Adicionar "Fonte: BDQueimadas INPE" no canto inferior esquerdo de forma discreta
- **Manter visuais:** Preservar o basemap satélite ESRI, o contorno da Amazônia Legal e a coloração dos focos de calor exatamente como estão na animação

## Legenda para Instagram (PT-BR)
Gerar o seguinte texto para a caption do Reel:

🔥 Focos de queimadas na Amazônia Legal | Maio – Outubro de 2026
Esta animação mostra, semana a semana, os pontos de calor detectados pelo BDQueimadas (INPE) na Amazônia Legal entre 1º de maio e 26 de outubro de 2026, sobre imagem de satélite da ESRI.
É possível observar a evolução dos focos ao longo do período, com maior concentração nos meses mais secos da região.
O monitoramento é fundamental para compreender a dinâmica do fogo e apoiar ações de prevenção e combate.
#Queimadas #AmazôniaLegal #Amazônia #Fogo #IncêndiosFlorestais #Desmatamento #MudançasClimáticas #BDQueimadas #INPE #MapBiomas #MonitoramentoAmbiental #SensoriamentoRemoto #Satélite #Geoespacial #MeioAmbiente #PreservaçãoAmbiental #Conservação #Brasil #AmazôniaEmFoco #Clima

## Arquivos a Gerar
1. `fogo_amazonia_legal_2026_weekly_esri_reel.mp4` - Vídeo final 1920x1080
2. `legenda_reel.txt` - Arquivo contendo apenas a legenda e hashtags acima, pronto para colar diretamente na publicação do Instagram

## Instruções para Execução
1. Converter `fogo_amazonia_legal_2026_weekly_esri.gif` para MP4 1920x1080 mantendo a velocidade original (1 frame por semana).
2. Adicionar o título solicitado no topo com boa legibilidade.
3. Adicionar o crédito "Fonte: BDQueimadas INPE" no rodapé inferior esquerdo.
4. Gerar a legenda e hashtags em português conforme especificado.
5. Salvar ambos os arquivos no mesmo diretório do GIF: `/home/ratitu/Documents/claude/mapbiomas_Fogo_API/`
