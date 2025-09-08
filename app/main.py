from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import fileUpload, chat

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # Vite dev server and production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(fileUpload.router, prefix="/upload", tags=["uploads"])
app.include_router(chat.router, prefix="", tags=["chat"])

@app.get("/")
def root():
    return {
        "message": "Welcome to WiseBot - Adaptive Knowledge Chatbot!",
        "docs": "/docs",
        "frontend": "http://localhost:5173"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
