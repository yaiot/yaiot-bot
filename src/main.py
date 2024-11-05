import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False


logging.basicConfig(level=logging.INFO)
settings = Settings()

bot = Bot(token=settings.bot_token)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
