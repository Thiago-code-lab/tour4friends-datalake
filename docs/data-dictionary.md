# Dicionario de Dados

## Objetivo

Este arquivo explica os principais datasets, colunas, classificacoes e convencoes do projeto **Tour4Friends Analytics - Data Lake**. O foco e ajudar qualquer usuario do projeto a entender:

* onde os dados estao;
* qual dataset usar para cada necessidade;
* o significado de cada campo principal;
* quais colunas sao tecnicas, operacionais ou sensiveis.

## Onde estao os dados

Os dados canônicos do projeto ficam em:

* `data/canonical/csv/restricted`

Datasets atuais:

* `source_registry.csv`
* `leads.csv`
* `lead_option_mapping.csv`
* `customers.csv`
* `partners.csv`
* `documents.csv`
* `medical_clearance.csv`
* `routes_catalog_seed.csv`
* `partner_consolidated_reference.csv`

## Convencoes gerais

### Colunas tecnicas

| Campo | Significado |
| --- | --- |
| `source_file` | Arquivo original de onde o registro veio |
| `source_sheet` | Aba original da planilha |
| `source_dataset` | Nome padronizado do dataset na camada canônica |
| `source_block` | Bloco lógico dentro de uma aba que tinha múltiplas estruturas |
| `record_classification` | Classificacao do tipo de dado: real, derivado ou sintético |

### Chaves

| Campo | Regra |
| --- | --- |
| `lead_id` | Hash estável para identificar um lead |
| `contact_id` | Hash estável para identificar uma pessoa/cliente |
| `partner_id` | Hash estável para identificar um parceiro/organizacao |
| `document_id` | Hash estável para identificar o registro documental |
| `route_id` | Identificador semântico do roteiro |

### Valores `raw`

Campos com sufixo `_raw` preservam o valor o mais proximo possivel da fonte original, antes de homologacao total pelo negocio.

### Valores normalizados

| Campo | Regra |
| --- | --- |
| `email` | Lowercase |
| `email_domain` | Dominio extraido do email |
| `whatsapp_e164` | Telefone padronizado com prefixo `+55` quando recuperavel |
| `submitted_at_iso` | Data em formato ISO 8601 |
| `data_nascimento` | Data em formato ISO 8601 |

## Classificacoes do projeto

### `record_classification`

| Valor | Significado |
| --- | --- |
| `real_operational` | Dado operacional real, apto para uso controlado |
| `real_candidate` | Dado aparentemente real, mas ainda sujeito a validacao adicional |
| `derived` | Dado consolidado/derivado de outras fontes |
| `synthetic_mock_likely` | Dado provavelmente sintético, de exemplo ou mock |

### `source_truth_role`

| Valor | Significado |
| --- | --- |
| `primary` | Fonte primária da entidade |
| `secondary` | Fonte complementar |
| `derived_reference` | Consolidado de referencia, nao fonte primaria |

### Campos LGPD

| Campo | Significado |
| --- | --- |
| `lgpd_tier` | Nivel de sensibilidade de uso do registro |
| `health_note_present` | Indica se existe informação de saúde na origem, sem expor o texto |
| `passport_copy_present` | Indica presenca de copia de passaporte, sem expor o link |
| `medical_certificate_present` | Indica presenca de atestado medico |

## Dataset: `source_registry.csv`

### Uso

Catalogo de origem dos datasets do projeto. Deve ser o primeiro arquivo consultado por quem precisa entender de onde cada base veio.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `source_file` | texto | Arquivo de origem |
| `source_sheet` | texto | Aba de origem |
| `entity` | texto | Entidade principal representada (`lead`, `customer`, `partner`) |
| `source_truth_role` | texto | Papel da fonte no modelo de verdade |
| `record_classification` | texto | Classificacao do dataset |
| `notes` | texto | Observacao operacional sobre a fonte |

## Dataset: `leads.csv`

### Uso

