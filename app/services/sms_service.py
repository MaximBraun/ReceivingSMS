import logging
from typing import Any

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.models.sms import SMS
from app.schemas.sms import TwilioWebhookPayload

logger = logging.getLogger("app.sms_service")

class SmsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_incoming_sms(
        self,
        payload: TwilioWebhookPayload,
        raw_payload: dict[str, Any],
    ) -> SMS:
        logger.info(
            "Saving incoming SMS",
            extra={
                "provider_message_id": payload.provider_message_id,
                "from_number": payload.from_number,
                "to_number": payload.to_number,
            },
        )
        provider_id: str = payload.provider_message_id

        stmt = select(SMS).where(SMS.provider_message_id == provider_id)
        result = await self.db.execute(stmt)
        existing: SMS | None = result.scalar_one_or_none()
        if existing:
            return existing

        sms = SMS(
            provider_message_id=provider_id,
            from_number=payload.from_number,
            to_number=payload.to_number,
            text=payload.text,
            raw_payload=raw_payload,
        )

        self.db.add(sms)
        await self.db.commit()
        await self.db.refresh(sms)
        return sms

    async def get_sms_by_id(self, sms_id: int) -> SMS | None:
        result = await self.db.execute(select(SMS).where(SMS.id == sms_id))
        return result.scalar_one_or_none()

    async def list_sms(
        self,
        limit: int = 50,
        offset: int = 0,
        from_number: str | None = None,
        to_number: str | None = None,
    ) -> tuple[list[SMS], int]:
        stmt = select(SMS).order_by(SMS.received_at.desc())
        count_stmt = select(func.count()).select_from(SMS)

        if from_number:
            stmt = stmt.where(SMS.from_number == from_number)
            count_stmt = count_stmt.where(SMS.from_number == from_number)
        if to_number:
            stmt = stmt.where(SMS.to_number == to_number)
            count_stmt = count_stmt.where(SMS.to_number == to_number)

        total = (await self.db.execute(count_stmt)).scalar_one()
        result = await self.db.execute(stmt.limit(limit).offset(offset))
        items = result.scalars().all()
        return list(items), total


def get_sms_service(
    db: AsyncSession = Depends(get_db_session),
) -> SmsService:
    return SmsService(db=db)