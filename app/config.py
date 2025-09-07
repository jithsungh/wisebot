from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    # DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()
