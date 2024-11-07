from aiogram import Bot, Dispatcher
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import BotCommand, Message

from src.config import settings
from src.handlers import auth, links, scenarios
from src.yandex import YandexIoTException, get_yandex_client

dp = Dispatcher()
bot = Bot(token=settings.bot_token)
dp.include_routers(auth.router, scenarios.router, links.router)


async def setup_bot_commands(bot: Bot):
    """
    Setup bot commands is used to make autocompletion in telegram,
    when user types '/' in chat.
    """

    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Run scenario of your home by ID"),
            BotCommand(command="/auth", description="Authorize in Yandex"),
            BotCommand(
                command="/all_scenarios", description="Get all scenarios of your home"
            ),
            BotCommand(
                command="/scenario",
                description="Generate link to run scenario of your home",
            ),
            BotCommand(command="/links", description="Get all user's links to share"),
            BotCommand(command="/revoke_link", description="Revoke link by ID"),
        ]
    )


@dp.message(CommandStart(deep_link=True))
async def cmd_start_scenario(message: Message, command: CommandObject):
    await message.answer("Starting scenario...")
    # TODO: Достать токен из базы

    access_token = "fdkjlfdjdl"  # Заглушка
    scenario_id = command.args

    for yandex_client in get_yandex_client():
        await message.answer(f"Running scenario {scenario_id}...")

        try:
            await yandex_client.run_scenario(scenario_id, access_token)
        except YandexIoTException as e:
            await message.answer(f"Error: {e.message}")
            return

        await message.answer(f"Scenario {scenario_id} has completed successfully!")
