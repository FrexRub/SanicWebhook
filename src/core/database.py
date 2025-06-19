from sanic.config import Config
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import setting


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    url=setting.db.url,
    echo=setting.db.echo,
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class DatabaseConnection:

    def __init__(self, config: Config) -> None:
        self._url: URL = URL.create(
            config.DB_DRIVER,
            config.DB_USER,
            config.DB_PASSWORD,
            config.DB_HOST,
            config.DB_PORT,
            config.DB_NAME,
        )
        self._connection: AsyncEngine = create_async_engine(
            url=self._url, echo=setting.db.echo
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self._connection,
            expire_on_commit=False,
        )

    def create_session(self) -> AsyncSession:
        return self._session_factory()
