from typing import Optional

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.middlewaries.auth_middleware import YandexAuthMiddleware
from src.models import User
from src.yandex import YandexIoTException, get_yandex_client

router = Router()
router.message.middleware(YandexAuthMiddleware())


# todo: following command need to be rewritten to the alerts configuration
#  for smart home devices, for now just testing the Yandex IoT API to get the user info
@router.message(Command("home_info"))
async def cmd_home_info(message: Message, user: Optional[User]):
    if user is None:
        await message.answer("You aren't registered at system. Please, type /auth")
        return

    # todo: generators are really hard to use there, because
    #  aiogram doesn't have DI framework like FastAPI using Depends
    #  for better code need to rewrite get_yandex_client to single object getter
    for yandex_client in get_yandex_client():
        try:
            smart_home_info = await yandex_client.get_smart_home_user_info(
                user.access_token
            )
        except YandexIoTException as e:
            await message.answer(f"Error: {e.message}")
            return

        response = (
            "Home info:\n\n"
            f"request_id: {smart_home_info.request_id}\n"
            f"status: {smart_home_info.status}\n"
            "devices:\n"
        )

        for device in smart_home_info.devices:
            response += (
                f"id: {device.id}\n"
                f"name: {device.name}\n"
                f"type: {device.type}\n"
            )

        response += "scenarios:\n"

        for scenario in smart_home_info.scenarios:
            response += (
                f"id: {scenario.id}\n"
                f"name: {scenario.name}\n"
                f"is_active: {scenario.is_active}\n\n"
            )

        await message.answer(response)
