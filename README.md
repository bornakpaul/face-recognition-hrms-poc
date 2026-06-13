# Face Recognition HRMS POC

A Python-based Face Recognition and Liveness Detection service built using FastAPI, InsightFace, MediaPipe, PostgreSQL, and pgvector.

This service is designed to support employee attendance systems where employees can check in/out by looking at a camera mounted on a tablet or kiosk device.

---

# Features

* Face Detection
* Face Embedding Generation
* Multiple Face Registration per Employee
* Face Recognition
* Basic Liveness Detection (Head Turn Detection)
* PostgreSQL Vector Storage
* pgvector Similarity Search
* Swagger API Documentation
* Dockerized PostgreSQL Setup

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

```
app/

├── api/
│   └── face_api.py

├── db/
│   └── database.py

├── models/
│   └── face_model.py

├── services/
│   ├── face_service.py
│   └── liveness_service.py

├── utils/
│   └── image_utils.py

└── main.py
```

---

# Setup Instructions

## Create Virtual Environment

```bash
python3.11 -m venv venv

source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

If requirements.txt is unavailable:

```bash
pip install fastapi
pip install uvicorn
pip install insightface
pip install onnxruntime
pip install opencv-python
pip install numpy
pip install psycopg2-binary
pip install mediapipe==0.10.14
pip install python-multipart
```

---

# PostgreSQL Setup

## Docker Compose

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

Start PostgreSQL:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

---

# Database Setup

Enable pgvector:

```sql
CREATE EXTENSION vector;
```

Create table:

```sql
CREATE TABLE employee_face (

    id BIGSERIAL PRIMARY KEY,

    employee_id BIGINT NOT NULL,

    embedding VECTOR(512) NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()

);
```

---

# Running The Application

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

### GET

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

## Detect Face

### POST

```text
/detect-face
```

Input:

```text
file=image
```

Response:

```json
{
  "face_count": 1
}
```

---

## Generate Embedding

### POST

```text
/embedding
```

Input:

```text
file=image
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

## Register Employee Faces

Registers multiple face images for a single employee.

### POST

```text
/register-face
```

Input (multipart/form-data):

```text
employee_id = 17

files = front.jpg
files = left.jpg
files = right.jpg
files = smile.jpg
files = up.jpg
files = down.jpg
```

Response:

```json
{
  "success": true,
  "employee_id": 17,
  "total_files": 6,
  "registered_faces": 6,
  "failed_faces": 0,
  "failed_files": []
}
```

Example Partial Success:

```json
{
  "success": true,
  "employee_id": 17,
  "total_files": 6,
  "registered_faces": 4,
  "failed_faces": 2,
  "failed_files": [
    {
      "file": "group.jpg",
      "reason": "Multiple faces detected"
    }
  ]
}
```

---

## Face Recognition

### POST

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
  "employee_id": 17,
  "distance": 0.08,
  "confidence": 92.0,
  "recognised": true,
  "live": true
}
```

Field Description:

| Field       | Description                |
| ----------- | -------------------------- |
| employee_id | Matched employee           |
| distance    | Vector similarity distance |
| confidence  | Recognition confidence     |
| recognised  | Face match result          |
| live        | Head-turn liveness result  |

---

## Liveness Detection

### POST

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

# Recognition Flow

Employee Registration:

```
Multiple Images
        ↓
Face Detection
        ↓
Embedding Generation
        ↓
Store Multiple Embeddings
        ↓
PostgreSQL + pgvector
```

Employee Recognition:

```
Image
  ↓
Embedding Generation
  ↓
Vector Similarity Search
  ↓
Nearest Embedding Match
  ↓
Employee Identified
  ↓
Confidence Calculation
  ↓
Liveness Validation
```

---

# Current Limitations

This project is currently a Proof of Concept (POC).

Current liveness detection is based on head-turn detection using MediaPipe FaceMesh.

Possible spoofing methods:

* Printed photograph
* Mobile screen replay
* Laptop screen replay
* Video replay attack

For production environments, consider integrating:

* Silent Face Anti Spoof
* MiniFASNet
* Passive Liveness Detection
* Blink Detection
* Depth Detection

---

# Authors

Bornak Paul

Senior Software Engineer / System Analyst - I

HRMS Face Recognition POC
