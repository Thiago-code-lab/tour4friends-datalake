# Catalogo Mestre de Roteiros

## Seed inicial a partir dos materiais existentes

Esta estrutura foi criada a partir de nomes de arquivos e pastas disponiveis hoje. Onde a descricao foi inferida somente pelo nome do material, isso deve ser validado pelo time de produto.

| route_id | route_name | segmento | modalidade | fonte |
| --- | --- | --- | --- | --- |
| `caminho_frances_bike` | Caminho Frances de Bicicleta | Bike | Autoguiado / guiado | PDFs e DOCX em `Bike - Cicloviagem` |
| `caminho_portugues_bike` | Caminho Portugues de Bicicleta | Bike | Autoguiado / guiado | PDFs em `Bike - Cicloviagem` |
| `caminho_santiago_pe` | Caminho de Santiago a Pe | Peregrinacao | A pe | PDFs em `Caminho Santiago a Pé` |
| `caminho_portugues_grupo_2026` | Grupo 2026 Caminho Portugues | Peregrinacao | Grupo | PDFs em `Grupo 2026 Caminho Português` |
| `caminho_assis_2026` | Caminho de Assis 2026 | Peregrinacao | Grupo | PDF e midias em `Grupo 2026 Caminho Assis ITALIA` |
| `smarttrip_espanha` | SmartTrip Espanha | Turismo Europa | Pacote | PDF `EUR100.20 SmartTrip Espanha` |
| `smarttrip_4_paises` | SmartTrip 4 Paises | Turismo Europa | Pacote | PDF `EUR100.20 SmartTrip 4Paises` |

## Proximo passo recomendado

* transformar este seed em colecao `routes`;
* extrair `dias`, `etapas`, `km`, `pais`, `preco`, `tipo_de_hospedagem` e `inclusoes`;
* vincular cada `route_id` aos materiais oficiais de roteiro e precificacao.
