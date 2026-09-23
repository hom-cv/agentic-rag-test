from functools import lru_cache

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import get_settings


@lru_cache
def build_async_engine() -> AsyncEngine:
    settings = get_settings()
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
    )
    return create_async_engine(
        url, pool_pre_ping=True, connect_args={"ssl": False}
    )


@lru_cache
def build_async_session() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(build_async_engine(), expire_on_commit=False)


async def close_db() -> None:
    """Dispose an existing pool without creating one solely for shutdown."""
    try:
        if build_async_engine.cache_info().currsize:
            await build_async_engine().dispose()
    finally:
        build_async_session.cache_clear()
        build_async_engine.cache_clear()
