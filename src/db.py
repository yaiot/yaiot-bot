import contextlib
from typing import Any, AsyncIterator, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = None):
        if engine_kwargs is None:
            engine_kwargs = {}

        self._engine = create_async_engine(host, **engine_kwargs)
        self._session_maker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            return

        await self._engine.dispose()

        self._engine = None
        self._session_maker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self._session_maker()

        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager = DatabaseSessionManager(settings.db_host)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_manager.session() as session:
        yield session
