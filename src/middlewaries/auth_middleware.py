from typing import Callable, Dict, Any, Awaitable, Annotated
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select

from src.db import get_db_session
from src.models import User


class YandexAuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        session = get_db_session()

        user = data["event_from_user"]
        result = await session.execute(select(User).filter_by(telegram_id=user.id))
        await session.commit()

        data["is_yandex_authorized"] = result is not None

        return await handler(event, data)