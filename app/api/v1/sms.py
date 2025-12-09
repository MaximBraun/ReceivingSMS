import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, Form
from typing import Annotated

from app.core.config import get_settings, Settings
from app.core.twilio_auth import validate_twilio_signature
from app.schemas.sms import (
    TwilioWebhookPayload,
    SmsInDB,
    SmsListItem,
    SmsListResponse,
)
from app.services.sms_service import SmsService, get_sms_service


logger = logging.getLogger("app.api.sms")


router = APIRouter(prefix="/api/v1", tags=["sms"])


@router.post(
    "/webhooks/twilio/sms",
    response_model=SmsInDB,
    status_code=status.HTTP_201_CREATED,
)
async def twilio_sms_webhook(
    request: Request,
    MessageSid: Annotated[str, Form()],
    AccountSid: Annotated[str, Form()],
    From: Annotated[str, Form()],
    To: Annotated[str, Form()],
    Body: Annotated[str, Form()],
    NumMedia: Annotated[str, Form()] = "0",
    MessageStatus: Annotated[str | None, Form()] = None,
    SmsStatus: Annotated[str | None, Form()] = None,
    SmsSid: Annotated[str | None, Form()] = None,
    SmsMessageSid: Annotated[str | None, Form()] = None,
    settings: Settings = Depends(get_settings),
    sms_service: SmsService = Depends(get_sms_service),
) -> SmsInDB:
    """
    Webhook endpoint для приема входящих SMS от Twilio.
    
    Twilio отправляет данные в формате application/x-www-form-urlencoded.
    """
    # Собираем все form-параметры для валидации подписи
    form_data = {
        "MessageSid": MessageSid,
        "AccountSid": AccountSid,
        "From": From,
        "To": To,
        "Body": Body,
        "NumMedia": NumMedia,
    }
    if MessageStatus:
        form_data["MessageStatus"] = MessageStatus
    if SmsStatus:
        form_data["SmsStatus"] = SmsStatus
    if SmsSid:
        form_data["SmsSid"] = SmsSid
    if SmsMessageSid:
        form_data["SmsMessageSid"] = SmsMessageSid
    
    # Валидируем подпись Twilio
    await validate_twilio_signature(request, form_data, settings)
    
    # Создаем payload объект
    payload = TwilioWebhookPayload(
        MessageSid=MessageSid,
        AccountSid=AccountSid,
        From=From,
        To=To,
        Body=Body,
        NumMedia=NumMedia,
        MessageStatus=MessageStatus,
        SmsStatus=SmsStatus,
        SmsSid=SmsSid,
        SmsMessageSid=SmsMessageSid,
    )
    
    logger.info(
        "Received Twilio SMS webhook",
        extra={
            "message_sid": payload.MessageSid,
            "from": payload.From,
            "to": payload.To,
        },
    )
    
    sms = await sms_service.save_incoming_sms(
        payload=payload,
        raw_payload=payload.model_dump(),
    )
    return SmsInDB.model_validate(sms)


@router.get("/sms/{sms_id}", response_model=SmsInDB)
async def get_sms(
    sms_id: int,
    sms_service: SmsService = Depends(get_sms_service),
) -> SmsInDB:
    sms = await sms_service.get_sms_by_id(sms_id)
    if not sms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SMS not found")
    return SmsInDB.model_validate(sms)


@router.get("/sms", response_model=SmsListResponse)
async def get_sms_list(
    sms_service: SmsService = Depends(get_sms_service),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    from_number: str | None = Query(None),
    to_number: str | None = Query(None),
) -> SmsListResponse:
    items, total = await sms_service.list_sms(
        limit=limit,
        offset=offset,
        from_number=from_number,
        to_number=to_number,
    )
    return SmsListResponse(
        items=[SmsListItem.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )