from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, text

from src.config import settings
from src.db import get_db_session, session_manager
from src.models import User
from src.yandex import YandexClient, get_yandex_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Context manager that is used to manage the lifespan of the application.
    https://fastapi.tiangolo.com/advanced/events/

    :param _: FastAPI application instance.
    """

    async with session_manager.connect() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    yield

    await session_manager.close()


app = FastAPI(lifespan=lifespan)
server = uvicorn.Server(
    config=uvicorn.Config(app, host=settings.host, port=settings.port)
)

Session = Annotated[AsyncSession, Depends(get_db_session)]
YandexClient = Annotated[YandexClient, Depends(get_yandex_client)]


@app.get("/auth/yandex/callback")
async def yandex_auth(
    code: str,
    state: int,
    session: Session,
    client: YandexClient,
) -> str:
    """
    Yandex OAuth2 authorization endpoint, which is used to store the user's access token in the database.
    https://yandex.ru/dev/id/doc/ru/concepts/ya-oauth-intro

    :param code: authorization code, which is used to get the access token.
    :param state: telegram user id, which is used to store the access token in the database.
    :param session: dependency that provides a database session.
    :param client: dependency that provides an HTTP client for sending requests.
    :return:
    """

    td = await client.exchange_code_for_data(code)
    user = User(
        telegram_id=state,
        access_token=td.access_token,
        refresh_token=td.refresh_token,
        # The token is valid for 1 year, expires_in is duration in seconds.
        # Remembers the expiration timestamp of the token, minus one day for reliability.
        expires_at=int(
            (datetime.now() + timedelta(seconds=td.expires_in - 86400)).timestamp()
        ),
    )

    await session.execute(
        text(
            "INSERT INTO user (telegram_id, access_token, refresh_token, expires_at)"
            "VALUES (:telegram_id, :access_token, :refresh_token, :expires_at)"
            "ON CONFLICT (telegram_id) DO UPDATE SET"
            " access_token = :access_token, refresh_token = :refresh_token, expires_at = :expires_at"
        ),
        user.dict(),
    )
    await session.commit()
    return "Authorization successful, page can be closed."
