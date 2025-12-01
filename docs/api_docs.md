## API Documentation (Endpoint Focus)

All examples assume:

- Base URL: `http://localhost:8000`
- Basic Auth header present: `Authorization: Basic <base64(admin:secret)>`
- Header for JSON bodies: `Content-Type: application/json`

---

### 1) List Transactions

- Endpoint & Method: `GET /transactions`

- Request Example:

```bash
curl -H "Authorization: Basic $BASIC" http://localhost:8000/transactions
```

- Response Example (200 OK):

```json
[
  {
    "id": 1,
    "sms_address": "MTN",
    "sms_date": "2025-09-19T12:00:00+00:00",
    "sms_type": "SMS",
    "sms_body": "You have received 1,000 RWF",
    "transaction_type": "money_in",
    "amount": 1000,
    "currency": "RWF",
    "sender": null,
    "receiver": null,
    "balance": null,
    "fee": 0,
    "transaction_id": "12345",
    "external_transaction_id": null,
    "message": "You have received 1,000 RWF",
    "readable_date": "2025-09-19 12:00",
    "contact_name": null,
    "raw_json": { "source": "sms" }
  }
]
```

- Error Codes:
  - 401 Unauthorized: Missing/invalid Basic Auth header

---

### 2) Get Transaction by ID

- Endpoint & Method: `GET /transactions/{id}`

- Request Example:

```bash
curl -H "Authorization: Basic $BASIC" http://localhost:8000/transactions/1
```

- Response Example (200 OK):

```json
{
  "id": 1,
  "sms_address": "MTN",
  "sms_date": "2025-09-19T12:00:00+00:00",
  "sms_type": "SMS",
  "sms_body": "You have received 1,000 RWF",
  "transaction_type": "money_in",
  "amount": 1000,
  "currency": "RWF",
  "sender": null,
  "receiver": null,
  "balance": null,
  "fee": 0,
  "transaction_id": "12345",
  "external_transaction_id": null,
  "message": "You have received 1,000 RWF",
  "readable_date": "2025-09-19 12:00",
  "contact_name": null,
  "raw_json": { "source": "sms" }
}
```

- Error Codes:
  - 401 Unauthorized: Missing/invalid Basic Auth header
  - 404 Not Found: No transaction with that id

---

### 3) Create Transaction

- Endpoint & Method: `POST /transactions`

- Request Example:

```bash
curl -X POST \
  -H "Authorization: Basic $BASIC" \
  -H "Content-Type: application/json" \
  -d '{
    "sms_address": "MTN",
    "sms_date": "2025-09-19T12:00:00Z",
    "sms_type": "SMS",
    "sms_body": "You have received 1,000 RWF",
    "transaction_type": "money_in",
    "amount": 1000,
    "currency": "RWF",
    "message": "You have received 1,000 RWF",
    "raw_json": {"source": "manual"}
  }' \
  http://localhost:8000/transactions
```

- Response Example (201 Created):

```json
{
  "id": 101,
  "sms_address": "MTN",
  "sms_date": "2025-09-19T12:00:00+00:00",
  "sms_type": "SMS",
  "sms_body": "You have received 1,000 RWF",
  "transaction_type": "money_in",
  "amount": 1000,
  "currency": "RWF",
  "sender": null,
  "receiver": null,
  "balance": null,
  "fee": 0,
  "transaction_id": null,
  "external_transaction_id": null,
  "message": "You have received 1,000 RWF",
  "readable_date": null,
  "contact_name": null,
  "raw_json": { "source": "manual" }
}
```

- Error Codes:
  - 400 Bad Request: Invalid/missing fields
  - 401 Unauthorized: Missing/invalid Basic Auth header

---

### 4) Update Transaction

- Endpoint & Method: `PUT /transactions/{id}`

- Request Example (partial update):

```bash
curl -X PUT \
  -H "Authorization: Basic $BASIC" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1500, "fee": 20}' \
  http://localhost:8000/transactions/1
```

- Response Example (200 OK):

```json
{
  "id": 1,
  "sms_address": "MTN",
  "sms_date": "2025-09-19T12:00:00+00:00",
  "sms_type": "SMS",
  "sms_body": "You have received 1,000 RWF",
  "transaction_type": "money_in",
  "amount": 1500,
  "currency": "RWF",
  "sender": null,
  "receiver": null,
  "balance": null,
  "fee": 20,
  "transaction_id": "12345",
  "external_transaction_id": null,
  "message": "You have received 1,000 RWF",
  "readable_date": "2025-09-19 12:00",
  "contact_name": null,
  "raw_json": { "source": "sms" }
}
```

- Error Codes:
  - 400 Bad Request: Invalid field types
  - 401 Unauthorized: Missing/invalid Basic Auth header
  - 404 Not Found: No transaction with that id

---

### 5) Delete Transaction

- Endpoint & Method: `DELETE /transactions/{id}`

- Request Example:

```bash
curl -X DELETE -H "Authorization: Basic $BASIC" http://localhost:8000/transactions/1
```

- Response Example (204 No Content):

```
<empty body>
```

- Error Codes:
  - 401 Unauthorized: Missing/invalid Basic Auth header
  - 404 Not Found: No transaction with that id

---

Notes:

- `id` is assigned by the database on create.
- Always send the Basic Auth header; otherwise the API returns 401.