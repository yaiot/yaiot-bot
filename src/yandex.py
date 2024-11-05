import httpx
from pydantic import BaseModel

from src.config import settings


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


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

        response.raise_for_status()
        return TokenData(**response.json())


yandex_client = YandexClient(settings.yandex_client_id, settings.yandex_client_secret)


async def get_yandex_client() -> YandexClient:
    yield yandex_client
