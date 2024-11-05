import asyncio
import signal

from src.bot import bot, dp
from src.server import server
from src.yandex import yandex_client


async def start_bot_polling():
    await dp.start_polling(bot)


async def start_server():
    await server.serve()


async def shutdown(_):
    await dp.stop_polling()
    await server.shutdown()
    await yandex_client.close()


async def main():
    # kind-a graceful shutdown, but it's not working properly for some reason
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s)))

    await asyncio.gather(start_server(), start_bot_polling())


if __name__ == "__main__":
    asyncio.run(main())
