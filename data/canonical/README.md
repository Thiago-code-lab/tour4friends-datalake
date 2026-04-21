# Export Canonico

## Objetivo

Os arquivos em `data/canonical/csv/restricted` representam a camada canônica restrita gerada a partir das planilhas de contexto.

## Caracteristicas

* schema padronizado;
* classificacao `real_operational`, `real_candidate`, `derived` e `synthetic_mock_likely`;
* correcao de abas sem cabecalho e abas com multiplos blocos;
* remocao de campos sensiveis brutos de saude e documentos;
* pronto para conversao posterior em Parquet na etapa batch do Glue.

## Geracao

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\export_canonical_data.ps1
```
