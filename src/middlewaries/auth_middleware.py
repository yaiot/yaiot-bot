from typing import Any, Awaitable, Callable, Dict

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
        # todo: generators are really hard to use there, because
        #  aiogram doesn't have DI framework like FastAPI using Depends
        #  for better code need to rewrite get_db_session to single object getter
        async for session in get_db_session():
            tg_user = data.get("event_from_user")
            result = await session.execute(
                select(User).filter_by(telegram_id=tg_user.id)
            )
            data["user"] = result.scalars().first()

        return await handler(event, data)
