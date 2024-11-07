from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from sqlmodel import select, true

from src.db import get_db_session
from src.models import User, UserAlerts
from src.yandex import YandexClient, get_yandex_client

scheduler = AsyncIOScheduler(timezone=utc)

monitor_smart_home_devices_period_seconds = 1


@scheduler.scheduled_job("interval", seconds=monitor_smart_home_devices_period_seconds)
async def monitor_smart_home_devices():
    # todo: generators are really hard to use there, because
    #  scheduler doesn't have DI framework like FastAPI using Depends
    #  for better code need to rewrite get_db_session, get_yandex_client to single object getter

    users_with_alerts = []
    async for session in get_db_session():
        users_with_alerts = await session.execute(
            select(User).join(UserAlerts).filter(UserAlerts.alerts_enabled.is_(true()))  # noqa
        )

    for yandex_client in get_yandex_client():
        for user in users_with_alerts.scalars():
            await monitor_user_smart_home_devices(user, yandex_client)


async def monitor_user_smart_home_devices(
    user: User,
    yandex_client: YandexClient,
):
    async for session in get_db_session():
        user_info = await yandex_client.get_smart_home_user_info(user.yandex_token)
        for device in user_info.devices:
            device_state = await yandex_client.get_device_state_info(device.id)

        # todo: update device state in the database, alert if it's changed
        # todo: send alert to user in telegram if device state is changed
