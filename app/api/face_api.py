from fastapi import APIRouter, UploadFile

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
        file: UploadFile,
        employee_id: int
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

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM employee_face
        WHERE employee_id=%s
        """,
        (employee_id,)
    )

    count = cursor.fetchone()[0]

    if count > 0:

        return {
            "success": False,
            "message":
            "Face already registered"
        }

    embedding = generate_embedding(
        image
    )

    cursor.execute(
        """
        INSERT INTO employee_face(
            employee_id,
            embedding
        )
        VALUES(%s,%s)
        """,
        (
            employee_id,
            embedding
        )
    )

    conn.commit()

    return {

        "success": True,
        "message":
            "Face registered successfully"
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