from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    telegram_id: int = Field(primary_key=True)
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: int
