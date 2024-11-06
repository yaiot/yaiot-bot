from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.config import settings

router = Router()

@router.message(Command("auth"))
async def cmd_auth(message: Message):
    url = (
        "https://oauth.yandex.ru/authorize?response_type=code&"
        f"client_id={settings.yandex_client_id}&"
        f"redirect_uri={settings.yandex_redirect_uri}&"
        f"state={message.from_user.id}"
    )

    await message.answer(
        f"<a href='{url}'>Click here to authorize</a>", parse_mode="HTML"
    )