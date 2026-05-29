# Modelo de Dados e Colecoes

## Colecoes principais

### `contacts`

* `contact_id`
* `contact_type` (`lead`, `customer`, `partner_contact`)
* `nome_completo`
* `email`
* `whatsapp_e164`
* `cidade`
* `estado`
* `source_dataset`
* `record_classification`
* `created_at`

### `partners`

* `partner_id`
* `nome_organizacao`
* `categoria`
* `perfil`
* `email`
* `telefone`
* `instagram`
* `endereco_raw`
* `cidade`
* `estado`
* `source_dataset`

### `routes`

* `route_id`
* `route_name`
* `segmento`
* `modalidade`
* `pais`
* `status_catalogo`
* `catalog_source`

### `departures`

* `departure_id`
* `route_id`
* `departure_name`
* `ano_referencia`
* `pais`
* `status`
* `source_material`

### `bookings`

* `booking_id`
* `contact_id`
* `route_id`
* `departure_id`
* `status`
* `price_id`
* `created_at`

### `medical_clearance`

* `contact_id`
* `health_note_present`
* `preventive_exam_regular`
* `prepared_for_route`
* `medical_certificate_present`
* `source_dataset`

### `documents`

* `document_id`
* `contact_id`
* `document_type`
* `status`
* `source_dataset`
* `document_source`

## Relacoes

* `contacts -> bookings` por `contact_id`
* `routes -> departures` por `route_id`
* `departures -> bookings` por `departure_id`
* `contacts -> medical_clearance` por `contact_id`
* `contacts -> documents` por `contact_id`
