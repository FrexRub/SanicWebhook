import asyncio
from typing import AsyncGenerator, Generator

from sanic_testing.testing import SanicTestClient

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.main import WebhookApp
from src.core.database import Base
from src.core.config import ConnectionsConfig


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/testdb"


@pytest.fixture
def test_config():
    class TestConfig(ConnectionsConfig):
        DB_DRIVER = "postgresql+asyncpg"
        DB_USER = "test"
        DB_PASSWORD = "test"
        DB_HOST = "localhost"
        DB_PORT = 5432
        DB_NAME = "testdb"

    return TestConfig()


@pytest_asyncio.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    yield loop
    loop.close()



@pytest.fixture
async def app(test_config):
    _app = WebhookApp("TestWebhookApp", test_mode=True)
    _app.update_config(test_config)

    @_app.before_server_start
    async def setup_db(app, _):
        _app.setup_db(test_config)

    yield _app


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def client(app):
    return SanicTestClient(app)



@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine: AsyncEngine = create_async_engine(SQLALCHEMY_DATABASE_URL)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()  # Важно!


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()
