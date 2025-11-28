import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.app import app
from app.core.database import Base, get_session


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine(event_loop):
    """Create a shared in-memory SQLite engine and initialize the schema once."""

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    event_loop.run_until_complete(init_models())
    yield engine
    event_loop.run_until_complete(engine.dispose())


@pytest.fixture(scope="session")
def session_maker(engine):
    """Async session factory bound to the shared in-memory engine."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def client(session_maker):
    """FastAPI TestClient with DB session dependency overridden to use the test DB."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
