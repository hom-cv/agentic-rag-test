from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import build_async_session


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a db session"""
    async with build_async_session()() as session:
        yield session


AnnotatedSession = Annotated[AsyncSession, Depends(get_db)]
