from aiogram import Bot, Dispatcher
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import BotCommand, Message

from src.config import settings
from src.handlers import auth, scenarios, smart_home

dp = Dispatcher()
bot = Bot(token=settings.bot_token)
dp.include_routers(auth.router, scenarios.router, smart_home.router)


async def setup_bot_commands(bot: Bot):
    """
    Setup bot commands is used to make autocompletion in telegram,
    when user types '/' in chat.
    """

    await bot.set_my_commands(
        [
            # todo: @DenChika need to register all his commands over here
            BotCommand(command="/auth", description="Authorize in Yandex"),
            BotCommand(
                command="/home_info", description="Get information about your home"
            ),
        ]
    )


@dp.message(CommandStart(deep_link=True))
async def cmd_start(message: Message, command: CommandObject):
    await message.answer("Starting scenario...")
    # TODO: Достать токен из базы и запустить сценарий
