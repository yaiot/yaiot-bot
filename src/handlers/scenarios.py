from typing import Optional

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.middlewaries.auth_middleware import YandexAuthMiddleware
from src.models import User
from src.yandex import YandexIoTException, get_yandex_client

router = Router()
router.message.middleware(YandexAuthMiddleware())


@router.message(Command("scenario"))
async def cmd_scenario(
    message: Message,
    command: CommandObject,
    user: Optional[User],
):
    if command.args is None:
        await message.answer("Please provide scenario ID.\n" "Example: /scenario 12345")
        return

    args = command.args.split(" ")

    if len(args) > 1:
        await message.answer("Wrong command format\n" "Correct format: /scenario <id>")
        return

    id = args[0]

    if user is None:
        await message.answer("You aren't registered at system. Please, type /auth")
        return

    link = f"https://t.me/yaiot-bot?start={id}"

    # TODO: Сохранить ссылку или id в базу

    await message.answer(
        "Your link:\n" f"<a href='{link}'>{link}</a>", parse_mode="HTML"
    )


@router.message(Command("all_scenarios"))
async def cmd_all_scenarios(
    message: Message,
    user: Optional[User],
):
    if user is None:
        await message.answer("You aren't registered at system. Please, type /auth")

    for yandex_client in get_yandex_client():
        try:
            smart_home_info = await yandex_client.get_smart_home_user_info(
                user.access_token
            )
        except YandexIoTException as e:
            await message.answer(f"Error: {e.message}")
            return

        if len(smart_home_info.scenarios) == 0:
            await message.answer("You have no available scenarios in your smart home")
            return

        response = "Available scenarios:\n\n"

        for scenario in smart_home_info.scenarios:
            response += (
                f"id: {scenario.id}\n"
                f"name: {scenario.name}\n"
                f"is_active: {scenario.is_active}\n\n"
            )

        await message.answer(response)
