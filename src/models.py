import json
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel, TypeDecorator


class User(SQLModel, table=True):
    telegram_id: int = Field(primary_key=True)
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: int


class UserAlerts(SQLModel, table=True):
    telegram_id: int = Field(primary_key=True, foreign_key="user.telegram_id")
    alerts_enabled: bool = Field(default=True)


class Device(SQLModel, table=False):
    id: str
    name: str
    state: str


class DeviceJSON(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        if isinstance(value, list):
            return json.dumps(
                [item.dict() if hasattr(item, "dict") else item for item in value]
            )

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return [Device(**item) for item in json.loads(value)]

        return value


class UserDevices(SQLModel, table=True):
    telegram_id: int = Field(primary_key=True, foreign_key="user.telegram_id")
    devices: List[Device] = Field(sa_column=Column(DeviceJSON), default=[])
