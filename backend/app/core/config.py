from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote_plus
from typing import Optional
from pydantic import model_validator


class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "mygenie"
    DATABASE_URL: Optional[str] = None

    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_ORIGINS: str = ""

    # AI Provider (optional)
    AI_PROVIDER: str = "mock"  # mock, gemini, openai
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.8-flash"
    OPENAI_API_KEY: Optional[str] = None

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgres://"):
                return "postgresql+psycopg://" + url.removeprefix("postgres://")
            if url.startswith("postgresql://"):
                return "postgresql+psycopg://" + url.removeprefix("postgresql://")
            return url

        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins(self) -> list[str]:
        local_origins = (
            []
            if self.ENVIRONMENT.lower() == "production"
            else ["http://localhost:3000", "http://localhost:5173"]
        )
        configured_origins = [
            origin.strip().rstrip("/")
            for origin in self.FRONTEND_ORIGINS.split(",")
            if origin.strip()
        ]
        return list(dict.fromkeys([*local_origins, *configured_origins]))

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production" and (
            len(self.SECRET_KEY) < 32
            or self.SECRET_KEY == "dev-secret-key-change-me"
        ):
            raise ValueError(
                "SECRET_KEY must be at least 32 characters in production."
            )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()