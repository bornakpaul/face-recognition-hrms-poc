import zipfile
from fastapi import APIRouter, UploadFile, File
from typing import List

from app.utils.image_utils import decode_image

from app.services.face_service import (
    detect_faces,
    generate_embedding
)

from app.services.liveness_service import (
    detect_head_turn
)

from app.db.database import (
    cursor,
    conn
)

router = APIRouter()


@router.get("/health")
def health():

    return {
        "status": "ok"
    }


@router.post("/detect-face")
async def detect_face(
        file: UploadFile
):

    image_bytes = await file.read()

    image = decode_image(
        image_bytes
    )

    if image is None:

        return {

            "success": False,
            "message":
            "Invalid image uploaded"
        }

    faces = detect_faces(
        image
    )

    return {

        "success": True,
        "face_count":
            len(faces)
    }


@router.post("/embedding")
async def embedding(
        file: UploadFile
):

    image_bytes = await file.read()

    image = decode_image(
        image_bytes
    )

    if image is None:

        return {
            "success": False,
            "message":
            "Invalid image uploaded"
        }

    faces = detect_faces(
        image
    )

    if len(faces) == 0:

        return {
            "success": False,
            "message":
            "No face detected"
        }

    if len(faces) > 1:

        return {
            "success": False,
            "message":
            "Multiple faces detected"
        }

    embedding = generate_embedding(
        image
    )

    return {
        "success": True,
        "embedding":
            embedding,
        "dimensions":
            len(embedding)
    }


@router.post("/register-face")
async def register_face(
        files: List[UploadFile] = File(...),
        employee_id: int = File(...)
):

    registered_faces = 0

    failed_files = []

    for file in files:

        try:

            image_bytes = await file.read()

            image = decode_image(
                image_bytes
            )

            if image is None:

                failed_files.append({
                    "file": file.filename,
                    "reason": "Invalid image uploaded"
                })

                continue


            faces = detect_faces(
                image
            )

            if len(faces) == 0:

                failed_files.append({
                    "file": file.filename,
                    "reason": "No face detected"
                })

                continue


            if len(faces) > 1:

                failed_files.append({
                    "file": file.filename,
                    "reason": "Multiple faces detected"
                })

                continue


            embedding = generate_embedding(
                image
            )

            cursor.execute(
                """
                INSERT INTO employee_face(
                    employee_id,
                    embedding,
                    created_at
                )
                VALUES(
                    %s,
                    %s,
                    NOW()
                )
                """,
                (
                    employee_id,
                    embedding
                )
            )

            registered_faces += 1

        except Exception as ex:

            failed_files.append({
                "file": file.filename,
                "reason": str(ex)
            })

    conn.commit()

    return {

        "success": registered_faces > 0,

        "employee_id": employee_id,

        "total_files": len(files),

        "registered_faces": registered_faces,

        "failed_faces":
            len(failed_files),

        "failed_files":
            failed_files
    }


@router.post("/recognize")
async def recognize(
        file: UploadFile
):

    image_bytes = await file.read()

    image = decode_image(
        image_bytes
    )

    if image is None:

        return {

            "success": False,
            "message":
            "Invalid image uploaded"
        }

    faces = detect_faces(
        image
    )

    if len(faces) == 0:

        return {

            "success": False,
            "message":
            "No face detected"
        }

    if len(faces) > 1:

        return {

            "success": False,
            "message":
            "Multiple faces detected"
        }

    live = detect_head_turn(
        image
    )

    embedding = generate_embedding(
        image
    )

    cursor.execute(
        """
        SELECT
            employee_id,

            embedding <=> %s::vector
            AS distance

        FROM employee_face

        ORDER BY distance

        LIMIT 1
        """,
        (embedding,)
    )

    result = cursor.fetchone()

    if result is None:

        return {

            "success": False,
            "message":
            "No match found"
        }

    employee_id, distance = result

    confidence = max(
        0,
        round(
            (1 - distance) * 100,
            2
        )
    )

    recognised = (
        distance < 0.20
    )

    return {
        "success": True,
        "employee_id":
            employee_id,
        "distance":
            distance,
        "confidence":
            confidence,
        "recognised":
            recognised,
            "live": live,
    }


@router.post("/liveness")
async def liveness(
        file: UploadFile
):

    image_bytes = await file.read()

    image = decode_image(
        image_bytes
    )

    if image is None:

        return {

            "success": False,
            "message":
            "Invalid image uploaded"
        }

    live = detect_head_turn(
        image
    )

    return {
        "success": True,
        "live": live
    }