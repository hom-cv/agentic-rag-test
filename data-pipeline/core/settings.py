from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Database environment variables, loaded by Pipenv from .env."""

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
