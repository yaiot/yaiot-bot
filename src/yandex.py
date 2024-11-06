import typing
from dataclasses import dataclass
from typing import Generator

import httpx
from pydantic import BaseModel

from src.config import settings


class YandexException(Exception):
    pass


@dataclass
class YandexOAuthException(YandexException):
    error: str
    error_description: str


@dataclass
class YandexIoTException(YandexException):
    request_id: str
    status: str
    message: str


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class Device(BaseModel):
    id: str
    name: str
    type: str
    state: str


class SmartHomeUserInfo(BaseModel):
    status: str
    request_id: str
    devices: typing.List[Device]


class YandexClient:
    def __init__(self, yandex_client_id: str, yandex_client_secret: str):
        self.yandex_client_id = yandex_client_id
        self.yandex_client_secret = yandex_client_secret
        self.c = httpx.AsyncClient()

    async def exchange_code_for_data(
        self,
        code: str,
    ) -> TokenData:
        """
        Exchange the authorization code for an access token.
        https://yandex.ru/dev/id/doc/ru/codes/code-url#token

        :param code: authorization code, which is used to get the access token.
        :return: access token.
        """

        response = await self.c.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.yandex_client_id,
                "client_secret": self.yandex_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise YandexOAuthException(**response.json())

        return TokenData(**response.json())

    async def get_smart_home_user_info(
        self,
        access_token: str,
    ) -> SmartHomeUserInfo:
        """
        Get information about the user's devices in the smart home.
        https://yandex.ru/dev/dialogs/smart-home/doc/ru/concepts/platform-user-info

        :param access_token: personal access token of the user.
        :return: information about the user's devices in the smart home.
        """

        response = await self.c.get(
            "https://api.iot.yandex.net/v1.0/user/info",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            raise YandexIoTException(**response.json())

        return SmartHomeUserInfo(**response.json())


yandex_client = YandexClient(settings.yandex_client_id, settings.yandex_client_secret)


def get_yandex_client() -> Generator[YandexClient, None, None]:
    yield yandex_client
