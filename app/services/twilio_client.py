from typing import Any, Dict, AsyncGenerator

from twilio.rest import Client as TwilioClient
from fastapi import Depends

from app.core.config import Settings, get_settings


class TwilioService:
    """
    Сервис для работы с Twilio API.
    Использует синхронный Twilio SDK, но обернут для удобства.
    """
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = TwilioClient(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        )

    def get_account_balance(self) -> Dict[str, Any]:
        """
        Получает баланс аккаунта Twilio.
        """
        account = self._client.api.accounts(self._settings.twilio_account_sid).fetch()
        return {
            "account_sid": account.sid,
            "status": account.status,
            "type": account.type,
        }

    def send_sms(
        self,
        to: str,
        body: str,
        from_: str | None = None,
    ) -> Dict[str, Any]:
        """
        Отправляет SMS через Twilio.
        
        Args:
            to: номер получателя
            body: текст сообщения
            from_: номер отправителя (если не указан, используется twilio_phone_number из настроек)
        """
        from_number = from_ or self._settings.twilio_phone_number
        if not from_number:
            raise ValueError("Twilio phone number not configured")
        
        message = self._client.messages.create(
            body=body,
            from_=from_number,
            to=to,
        )
        
        return {
            "sid": message.sid,
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body,
        }


async def get_twilio_service(
    settings: Settings = Depends(get_settings),
) -> TwilioService:
    """
    Dependency для получения TwilioService.
    """
    return TwilioService(settings=settings)

