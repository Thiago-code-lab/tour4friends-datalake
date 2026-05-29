# Tour4Friends Analytics - Execucao Local

Este guia cobre a etapa atual do projeto com foco em baixo custo: carga inicial dos CSVs no MongoDB, exportacao Bronze em JSON Lines, conversao local para Silver em Parquet, geracao Gold local em Parquet, diagnostico do ambiente e preparacao opcional do bucket S3 para uso futuro.

## 1. Pre-requisitos

- Python 3.10 ou superior
- Docker Desktop ou Docker Engine
- MongoDB rodando localmente em container
- AWS CLI apenas quando for enviar arquivos para S3

Se `python` nao for reconhecido no PowerShell, reinstale o Python marcando a opcao para adicionar ao `PATH` e abra um novo terminal.

## 2. Criar e ativar a virtualenv

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configurar variaveis de ambiente

Crie o arquivo `.env` a partir do exemplo:

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Linux/macOS

```bash
cp .env.example .env
```

Valores iniciais do `.env`:

```dotenv
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=tour4friends
AWS_REGION=us-east-1
S3_BUCKET=tour4friends-lake-dev
```

## 4. Subir MongoDB local via Docker

### Windows PowerShell / Linux / macOS

```bash
docker run -d --name tour4friends-mongo -p 27017:27017 mongo:7
```

Para parar o container:

```bash
docker stop tour4friends-mongo
```

Para iniciar novamente depois:

```bash
docker start tour4friends-mongo
```

## 5. Diagnostico

O script abaixo valida:

- Python disponivel e versao
- dependencias do `requirements.txt`
- arquivo `.env`
- pasta `data/`
- quantidade de CSVs
- Docker acessivel
- MongoDB respondendo com `ping`

```powershell
python scripts/check_environment.py
```

## 6. Carregar os CSVs no MongoDB

O script le todos os arquivos `.csv` em `data/`, converte o nome do arquivo em nome de collection e insere os registros no banco configurado.

### Windows PowerShell

```powershell
$env:RESET_COLLECTIONS="true"
python scripts/load_csv_to_mongodb.py
Remove-Item Env:RESET_COLLECTIONS -ErrorAction SilentlyContinue
```

## 7. Exportar Bronze local em JSON Lines

O script exporta todas as collections do MongoDB para `tmp/bronze/<collection>/ano=YYYY/mes=MM/dia=DD/part-00001.jsonl`.

```powershell
python scripts/export_mongodb_to_s3_bronze.py
```

## 8. Converter Bronze para Silver local em Parquet

O script le todos os arquivos `.jsonl` em `tmp/bronze/`, converte para Parquet em `tmp/silver/` e preserva o mesmo particionamento por collection, ano, mes e dia.

```powershell
python scripts/bronze_to_silver_local.py
```

## 9. Converter Silver para Gold local em Parquet

O script le os Parquet de `tmp/silver/` e gera tabelas analiticas em `tmp/gold/`:

- `gold_receita_por_mes`
- `gold_reservas_por_destino`
- `gold_ticket_medio_por_cliente`
- `gold_taxa_cancelamento`
- `gold_satisfacao_por_destino`, quando houver dados suficientes

```powershell
python scripts/silver_to_gold_local.py
```

Observacoes:

- Usa `pandas`.
- Se uma tabela Gold nao puder ser gerada por falta de colunas, o script emite aviso claro e segue com as demais.
- A collection `reservas_viagens_expandido` e obrigatoria para a Gold local.

## 10. Validar saidas do pipeline

O script abaixo valida:

- collections no MongoDB
- arquivos JSONL em `tmp/bronze`
- arquivos Parquet em `tmp/silver`
- arquivos Parquet em `tmp/gold`
- contagem de linhas por camada
- presenca das tabelas Gold obrigatorias

```powershell
python scripts/validate_pipeline_outputs.py
```

## 11. Preparar estrutura do bucket S3

Esse passo e opcional e so faz sentido depois de configurar credenciais AWS CLI ou variaveis padrao da AWS.

```powershell
python scripts/create_s3_structure.py
```

## 12. Configurar AWS CLI

```powershell
aws configure
```

## 13. Enviar Bronze local para S3

```powershell
$env:UPLOAD_TO_S3="true"
python scripts/export_mongodb_to_s3_bronze.py
Remove-Item Env:UPLOAD_TO_S3 -ErrorAction SilentlyContinue
```

## 14. Estrutura esperada no projeto

```text
tmp/
  bronze/
    reservas_viagens_expandido/
      ano=2026/
        mes=05/
          dia=03/
            part-00001.jsonl
  silver/
    reservas_viagens_expandido/
      ano=2026/
        mes=05/
          dia=03/
            part-00001.parquet
  gold/
    gold_receita_por_mes/
      part-00001.parquet
    gold_reservas_por_destino/
      part-00001.parquet
```

## 15. Decisoes desta etapa

- Mantido o pipeline local e simples para caber no AWS Free Tier.
- O foco de armazenamento continua em S3, sem processamento gerenciado nesta fase.
- Nenhum Glue, Athena, Batch, Lambda, EC2, ECS, EKS, MSK ou RDS foi introduzido nesta etapa.

## 16. Teste completo do zero

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
docker run -d --name tour4friends-mongo -p 27017:27017 mongo:7
python scripts/check_environment.py
$env:RESET_COLLECTIONS="true"
python scripts/load_csv_to_mongodb.py
Remove-Item Env:RESET_COLLECTIONS -ErrorAction SilentlyContinue
python scripts/export_mongodb_to_s3_bronze.py
python scripts/bronze_to_silver_local.py
python scripts/silver_to_gold_local.py
python scripts/validate_pipeline_outputs.py
python scripts/create_s3_structure.py
$env:UPLOAD_TO_S3="true"
python scripts/export_mongodb_to_s3_bronze.py
Remove-Item Env:UPLOAD_TO_S3 -ErrorAction SilentlyContinue
```
