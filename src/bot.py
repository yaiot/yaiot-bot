from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from src.config import settings

dp = Dispatcher()
bot = Bot(token=settings.bot_token)


@dp.message(Command("auth"))
async def cmd_auth(message: types.Message):
    url = (
        "https://oauth.yandex.ru/authorize?response_type=code&"
        f"client_id={settings.yandex_client_id}&"
        f"redirect_uri={settings.yandex_redirect_uri}&"
        f"state={message.from_user.id}"
    )

    await message.answer(
        f"<a href='{url}'>Click here to authorize</a>", parse_mode="HTML"
    )
