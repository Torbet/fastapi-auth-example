from importlib import import_module
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def load_models():
    """Import all model modules so SQLAlchemy's metadata is populated.

    This is used both by the FastAPI app (via lifespan) and by Alembic
    migrations to discover the `User` model.
    """
    import_module("app.models.user")
