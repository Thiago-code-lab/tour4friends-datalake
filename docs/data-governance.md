# Governanca, Padronizacao e LGPD

## Padronizacao de colunas

| Origem | Coluna canônica |
| --- | --- |
| `Nome:` | `nome_completo` |
| `1.1 Nome Completo` | `nome_completo` |
| `1.1 Nome e Sobrenome` | `nome_completo` |
| `1.2 E-mail de Contato` | `email` |
| `Email:` | `email` |
| `1.3 WhatsApp` | `whatsapp_e164` |
| `WhatsApp:` | `whatsapp_e164` |
| `1.4 Data de Nascimento` | `data_nascimento` |
| `1.8 Cidade | Estado` | `cidade`, `estado` |
| `1.8 Endereço (Rua/Avenida | Número | CEP | Cidade | Estado)` | `endereco_raw`, `cidade`, `estado` |
| `Qual o Caminho do seu interesse:` | `caminho_interesse_raw` |
| `Como podemos ajudá-lo(a):` | `mensagem_interesse` |

## Regras aplicadas na exportacao canônica

* emails sao normalizados para lowercase;
* telefones sao convertidos para `whatsapp_e164` quando o numero e recuperavel;
* datas em serial Excel sao convertidas para ISO 8601;
* planilhas com multiplos blocos sao separadas em datasets independentes;
* colunas sem cabecalho sao rebatizadas com nomes inferidos e marcadas em documentacao;
* dados derivados recebem `source_truth_role = derived_reference`.

## Mapeamento de enums

Os valores `value-1`, `value-2`, `value-3` e `Option Value` foram extraidos para um arquivo de mapeamento operacional:

* `data/canonical/csv/restricted/lead_option_mapping.csv`

Regra atual:

* `semantic_label` fica vazio enquanto negocio nao homologar a legenda real;
* `mapping_status = pending_business_definition`;
* o `raw_value` permanece preservado para nao inventar semantica.

## LGPD

### Classificacao por sensibilidade

| Campo | Nivel | Tratamento |
| --- | --- | --- |
| Nome, email, telefone, cidade, estado | `confidential_personal` | Permitido no export restrito |
| Data de nascimento | `restricted_personal` | Mantido apenas no export restrito |
| Passaporte, links de documentos | `restricted_document` | Nao exportar valor bruto para analytics |
| Saude e observacoes medicas | `sensitive_personal` | Exportar apenas flags, nunca texto livre |

### Regras aplicadas

* Numeros de passaporte nao sao exportados em texto puro.
* Links de documentos nao sao exportados.
* Texto livre de saude nao e exportado; apenas indicadores de presenca e situacao.
* A camada `restricted` deve ser usada somente por operacao autorizada.

## Duplicidade e versao oficial

* pasta oficial = versao sem sufixo de export;
* arquivo oficial = hash mantido mais antigo/sem sufixo adicional;
* consolidacoes derivadas nao substituem as fontes primarias.
