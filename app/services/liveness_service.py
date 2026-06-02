import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True
)


def detect_head_turn(image):

    image_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    results = face_mesh.process(
        image_rgb
    )

    if not results.multi_face_landmarks:
        return False

    landmarks = (
        results
        .multi_face_landmarks[0]
        .landmark
    )

    nose = landmarks[1]

    left_cheek = landmarks[234]

    right_cheek = landmarks[454]

    left_distance = abs(
        nose.x -
        left_cheek.x
    )

    right_distance = abs(
        nose.x -
        right_cheek.x
    )

    difference = abs(
        left_distance -
        right_distance
    )

    return difference > 0.05