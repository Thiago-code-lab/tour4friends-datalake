# APIs Minimas

## Backend / CRM

### Leads

* `POST /api/leads`
* `GET /api/leads/{lead_id}`
* `PATCH /api/leads/{lead_id}`

### Roteiros

* `GET /api/routes`
* `GET /api/routes/{route_id}`
* `GET /api/routes/{route_id}/departures`

### Grupos / saidas

* `POST /api/departures`
* `GET /api/departures/{departure_id}`
* `PATCH /api/departures/{departure_id}`

### Reservas

* `POST /api/bookings`
* `GET /api/bookings/{booking_id}`
* `PATCH /api/bookings/{booking_id}/status`

### Documentos

* `POST /api/contacts/{contact_id}/documents`
* `GET /api/contacts/{contact_id}/documents`

## Campos minimos por endpoint

* `POST /api/leads`: `nome_completo`, `email`, `whatsapp_e164`, `route_interest`
* `POST /api/bookings`: `contact_id`, `route_id`, `departure_id`, `price_id`
* `POST /api/contacts/{contact_id}/documents`: `document_type`, `storage_key`, `status`
