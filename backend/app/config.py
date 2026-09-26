import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

def _parse_origins(raw: str) -> List[str]:
    """Parse comma-separated CORS origins from env var."""
    return [o.strip() for o in raw.split(",") if o.strip()]

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ENV: str = os.getenv("ENV", "development")
    MAX_UPLOAD_SIZE_MB: int = 25
    # Maximum characters allowed in a single chat question (security: prevent prompt injection overload)
    MAX_QUESTION_LENGTH: int = int(os.getenv("MAX_QUESTION_LENGTH", "1000"))
    # Maximum documents held in memory at once (LRU eviction when exceeded)
    MAX_STORAGE_DOCS: int = int(os.getenv("MAX_STORAGE_DOCS", "50"))
    # CORS: comma-separated list of allowed origins; defaults to localhost only
    ALLOWED_ORIGINS: List[str] = _parse_origins(
        os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
    )

settings = Settings()
