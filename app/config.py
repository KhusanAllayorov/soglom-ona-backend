import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./soglom_ona.sqlite3")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "soglom_ona_secure_key_2026_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 kun

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        # Railway ba'zida "postgres://" beradi, SQLAlchemy 2.0 "postgresql://" talab qiladi
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
