from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


class TwilioWebhookPayload(BaseModel):
    """
    Payload от Twilio webhook (form-data формат).
    Twilio отправляет данные как application/x-www-form-urlencoded.
    """
    model_config = ConfigDict(extra="allow")

    # Основные поля из Twilio webhook
    MessageSid: str  # уникальный ID сообщения (наш provider_message_id)
    AccountSid: str
    From: str  # номер отправителя (наш from_number)
    To: str  # номер получателя (наш Twilio номер, to_number)
    Body: str  # текст сообщения (наш text)
    
    # Дополнительные поля (опциональные, но часто присутствуют)
    NumMedia: str = "0"  # количество медиа-файлов
    MessageStatus: str | None = None
    SmsStatus: str | None = None
    SmsSid: str | None = None
    SmsMessageSid: str | None = None

    # Вспомогательные свойства для совместимости с сервисом
    @property
    def provider_message_id(self) -> str:
        return self.MessageSid

    @property
    def to_number(self) -> str:
        return self.To

    @property
    def from_number(self) -> str:
        return self.From

    @property
    def text(self) -> str:
        return self.Body


class SmsInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    provider_message_id: str
    from_number: str
    to_number: str
    text: str
    received_at: datetime
    status: str


class SmsListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    provider_message_id: str
    from_number: str
    to_number: str
    text: str
    received_at: datetime
    status: str


class SmsListResponse(BaseModel):
    items: list[SmsListItem]
    total: int
    limit: int
    offset: int