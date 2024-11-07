import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from sqlmodel import select, true

from src.bot import Bot, get_telegram_client
from src.db import get_db_session
from src.models import Device, User, UserAlerts, UserDevices
from src.yandex import YandexClient, YandexIoTException, get_yandex_client

scheduler = AsyncIOScheduler(timezone=utc)

monitor_smart_home_devices_state_changes_period = 15
monitor_smart_home_devices_changes_period = 60


@scheduler.scheduled_job(
    "interval", seconds=monitor_smart_home_devices_state_changes_period
)
async def monitor_smart_home_devices_state_changes():
    """
    Monitor smart home devices state changes (for now is online/offline state only, but
    it can be extended to other states like low battery, etc.).

    The function gets all users, which have alerts enabled, and comparing already saved
    devices states with the current states. If the state is changed, the function sends
    an alert to the user in the telegram and updates the device state in the database.
    """

    users_with_alerts = []
    async for session in get_db_session():
        users_with_alerts = await session.execute(
            select(User).join(UserAlerts).filter(UserAlerts.alerts_enabled.is_(true()))  # noqa
        )

    # todo: generators are really hard to use there, because
    #  we doesn't have DI framework like FastAPI using Depends
    #  for better code need to rewrite get_yandex_client, get_telegram_client to
    #  single object getter
    for yandex_client in get_yandex_client():
        for tg_client in get_telegram_client():
            for user in users_with_alerts.scalars():
                await monitor_user_smart_home_devices(user, yandex_client, tg_client)


async def monitor_user_smart_home_devices(
    user: User,
    yandex_client: YandexClient,
    bot: Bot,
):
    user_devices: Optional[UserDevices] = None
    async for session in get_db_session():
        user_devices = (
            (
                await session.execute(
                    select(UserDevices).filter_by(telegram_id=user.telegram_id)
                )
            )
            .scalars()
            .first()
        )

    if user_devices is None:
        logging.warning(
            f"user {user.telegram_id} has no devices in the database, waiting for the next update"
        )
        return

    changed_devices = []
    for db_device_state in user_devices.devices:
        try:
            yandex_device_state = await yandex_client.get_device_state_info(
                user.access_token, db_device_state.id
            )
        except YandexIoTException as e:
            logging.error(f"error getting device state: {e.message}")
            continue

        if yandex_device_state.state != db_device_state.state:
            db_device_state.state = yandex_device_state.state
            changed_devices.append(db_device_state)

    if not changed_devices:
        logging.debug(f"user {user.telegram_id} has no changed devices")
        return

    logging.info(f"user {user.telegram_id} has changed devices: {changed_devices}")
    async for session in get_db_session():
        await session.merge(user_devices)
        await session.commit()

    for device in changed_devices:
        logging.debug(
            f"sending alert to user {user.telegram_id} about device {device.name}"
        )
        await bot.send_message(
            user.telegram_id, f"Device {device.name} changed state to {device.state}"
        )


@scheduler.scheduled_job("interval", seconds=monitor_smart_home_devices_changes_period)
async def monitor_smart_home_devices_changes():
    """
    Monitor smart home devices changes updates the list of the user's
    devices in the database, because some of them can be added or removed.

    The function gets all users, which have alerts enabled, and atomically updates
    the list of devices in the database.
    """

    users_with_alerts = []
    async for session in get_db_session():
        users_with_alerts = await session.execute(
            select(User).join(UserAlerts).filter(UserAlerts.alerts_enabled.is_(true()))  # noqa
        )

    for yandex_client in get_yandex_client():
        for user in users_with_alerts.scalars():
            user_info = await yandex_client.get_smart_home_user_info(user.access_token)
            async for session in get_db_session():
                user_devices = UserDevices(
                    telegram_id=user.telegram_id,
                    devices=[
                        Device(id=d.id, name=d.name, state=d.state)
                        for d in user_info.devices
                    ],
                )
                await session.merge(user_devices)
                await session.commit()
