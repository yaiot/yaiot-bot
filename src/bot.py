from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandObject, CommandStart
from src.config import settings
from src.handlers import auth, scenarios
from src.middlewaries.auth_middleware import YandexAuthMiddleware

dp = Dispatcher()
bot = Bot(token=settings.bot_token)
dp.include_routers(auth.router, scenarios.router)
scenarios.router.message.middleware(YandexAuthMiddleware())

@dp.message(CommandStart(
    deep_link=True
))
async def cmd_start(
        message: Message,
        command: CommandObject
):
    await message.answer(f"Starting scenario...")
    # TODO: Достать токен из базы и запустить сценарий