Base canônica de leads/interessados que vieram principalmente da aba `Contatos 2026 I`.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `lead_id` | hash/texto | Identificador estável do lead |
| `source_file` | texto | Arquivo de origem |
| `source_sheet` | texto | Aba de origem |
| `source_dataset` | texto | Dataset padronizado |
| `source_block` | texto | Bloco lógico da aba original |
| `record_classification` | texto | Classificacao do dado |
| `lead_legacy_id` | texto/numero | ID legado da planilha/formulario |
| `nome_completo` | texto | Nome do lead |
| `email` | texto | Email normalizado |
| `email_domain` | texto | Dominio do email |
| `whatsapp_raw` | texto | Telefone no formato original |
| `whatsapp_e164` | texto | Telefone normalizado |
| `intencao_viagem_raw` | texto | Valor bruto sobre a intenção de viagem |
| `intencao_viagem_label` | texto | Label semântico homologado; hoje pode estar vazio |
| `forma_viagem_raw` | texto | Valor bruto sobre forma/modalidade |
| `forma_viagem_label` | texto | Label semântico homologado |
| `caminho_interesse_raw` | texto | Valor bruto do roteiro/caminho de interesse |
| `caminho_interesse_label` | texto | Label semântico homologado |
| `mensagem_interesse` | texto | Mensagem livre do lead |
| `consentimento_status` | texto | Status do termo de uso/consentimento |
| `submitted_at_raw` | texto | Data original da fonte |
| `submitted_at_iso` | datetime/texto | Data normalizada |
| `mapping_status_intencao_viagem` | texto | Status do mapeamento de enum da intenção |
| `mapping_status_forma_viagem` | texto | Status do mapeamento de enum da forma |
| `mapping_status_caminho_interesse` | texto | Status do mapeamento de enum do caminho |

## Dataset: `lead_option_mapping.csv`

### Uso

Tabela auxiliar para homologar os valores `value-1`, `value-2`, `Option Value` e combinacoes semelhantes encontradas nos formulários.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `source_dataset` | texto | Dataset onde o valor apareceu |
| `field_name` | texto | Campo que contem o enum bruto |
| `raw_value` | texto | Valor bruto encontrado |
| `semantic_label` | texto | Valor de negocio esperado; hoje pendente |
| `mapping_status` | texto | Status do mapeamento |
| `note` | texto | Observacao de apoio |

## Dataset: `customers.csv`

### Uso

Base canônica de clientes e contatos operacionais, consolidada a partir de `Clientes Antigos` e `Contatos 2026`.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `contact_id` | hash/texto | Identificador estável da pessoa |
| `source_file` | texto | Arquivo de origem |
| `source_sheet` | texto | Aba de origem |
| `source_dataset` | texto | Dataset padronizado |
| `record_classification` | texto | Classificacao do dado |
| `customer_stage` | texto | Estagio do contato, ex.: `cliente_antigo`, `contato_2026` |
| `submitted_at_iso` | datetime/texto | Data de submissao/registro |
| `ano_referencia` | texto/numero | Ano informado na fonte |
| `username` | texto | Usuario legado da fonte, quando existir |
| `nome_completo` | texto | Nome da pessoa |
| `email` | texto | Email normalizado |
| `email_domain` | texto | Dominio do email |
| `whatsapp_raw` | texto | Telefone no formato original |
| `whatsapp_e164` | texto | Telefone normalizado |
| `data_nascimento` | datetime/texto | Data de nascimento |
| `birth_year` | texto/numero | Ano de nascimento |
| `cidade` | texto | Cidade inferida/extraida |
| `estado` | texto | Estado inferido/extraido |
| `endereco_raw` | texto | Endereco bruto da origem |
| `interesse_roteiro_raw` | texto | Texto livre de interesse em roteiro |
| `hospedagem_tipo_raw` | texto | Tipo de hospedagem indicado |
| `hospedagem_categoria_raw` | texto | Categoria de hospedagem |
| `nivel_conhecimento_raw` | texto | Nível de conhecimento do caminho/roteiro |
| `preparado_para_caminho` | texto | Autoavaliacao de preparo |
| `lgpd_tier` | texto | Nivel de sensibilidade do registro |

## Dataset: `partners.csv`

### Uso

