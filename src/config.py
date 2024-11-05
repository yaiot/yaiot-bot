import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    host: str = "0.0.0.0"
    port: int = 8080
    db_host: str = "sqlite+aiosqlite:///database.db"
    yandex_client_id: str = "60e9bdeac7b14dec88b22343559bab87"
    yandex_client_secret: str
    yandex_redirect_uri: str = "http://localhost:8080/auth/yandex/callback"

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False


logging.basicConfig(level=logging.INFO)

settings = Settings()
