from fastapi import FastAPI
from .config import settings
from .routes import fileUpload

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.include_router(fileUpload.router, prefix="/uploads", tags=["uploads"])


@app.get("/")
def root():
    return {"message": "Welcome to Adaptive Knowledge Chatbot!"}