Base canônica de parceiros, agências, grupos, clubes, igrejas e outras organizacoes mapeadas para prospeccao ou relacionamento.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `partner_id` | hash/texto | Identificador estável da organizacao |
| `source_file` | texto | Arquivo de origem |
| `source_sheet` | texto | Aba de origem |
| `source_dataset` | texto | Dataset padronizado |
| `record_classification` | texto | Classificacao do dado |
| `nome_organizacao` | texto | Nome da organizacao |
| `categoria` | texto | Categoria do parceiro |
| `perfil` | texto | Perfil/descritivo comercial |
| `email` | texto | Email principal |
| `email_domain` | texto | Dominio do email |
| `telefone_raw` | texto | Telefone bruto |
| `whatsapp_e164` | texto | Telefone normalizado |
| `instagram` | texto | Handle de Instagram |
| `endereco_raw` | texto | Endereco ou localidade bruta |
| `cidade` | texto | Cidade inferida/extraida |
| `estado` | texto | Estado inferido/extraido |
| `contato_modelo` | texto | Tipo/canal de contato modelado |
| `observacoes` | texto | Observacao operacional |

## Dataset: `documents.csv`

### Uso

Camada documental resumida, sem expor dados sensíveis brutos.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `document_id` | hash/texto | Identificador do registro documental |
| `contact_id` | hash/texto | Pessoa vinculada |
| `source_dataset` | texto | Dataset de origem |
| `document_type` | texto | Tipo do documento/resumo documental |
| `passport_informed` | boolean | Indica se passaporte foi informado |
| `passport_copy_present` | boolean | Indica se existe copia de passaporte |
| `medical_certificate_present` | boolean | Indica se existe atestado medico |
| `status` | texto | Status de normalizacao do registro |

## Dataset: `medical_clearance.csv`

### Uso

Resumo operacional de preparo fisico e flags de saude, sem expor o texto medico bruto.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `contact_id` | hash/texto | Pessoa vinculada |
| `source_dataset` | texto | Dataset de origem |
| `health_note_present` | boolean | Indica se a fonte continha observacao de saude |
| `uses_heart_medicine_flag` | texto | Indicacao bruta sobre medicacao cardiaca/pressao |
| `joint_problem_flag` | texto | Indicacao bruta sobre articulacoes/ossos |
| `preventive_exam_regular` | texto | Indicacao sobre exames preventivos |
| `training_status` | texto | Situação de treino/preparo |
| `prepared_for_route` | texto | Autoavaliacao de preparo |
| `medical_certificate_present` | boolean | Indica presenca de atestado |

## Dataset: `routes_catalog_seed.csv`

### Uso

Seed inicial do catálogo mestre de roteiros, criado a partir dos materiais disponiveis no contexto do projeto.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `route_id` | texto | Identificador estável do roteiro |
| `route_name` | texto | Nome amigavel do roteiro |
| `segmento` | texto | Segmento comercial |
| `modalidade` | texto | Modalidade do roteiro |
| `catalog_source` | texto | Pasta/fonte do material |
| `status_catalogo` | texto | Status do seed/catalogo |

## Dataset: `partner_consolidated_reference.csv`

### Uso

Base derivada de referencia, útil para conferência e comparacao com as fontes primarias de parceiros.

### Colunas

| Campo | Tipo aparente | Descricao |
| --- | --- | --- |
| `nome_organizacao` | texto | Nome da organizacao |
| `email` | texto | Email normalizado |
| `whatsapp_e164` | texto | Telefone normalizado |
| `cidade_endereco` | texto | Cidade/endereco como veio na origem |
| `fonte` | texto | Fonte declarada do consolidado |
| `source_dataset` | texto | Nome do dataset derivado |
| `record_classification` | texto | Classificacao `derived` |

## Recomendações de uso

* Para entender origem dos dados, comece por `source_registry.csv`.
* Para leads, use `leads.csv` e consulte `lead_option_mapping.csv` antes de interpretar enums.
* Para clientes, use `customers.csv`.
* Para parceiros, prefira `partners.csv`; use `partner_consolidated_reference.csv` apenas para conferência.
* Para informacoes documentais e de saude, use `documents.csv` e `medical_clearance.csv`, nunca o texto sensível bruto.
* Para roteiros, use `routes_catalog_seed.csv` como seed inicial, nao como catalogo final homologado.

## Observacoes importantes

* O projeto ainda possui campos pendentes de homologacao de negocio, principalmente em enums de interesse e modalidade.
* Alguns dados foram classificados como `synthetic_mock_likely` e nao devem ir para dashboards finais sem validacao.
* Campos sensiveis foram reduzidos a flags e status na camada canônica por requisitos de governanca e LGPD.
