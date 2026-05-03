# Tour4Friends Analytics - AWS Free Tier

Este guia cobre apenas o uso minimo de AWS para esta etapa: Amazon S3 + AWS CLI.

## 1. Objetivo

Usar S3 como armazenamento do Data Lake sem subir servicos gerenciados de processamento. Nesta etapa, nao usar Glue, Athena, Batch, Lambda, EC2, ECS, EKS, MSK ou RDS.

## 2. Criar o bucket S3

Escolha um nome globalmente unico, por exemplo:

```text
tour4friends-lake-dev-seu-nome
```

### us-east-1

```powershell
aws s3api create-bucket --bucket tour4friends-lake-dev-seu-nome --region us-east-1
```

## 3. Configurar credenciais locais

```powershell
aws configure
```

Informe:

- AWS Access Key ID
- AWS Secret Access Key
- Default region name: `us-east-1`
- Default output format: `json`

## 4. Atualizar o arquivo .env

```dotenv
S3_BUCKET=tour4friends-lake-dev-seu-nome
```

## 5. Criar os prefixes do Data Lake

```powershell
python scripts/create_s3_structure.py
```

Os prefixes criados serao:

- `bronze/`
- `silver/`
- `gold/`
- `logs/`
- `checkpoints/`

## 6. Enviar Bronze para S3

```powershell
$env:UPLOAD_TO_S3="true"
python scripts/export_mongodb_to_s3_bronze.py
Remove-Item Env:UPLOAD_TO_S3 -ErrorAction SilentlyContinue
```

## 7. Enviar Silver para S3

```powershell
aws s3 cp .\tmp\silver\ s3://tour4friends-lake-dev-seu-nome/silver/ --recursive
```

## 8. Enviar Gold para S3

```powershell
aws s3 cp .\tmp\gold\ s3://tour4friends-lake-dev-seu-nome/gold/ --recursive
```

## 9. Boas praticas para evitar custo

- Use apenas S3 nesta fase.
- Nao habilite servicos de processamento gerenciado.
- Nao crie buckets em varias regioes sem necessidade.
- Evite armazenar arquivos duplicados desnecessarios.
- Revise o volume enviado para S3 antes de rodar uploads recursivos.
- Mantenha datasets pequenos durante a fase academica e local.
- Apague saidas locais antigas quando nao forem mais necessarias.

## 10. Comandos minimos no Windows PowerShell

```powershell
aws configure
aws s3api create-bucket --bucket tour4friends-lake-dev-seu-nome --region us-east-1
python scripts/create_s3_structure.py
$env:UPLOAD_TO_S3="true"
python scripts/export_mongodb_to_s3_bronze.py
Remove-Item Env:UPLOAD_TO_S3 -ErrorAction SilentlyContinue
aws s3 cp .\tmp\silver\ s3://tour4friends-lake-dev-seu-nome/silver/ --recursive
aws s3 cp .\tmp\gold\ s3://tour4friends-lake-dev-seu-nome/gold/ --recursive
```
