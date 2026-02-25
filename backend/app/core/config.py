from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── 應用程式 ────────────────────────────────────────
    APP_NAME: str = "家庭購物清單"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # ── 資料庫 ──────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/shoppinglist"

    # ── JWT ─────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_256BIT_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── SMTP ────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@shoppinglist.app"

    # ── 邀請 Token 有效期 (小時) ─────────────────────────
    INVITATION_EXPIRE_HOURS: int = 48

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
