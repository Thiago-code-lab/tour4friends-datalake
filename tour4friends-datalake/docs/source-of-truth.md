# Fonte de Verdade e Separacao Real/Mock

## Fonte de verdade por entidade

| Entidade | Fontes atuais | Fonte de verdade alvo | Status |
| --- | --- | --- | --- |
| `lead` | `Cópia de T4F_mail_marketing.xlsx` -> `Contatos 2026 I` (blocos 1, 2 e 3) | `MongoDB.leads` + export batch padronizado em `contacts/leads` | Definido |
| `cliente` | `Clientes Antigos`, `Contatos 2026` | `MongoDB.contacts` com `customer_stage` | Definido |
| `parceiro` | `100 agencias`, `100 Grupos Catolicos +Classe tr`, `100 bike class`, `Bike outros estados` | `MongoDB.partners` | Definido |
| `roteiro` | PDFs e DOCX em `Tour4friends-context` | `MongoDB.routes` + catalogo mestre curado | Definido com seed manual |
| `saida_grupo` | `Grupo 2026 Caminho Português`, `Grupo 2026 Caminho Assis ITALIA` e materiais de roteiro | `MongoDB.departures` | Definido |
| `preco` | PDFs `Valores*.pdf` e planilhas futuras | `MongoDB.route_prices` | Definido |
| `reserva` | Ainda nao existe amostra estruturada na pasta | `MongoDB.bookings` | Definido, pendente de dados |
| `medical_clearance` | Formularios `Clientes Antigos` e `Contatos 2026` | `MongoDB.medical_clearance` | Definido |
| `documents` | Formularios com passaporte, atestado e links | `MongoDB.documents` | Definido |

## Classificacao dos datasets atuais

| Dataset | Classificacao | Uso recomendado |
| --- | --- | --- |
| `100 agencias` | `real_candidate` | Parceiros reais, sujeito a validacao pontual |
| `Clientes Antigos` | `real_operational` | Base operacional historica |
| `Contatos 2026` | `real_operational` | Intake operacional de clientes |
| `Contatos 2026 I` | `real_operational` | Leads e contatos de interesse |
| `Bike outros estados` | `real_candidate` | Prospecção, com schema inferido na exportacao |
| `100 Grupos Catolicos +Classe tr` | `real_candidate` | Prospecção, com revisao comercial |
| `100 bike class` | `real_candidate` | Prospecção, com revisao comercial |
| `Contatos_Existentes_SP_11` | `derived` | Consolidado derivado, nao usar como fonte primaria |
| `Franciscanos` | `synthetic_mock_likely` | Mock / prospecção simulada |
| `Caminhos e Associações` | `synthetic_mock_likely` | Mock / prospecção simulada |
| `Novos_100_Parceiros_SP` | `synthetic_mock_likely` | Mock / prospecção simulada |
| `Devotos_Carlo_Acutis` | `synthetic_mock_likely` | Mock / prospecção simulada |

## Decisoes aplicadas

* Os CSVs canônicos exportados carregam a coluna `record_classification`.
* `Contatos_Existentes_SP_11` foi mantido apenas como consolidado de referencia; o export operacional de parceiros usa as abas primarias.
* `Contatos 2026 I` foi quebrado em tres blocos lógicos na exportacao canônica.
* `Bike outros estados` recebeu cabecalhos inferidos apenas na camada canônica, sem alterar o XLSX original.

## Duplicidades

As duplicidades exatas foram tratadas com a regra:

* manter a pasta/arquivo sem sufixo de export quando o hash e identico;
* remover pastas vazias de export;
* remover copia identica com sufixo `(1)` apenas quando o hash for exatamente igual.
