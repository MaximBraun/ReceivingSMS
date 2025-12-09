from typing import Any

from fastapi import APIRouter, Depends

from app.services.onlinesim_client import OnlineSimClient, get_onlinesim_client



router = APIRouter(prefix="/api/v1/onlinesim", tags=["onlinesim"])


@router.get("/info")
async def get_onlinesim_info(
    client: OnlineSimClient = Depends(get_onlinesim_client),
) -> dict[str, Any]:
    """
    Возвращает сырое содержимое OnlineSIM /info (для отладки и мониторинга).
    """
    return await client.get_info()