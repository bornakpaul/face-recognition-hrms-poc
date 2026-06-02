# Face Recognition HRMS POC

A Python-based Face Recognition and Liveness Detection service built using FastAPI, InsightFace, MediaPipe, PostgreSQL, and pgvector.

This service is designed to support employee attendance systems where employees can check in/out by looking at a camera mounted on a tablet or kiosk device.

---

# Features

* Face Detection
* Face Embedding Generation
* Employee Face Registration
* Face Recognition
* Basic Liveness Detection (Head Turn Detection)
* PostgreSQL Vector Storage
* pgvector Similarity Search
* Swagger API Documentation

---

# Technology Stack

| Component          | Technology              |
| ------------------ | ----------------------- |
| Backend API        | FastAPI                 |
| Face Recognition   | InsightFace (buffalo_l) |
| Computer Vision    | OpenCV                  |
| Liveness Detection | MediaPipe FaceMesh      |
| Database           | PostgreSQL              |
| Vector Search      | pgvector                |
| API Documentation  | Swagger/OpenAPI         |
| Containerization   | Docker                  |

---

# Project Structure

app/

├── api/

│ └── face_api.py

│

├── db/

│ └── database.py

│

├── models/

│ └── face_model.py

│

├── services/

│ ├── face_service.py

│ └── liveness_service.py

│

├── utils/

│ └── image_utils.py

│

└── main.py

---

# Setup Instructions

## 1. Create Virtual Environment

```bash
python3.11 -m venv venv

source venv/bin/activate
```

## 2. Install Dependencies

```bash
pip install fastapi

pip install uvicorn

pip install insightface

pip install onnxruntime

pip install opencv-python

pip install numpy

pip install psycopg2-binary

pip install mediapipe

pip install python-multipart
```

---

# PostgreSQL Setup

## Start PostgreSQL + pgvector using Docker

docker-compose.yml

```yaml
services:

  postgres:

    image: ankane/pgvector

    restart: always

    environment:

      POSTGRES_DB: hrms

      POSTGRES_USER: admin

      POSTGRES_PASSWORD: admin

    ports:

      - "5434:5432"

    volumes:

      - pgdata:/var/lib/postgresql/data

volumes:

  pgdata:
```

Start Docker:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

---

# Database Setup

Connect to PostgreSQL:

```bash
psql -h localhost -p 5434 -U admin -d hrms
```

Password:

```text
admin
```

Enable pgvector:

```sql
CREATE EXTENSION vector;
```

Create table:

```sql
CREATE TABLE employee_face (

    id BIGSERIAL PRIMARY KEY,

    employee_id BIGINT,

    embedding VECTOR(512),

    created_at TIMESTAMP DEFAULT NOW()

);
```

---

# Running the Application

From project root:

```bash
uvicorn app.main:app --reload --port 8001
```

Swagger:

```text
http://localhost:8001/docs
```

---

# API Documentation

## Health Check

GET

```text
/health
```

Response:

```json
{
  "status": "ok"
}
```

---

## Face Detection

POST

```text
/detect-face
```

Input:

multipart/form-data

```text
file: image
```

Response:

```json
{
  "success": true,
  "face_count": 1
}
```

---

## Generate Face Embedding

POST

```text
/embedding
```

Input:

```text
file: image
```

Response:

```json
{
  "success": true,
  "embedding": [...],
  "dimensions": 512
}
```

---

## Register Employee Face

POST

```text
/register-face
```

Input:

```text
employee_id=11

file=image
```

Response:

```json
{
  "success": true,
  "message": "Face registered successfully"
}
```

---

## Face Recognition

POST

```text
/recognize
```

Input:

```text
file=image
```

Response:

```json
{
  "success": true,
  "employee_id": 11,
  "distance": 0.08,
  "confidence": 92.0,
  "recognised": true,
  "live": true
}
```

Field Description:

| Field       | Description            |
| ----------- | ---------------------- |
| employee_id | Matched employee       |
| distance    | Vector distance        |
| confidence  | Match confidence       |
| recognised  | Face match result      |
| live        | Head movement detected |

---

## Liveness Detection

POST

```text
/liveness
```

Input:

```text
file=image
```

Response:

```json
{
  "success": true,
  "live": true
}
```

---

# Recognition Logic

Employee Registration:

Image

↓

Embedding Generation

↓

Store in PostgreSQL

↓

employee_face

Recognition:

Image

↓

Embedding Generation

↓

Vector Search (pgvector)

↓

Nearest Employee

↓

Confidence Calculation

↓

Recognition Result

---

# Current Limitations

This is a Proof of Concept (POC).

Current liveness detection uses MediaPipe head-turn detection and can be bypassed using replay attacks.

Examples:

* Mobile screen replay
* Laptop replay
* Video replay attack

---

# Authors

Bornak Paul
HRMS Face Recognition POC
