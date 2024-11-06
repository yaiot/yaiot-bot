from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.bot import bot
from src.handlers import auth

router = Router()

@router.message(Command("scenario"))
async def cmd_scenario(
        message: Message,
        command: CommandObject,
        is_yandex_authorized: bool
):
    if command.args is None:
        await message.answer(
            "Error: enter link ID"
        )
        return

    try:
        str_id = command.args.split(" ", maxsplit=0)
    except ValueError:
        await message.answer(
            "Error: wrong command format\n"
            "Correct format: /start <ID>"
        )
        return

    if not is_yandex_authorized:
        await message.answer(
            "Error: not authorized in yandex\n"
            f"Type '/{auth.__name__}' first"
        )

    link = f"https://t.me/{bot.id}?start={str_id}"

    await message.answer(
        "Your link:\n"
        f"<a href='{link}'>{link}</a>", parse_mode="HTML"
    )


@router.message(Command("scenarios"))
async def cmd_scenarios(
        message: Message,
        is_yandex_authorized: bool
):
    if not is_yandex_authorized:
        await message.answer(
            "Error: not authorized in yandex\n"
            f"Type '/{auth.__name__}' first"
        )

    await message.answer("Available scenarios:")
    # TODO: Вывести сценарии пользователя