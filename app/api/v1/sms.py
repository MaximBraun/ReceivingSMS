import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import get_settings, Settings
from app.schemas.sms import (
    OnlineSimNewSmsPayload,
    SmsInDB,
    SmsListItem,
    SmsListResponse,
)
from app.services.sms_service import SmsService, get_sms_service


logger = logging.getLogger("app.api.sms")


router = APIRouter(prefix="/api/v1", tags=["sms"])


def verify_webhook_token(
    token: str = Query(..., alias="token"),
    settings: Settings = Depends(get_settings),
) -> None:
    if token != settings.webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook token",
        )


@router.post(
    "/webhooks/onlinesim/new-sms",
    response_model=SmsInDB,
    status_code=status.HTTP_201_CREATED,
)
async def onlinesim_new_sms_webhook(
    payload: OnlineSimNewSmsPayload,
    _: None = Depends(verify_webhook_token),
    sms_service: SmsService = Depends(get_sms_service),
) -> SmsInDB:
    logger.info(
        "Received OnlineSIM webhook",
        extra={
            "operation_id": payload.operation_id,
            "number": payload.number,
            "sender": payload.sender,
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