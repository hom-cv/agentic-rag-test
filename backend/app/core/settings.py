from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment variables"""
    APP_NAME: str = "Agentic RAG"
    BASE_URL: str = "http://localhost:3000"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "agentic_rag"


@lru_cache
def get_settings() -> Settings:
    return Settings()
