from datetime import datetime
from typing import Any

from sqlalchemy import String, Text, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SMS(Base):
    __tablename__ = "incoming_sms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider_message_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    from_number: Mapped[str] = mapped_column(String(32), index=True)
    to_number: Mapped[str] = mapped_column(String(32), index=True)
    text: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
    )
    status: Mapped[str] = mapped_column(String(32), default="received", index=True)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )