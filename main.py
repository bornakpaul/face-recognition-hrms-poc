from fastapi import FastAPI, UploadFile
from insightface.app import FaceAnalysis

import cv2
import numpy as np
      
app = FastAPI()

face_model = FaceAnalysis(name="buffalo_l")

face_model.prepare(ctx_id=0,)


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
