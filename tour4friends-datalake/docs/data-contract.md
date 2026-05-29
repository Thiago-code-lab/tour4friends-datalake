# Data Contract Batch e Qualidade de Dados

## Premissas

* Orquestracao batch via **AWS Batch**.
* Publicacao bruta no **S3 Bronze**.
* Normalizacao e validacao via **AWS Glue**.
* Consumo via **Athena** e **Power BI**.

## Data contract por dataset

| Dataset | Owner | Cadencia | Chave | Campos obrigatorios |
| --- | --- | --- | --- | --- |
| `contacts_leads` | Negocio + Dados | Diario | `lead_id` | `nome_completo`, `email`, `source_dataset` |
| `contacts_customers` | Operacao + Dados | Diario | `contact_id` | `nome_completo`, `email`, `source_dataset` |
| `partners` | Comercial | Semanal | `partner_id` | `nome_organizacao`, `categoria`, `source_dataset` |
| `routes_catalog` | Produto | Sob demanda | `route_id` | `route_name`, `segmento`, `status_catalogo` |
| `departures` | Produto + Operacao | Sob demanda | `departure_id` | `route_id`, `departure_name`, `status` |
| `bookings` | Backend | Diario | `booking_id` | `contact_id`, `route_id`, `status` |
| `medical_clearance` | Operacao | Diario | `contact_id` | `contact_id`, `source_dataset` |
| `documents` | Operacao | Diario | `document_id` | `contact_id`, `document_type`, `status` |

## Regras minimas de qualidade

* `email` deve atender regex basica e ser armazenado em lowercase.
* `whatsapp_e164` deve conter prefixo `+`.
* datas devem sair em ISO 8601.
* `record_classification` e obrigatorio em toda carga manual.
* datasets `synthetic_mock_likely` nao entram em gold sem whitelist explicita.
* tabelas derivadas devem referenciar `source_dataset`.

## Criticos para rejeicao de lote

* ausencia de chave primaria;
* schema divergente do contrato;
* coluna obrigatoria nula acima de 5%;
* telefone invalido acima de 20% nas cargas de leads;
* duplicidade de chave acima de 1%.

## Fluxo batch recomendado

1. `AWS Batch` extrai ou converte fontes operacionais.
2. Arquivos chegam em `S3 Bronze`.
3. `AWS Glue` aplica schema, limpeza, deduplicacao e separa camadas.
4. `Athena` consulta apenas datasets validados.
5. `Power BI` consome visoes curated.
