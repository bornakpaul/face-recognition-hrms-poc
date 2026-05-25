from fastapi import FastAPI, UploadFile
from insightface.app import FaceAnalysis

import cv2
import numpy as np
import psycopg2
      
app = FastAPI()

face_model = FaceAnalysis(name="buffalo_l")

face_model.prepare(ctx_id=0,)

conn = psycopg2.connect(
    host="localhost",
    port="5434",
    database="hrms",
    user="admin",
    password="admin"
)

cursor = conn.cursor()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect-face")
async def detect_face(file: UploadFile):
    image_bytes = await file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if image is None:

        return {
            "success": False,
            "message":
            "Invalid image uploaded"
        }

    faces = face_model.get(image)

    return {"face_count": len(faces)}

@app.post("/embedding")
async def embedding(file: UploadFile):
    image_bytes = await file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if image is None:

        return {
            "success": False,
            "message":
            "Invalid image uploaded"
        }

    faces = face_model.get(image)

    if len(faces)==0:
        return {"success":False,"message":"No face detected"}

    embedding = faces[0].embedding

    return {
        "success":True,
        "embedding":
            embedding.tolist(),
        "dimensions":
            len(embedding)
    }

@app.post("/register-face")
async def register_face(file:UploadFile,employee_id:int):
    image_bytes= await file.read()
    image_np=np.frombuffer(image_bytes,np.uint8)
    image=cv2.imdecode(image_np,cv2.IMREAD_COLOR)

    if image is None:
        return {
            "success":False,
            "message":"invalid image uploaded"
        }

    faces = face_model.get(image)

    if len(faces) == 0:
        return {
            "success":False,
            "message":"No face detected"
        }

    embedding = faces[0].embedding.tolist()

    cursor.execute(
        """
        INSERT INTO employee_face(
        employee_id,
        embedding
        )
        VALUES(%s,%s)
        """,
        (employee_id,embedding)
    )
    conn.commit()

    return {
        "success":True,
        "message":"face registered successfully"
    }


@app.post("/recognize")
async def recognize(file:UploadFile):
    image_bytes = await file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np,cv2.IMREAD_COLOR)

    faces = face_model.get(image)

    if len(faces) ==0:
        return {
            "success":False,
            "message":"No face detected"
        }

    embedding = faces[0].embedding.tolist()

    cursor.execute(
        """
        SELECT employee_id,
        embedding <=> %s::vector AS distance
        FROM employee_face
        ORDER BY distance
        LIMIT 1;
        """,
        (embedding,)
    )

    result = cursor.fetchone()

    if result is None:
        return {"success":False,"message":"No match found"}

    employee_id,distance = result

    return {
        "success":True,
        "employee_id":employee_id,
        "distance":distance
    }
