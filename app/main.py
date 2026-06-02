from fastapi import FastAPI

from app.api.face_api import router


app = FastAPI()

app.include_router(router)