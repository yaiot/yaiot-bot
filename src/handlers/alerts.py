from enum import Enum
from typing import Optional

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlmodel import text

from src.db import get_db_session
from src.middlewaries.auth_middleware import YandexAuthMiddleware
from src.models import User, UserAlerts

router = Router()
router.message.middleware(YandexAuthMiddleware())


class AlertsOption(Enum):
    ENABLE = "enable"
    DISABLE = "disable"


@router.message(Command("alerts"))
async def cmd_manage_alerts(
    message: Message, command: CommandObject, user: Optional[User]
):
    args_split = [] if command.args is None else command.args.split(" ")
    option = AlertsOption(args_split[0]) if args_split else AlertsOption.ENABLE

    if option not in [AlertsOption.ENABLE, AlertsOption.DISABLE]:
        await message.answer(
            "Invalid option. Please, use /alerts enable or /alerts disable"
        )
        return

    if user is None:
        await message.answer("You aren't registered at system. Please, type /auth")
        return

    async for session in get_db_session():
        user_alerts = UserAlerts(
            telegram_id=user.telegram_id, alerts_enabled=option == AlertsOption.ENABLE
        )

        await session.execute(
            text(
                "INSERT INTO useralerts (telegram_id, alerts_enabled) "
                "VALUES (:telegram_id, :alerts_enabled) "
                "ON CONFLICT (telegram_id) DO UPDATE SET alerts_enabled = EXCLUDED.alerts_enabled"
            ),
            user_alerts.dict(),
        )
        await session.commit()

    await message.answer(f"Alerts have been {option.value}d")
