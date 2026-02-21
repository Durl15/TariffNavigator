from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore')

    PROJECT_NAME: str = "Tariff Navigator"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production

    # SQLite for development (zero setup)
    DATABASE_URL: str = "sqlite+aiosqlite:///./tariffnavigator.db"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]

    # Email Settings (Phase 2)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Set via environment variable
    SMTP_PASSWORD: str = ""  # Set via environment variable
    FROM_EMAIL: str = "noreply@tariffnavigator.com"
    FROM_NAME: str = "TariffNavigator"
    FRONTEND_URL: str = "http://localhost:3000"

    # AI Settings (Phase 3)
    OPENAI_API_KEY: str = ""  # Set via environment variable

    def model_post_init(self, __context) -> None:
        """Validate settings after initialization"""
        # Warn if using default secret key in production
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError(
                "CRITICAL: Default SECRET_KEY detected in production! "
                "Generate a strong key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
