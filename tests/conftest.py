import asyncio
from typing import AsyncGenerator, Generator

import pytest_asyncio
import sanic_testing
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.main import app as _app
from src.utils.jwt_utils import create_hash_password
from src.core.database import Base
from src.users.models import User


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/testdb"


class ConnectionsConfig:
    DB_DRIVER = "postgresql+asyncpg"
    DB_USER = "test"
    DB_PASSWORD = "test"
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_NAME = "testdb"


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def app():
    app = _app
    app.set_config()
    app.config["TESTING"] = True
    app.update_config(ConnectionsConfig)

    yield app


# @pytest_asyncio.fixture(loop_scope="function", scope="function")
# def client(app):
#     return app.test_client()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
# def test_cli(loop, app, test_client):
#     return loop.run_until_complete(test_client(app, protocol=WebSocketProtocol))
def test_cli(event_loop, app, test_client):
    return event_loop.run_until_complete(test_client(app))

#
#
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


#
#
# @pytest_asyncio.fixture(loop_scope="function", scope="function")
# async def override_get_db(db_session: AsyncSession):
#     async def _override_get_db():
#         try:
#             yield db_session
#         finally:
#             await db_session.close()  # Закрываем сессию после использования
#
#     return _override_get_db
#
#
# @pytest_asyncio.fixture(loop_scope="function", scope="function")
# async def client(
#     override_get_db, override_get_redis_cache
# ) -> AsyncGenerator[AsyncClient, None]:
#     app.dependency_overrides[get_async_session] = override_get_db
#     app.dependency_overrides[get_cache_connection] = override_get_redis_cache
#     async with AsyncClient(app=app, base_url="http://test") as c:
#         yield c
#     app.dependency_overrides.clear()  # Важно
#
#
# @pytest_asyncio.fixture(loop_scope="function", scope="function")
# async def test_user_admin(db_session: AsyncSession) -> User:
#     stmt = select(User).filter(User.email == "testuser@example.com")
#     res: Result = await db_session.execute(stmt)
#     user: User = res.scalar_one_or_none()
#     if user is None:
#         user_hashed_password: bytes = await create_hash_password("1qaz!QAZ")
#         user: User = User(
#             full_name="TestUser",
#             email="testuser@example.com",
#             hashed_password=user_hashed_password.decode(),
#             is_superuser=True,
#         )
#
#         db_session.add(user)
#         await db_session.commit()
#
#     return user
#
#
# @pytest_asyncio.fixture(loop_scope="function", scope="function")
# async def token_admin(
#     client: AsyncClient,
#     test_user_admin: User,
# ) -> str:
#     token_response = await client.post(
#         "/api/users/login",
#         json={"username": "testuser@example.com", "password": "1qaz!QAZ"},
#     )
#     token: str = token_response.json()["access_token"]
#     return token
#
#
# @pytest_asyncio.fixture(loop_scope="function", scope="function")
# async def test_user(db_session: AsyncSession) -> User:
#     stmt = select(User).filter(User.email == "petr@mail.com")
#     res: Result = await db_session.execute(stmt)
#     user: User = res.scalar_one_or_none()
#     if user is None:
#         user_hashed_password: bytes = await create_hash_password("2wsx@WSX")
#         user: User = User(
#             full_name="Petr",
#             email="petr@mail.com",
#             hashed_password=user_hashed_password.decode(),
#         )
#
#         db_session.add(user)
#         await db_session.commit()
#
#     return user
#
#
# @pytest_asyncio.fixture(loop_scope="function", scope="function")
# async def test_db(db_session: AsyncSession):
#     await data_from_files_to_test_db(db_session)
#     return db_session
