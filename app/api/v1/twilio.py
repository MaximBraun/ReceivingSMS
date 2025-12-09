from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel

from app.services.twilio_client import TwilioService, get_twilio_service


router = APIRouter(prefix="/api/v1/twilio", tags=["twilio"])


class SendSmsRequest(BaseModel):
    to: str
    body: str
    from_: str | None = None


@router.get("/account")
async def get_twilio_account(
    service: TwilioService = Depends(get_twilio_service),
) -> Dict[str, Any]:
    """
    Получает информацию об аккаунте Twilio.
    """
    return service.get_account_balance()


@router.post("/sms/send")
async def send_sms(
    request: SendSmsRequest,
    service: TwilioService = Depends(get_twilio_service),
) -> Dict[str, Any]:
    """
    Отправляет SMS через Twilio.
    """
    try:
        result = service.send_sms(
            to=request.to,
            body=request.body,
            from_=request.from_,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS: {str(e)}",
        )

