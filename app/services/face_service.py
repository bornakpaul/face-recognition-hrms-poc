from app.models.face_model import face_model


def detect_faces(image):

    return face_model.get(image)


def generate_embedding(image):

    faces = face_model.get(image)

    if len(faces) == 0:
        return None

    return faces[0].embedding.tolist()