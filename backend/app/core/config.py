from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore')

    PROJECT_NAME: str = "Tariff Navigator"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # SQLite for development (zero setup)
    DATABASE_URL: str = "sqlite+aiosqlite:///./tariffnavigator.db"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
