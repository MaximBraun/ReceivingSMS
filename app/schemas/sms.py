from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


class OnlineSimNewSmsPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    user_id: str
    country_code: str
    number: str  # номер, на который пришло СМС (наш to_number)
    sender: str  # имя/номер отправителя (наш from_number)
    message: str  # текст СМС
    time_start: str
    time_left: str
    operation_id: str
    webhook_type: str
    code: str  # SMS ID у OnlineSIM

    # вспомогательные свойства, если удобно
    @property
    def provider_message_id(self) -> str:
        return self.code

    @property
    def to_number(self) -> str:
        return self.number

    @property
    def from_number(self) -> str:
        return self.sender

    @property
    def text(self) -> str:
        return self.message


class SmsInDB(BaseModel):
    id: int
    provider_message_id: str
    from_number: str
    to_number: str
    text: str
    received_at: datetime
    status: str

    class Config:
        from_attributes = True


class SmsListItem(BaseModel):
    id: int
    provider_message_id: str
    from_number: str
    to_number: str
    text: str
    received_at: datetime
    status: str

    class Config:
        from_attributes = True


class SmsListResponse(BaseModel):
    items: list[SmsListItem]
    total: int
    limit: int
    offset: int