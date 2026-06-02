from insightface.app import FaceAnalysis

face_model = FaceAnalysis(
    name="buffalo_l"
)

face_model.prepare(
    ctx_id=0
)