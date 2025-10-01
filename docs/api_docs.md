# SMS Transactions REST API Documentation

## Overview
This REST API provides CRUD operations for SMS transaction data. It uses Basic Authentication and returns JSON responses.

**Base URL:** `http://localhost:8000`  
**Authentication:** Basic Auth (username: `admin`, password: `password`)

## Authentication
All endpoints require Basic Authentication. Include the Authorization header in your requests:

```
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

The encoded string above represents `admin:password` in base64.

## Endpoints

### 1. GET /transactions
**Description:** Retrieve all SMS transactions

**Request:**
```bash
curl -X GET http://localhost:8000/transactions \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ="
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "sender": "John Doe",
    "recipient": "Jane Smith",
    "message": "Hello, how are you today?",
    "timestamp": "2024-01-15 10:30:00",
    "amount": 0.00,
    "status": "sent"
  },
  {
    "id": 2,
    "sender": "Alice Johnson",
    "recipient": "Bob Wilson",
    "message": "Meeting at 2 PM today",
    "timestamp": "2024-01-15 11:45:00",
    "amount": 0.00,
    "status": "delivered"
  }
]
```

### 2. GET /transactions/{id}
**Description:** Retrieve a specific SMS transaction by ID

**Request:**
```bash
curl -X GET http://localhost:8000/transactions/1 \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ="
```

**Response (200 OK):**
```json
{
  "id": 1,
  "sender": "John Doe",
  "recipient": "Jane Smith",
  "message": "Hello, how are you today?",
  "timestamp": "2024-01-15 10:30:00",
  "amount": 0.00,
  "status": "sent"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Transaction not found"
}
```

### 3. POST /transactions
**Description:** Create a new SMS transaction

**Request:**
```bash
curl -X POST http://localhost:8000/transactions \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "New User",
    "recipient": "Another User",
    "message": "This is a new message",
    "timestamp": "2024-01-16 12:00:00",
    "amount": 5.50,
    "status": "sent"
  }'
```

**Response (201 Created):**
```json
{
  "id": 26,
  "sender": "New User",
  "recipient": "Another User",
  "message": "This is a new message",
  "timestamp": "2024-01-16 12:00:00",
  "amount": 5.50,
  "status": "sent"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Missing required fields"
}
```

### 4. PUT /transactions/{id}
**Description:** Update an existing SMS transaction

**Request:**
```bash
curl -X PUT http://localhost:8000/transactions/1 \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "John Doe Updated",
    "recipient": "Jane Smith",
    "message": "Updated message content",
    "timestamp": "2024-01-15 10:30:00",
    "amount": 0.00,
    "status": "delivered"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "sender": "John Doe Updated",
  "recipient": "Jane Smith",
  "message": "Updated message content",
  "timestamp": "2024-01-15 10:30:00",
  "amount": 0.00,
  "status": "delivered"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Transaction not found"
}
```

### 5. DELETE /transactions/{id}
**Description:** Delete an SMS transaction

**Request:**
```bash
curl -X DELETE http://localhost:8000/transactions/1 \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ="
```

**Response (200 OK):**
```json
{
  "message": "Transaction deleted",
  "deleted": {
    "id": 1,
    "sender": "John Doe",
    "recipient": "Jane Smith",
    "message": "Hello, how are you today?",
    "timestamp": "2024-01-15 10:30:00",
    "amount": 0.00,
    "status": "sent"
  }
}
```

**Response (404 Not Found):**
```json
{
  "error": "Transaction not found"
}
```

## Error Codes

| Code | Description | Example Response |
|------|-------------|------------------|
| 200  | Success     | Transaction data |
| 201  | Created     | New transaction data |
| 400  | Bad Request | `{"error": "Invalid transaction ID"}` |
| 401  | Unauthorized | `{"error": "Unauthorized", "message": "Invalid credentials"}` |
| 404  | Not Found   | `{"error": "Transaction not found"}` |

## Data Model

### Transaction Object
```json
{
  "id": 1,                    // Integer (auto-generated for POST)
  "sender": "John Doe",       // String (required)
  "recipient": "Jane Smith",  // String (required)
  "message": "Hello...",      // String (required)
  "timestamp": "2024-01-15 10:30:00", // String (required)
  "amount": 0.00,             // Float (required)
  "status": "sent"            // String (required)
}
```

## Testing Examples

### Using curl (Command Line)
```bash
# Get all transactions
curl -X GET http://localhost:8000/transactions \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ="

# Get specific transaction
curl -X GET http://localhost:8000/transactions/1 \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ="

# Create new transaction
curl -X POST http://localhost:8000/transactions \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{"sender":"Test","recipient":"User","message":"Test message","timestamp":"2024-01-16 12:00:00","amount":0.00,"status":"sent"}'

# Update transaction
curl -X PUT http://localhost:8000/transactions/1 \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{"sender":"Updated","recipient":"User","message":"Updated message","timestamp":"2024-01-16 12:00:00","amount":0.00,"status":"delivered"}'

# Delete transaction
curl -X DELETE http://localhost:8000/transactions/1 \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ="
```

### Using Postman
1. Set Base URL: `http://localhost:8000`
2. Add Authorization: Basic Auth (Username: `admin`, Password: `password`)
3. Set Content-Type: `application/json` for POST/PUT requests
4. Use the endpoint paths and request bodies from the examples above

## Security Notes

**Basic Authentication Limitations:**
- Credentials are sent in every request (base64 encoded, not encrypted)
- No session management or token expiration
- Credentials can be easily decoded from base64
- No protection against replay attacks

**Recommended Alternatives:**
- **JWT (JSON Web Tokens):** Stateless, secure token-based authentication
- **OAuth2:** Industry standard for authorization
- **API Keys:** Simple but more secure than Basic Auth
- **Session-based Auth:** Server-side session management
