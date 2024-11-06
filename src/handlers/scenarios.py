from typing import Optional

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.middlewaries.auth_middleware import YandexAuthMiddleware
from src.models import User

router = Router()
router.message.middleware(YandexAuthMiddleware())


@router.message(Command("scenario"))
async def cmd_scenario(
    message: Message,
    command: CommandObject,
    user: Optional[User],
):
    if command.args is None:
        await message.answer("Error: enter link ID")
        return

    try:
        str_id = command.args.split(" ", maxsplit=0)
    except ValueError:
        await message.answer(
            "Error: wrong command format\n" "Correct format: /start <ID>"
        )
        return

    if user is None:
        await message.answer("You aren't registered at system. Please, type /auth")

    link = f"https://t.me/{message.bot.id}?start={str_id}"

    await message.answer(
        "Your link:\n" f"<a href='{link}'>{link}</a>", parse_mode="HTML"
    )


@router.message(Command("scenarios"))
async def cmd_scenarios(
    message: Message,
    user: Optional[User],
):
    if user is None:
        await message.answer("You aren't registered at system. Please, type /auth")

    await message.answer("Available scenarios:")
    # TODO: Вывести сценарии пользователя
