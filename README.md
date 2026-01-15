# Lyftr Backend Assignment

A FastAPI-based backend service that receives webhook messages, validates them using HMAC-SHA256, stores them in SQLite with idempotency, and exposes APIs for listing messages and analytics.

---

## Features

- FastAPI backend
- Secure webhook with HMAC-SHA256 validation
- SQLite database for persistence
- Idempotent message handling
- Health check endpoints
- Message listing with pagination & filters
- Analytics endpoint
- Docker & Docker Compose support

---

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLite
- Docker
- Docker Compose

---

## Project Structure

```
lyftr/
│
├── app/
│ ├── main.py # FastAPI routes
│ ├── storage.py # Database logic
│
├── data/
│ └── app.db # SQLite database (auto-created)
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
```

---

## Running With Docker

### Prerequisites

- Docker
- Docker Compose

### Build and run

```bash
docker compose build
docker compose up
```

---

## Health Endpoints

### Live

**GET** `/health/live`

Response:
```json
{ "status": "live" }
```

### Ready

**GET** `/health/ready`

Response:
```json
{ "status": "ready" }
```

---

## Webhook Endpoint

**POST** `/webhook`

### Headers

- `Content-Type: application/json`
- `X-Signature: <HMAC_SHA256_SIGNATURE>`

### Sample Body

```json
{
  "message_id": "m1",
  "from_": "+919876543210",
  "to": "+14155550100",
  "ts": "2025-01-15T10:00:00Z",
  "text": "Hello"
}
```

### Behavior

- Invalid signature → 401 Unauthorized
- Valid signature → message stored → `{"status":"ok"}`
- Duplicate message_id → ignored → `{"status":"ok"}`

---

## List Messages API

**GET** `/messages`

### Query Parameters

- `limit` – number of messages
- `offset` – pagination offset
- `from` – filter by sender
- `since` – ISO timestamp
- `q` – text search

### Response

```json
{
  "data": [
    {
      "message_id": "m1",
      "from": "+919876543210",
      "to": "+14155550100",
      "ts": "2025-01-15T10:00:00Z",
      "text": "Hello"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

## Stats API

**GET** `/stats`

### Response

```json
{
  "total_messages": 1,
  "unique_senders": 1,
  "top_senders": [
    {
      "from": "+919876543210",
      "count": 1
    }
  ],
  "first_message_ts": "2025-01-15T10:00:00Z",
  "last_message_ts": "2025-01-15T10:00:00Z"
}
```

---

## Design Decisions

- HMAC-SHA256 ensures webhook authenticity
- SQLite chosen for simplicity and portability
- Idempotency implemented using message_id as PRIMARY KEY
- Database logic separated from API routes
- Docker used for consistent deployment

---

## Author

**Amisha Yadav**
- B.Tech CSE
- Backend Developer (Python, FastAPI)