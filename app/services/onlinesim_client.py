from typing import Any, Dict, AsyncGenerator

import httpx
from fastapi import Depends

from app.core.config import Settings, get_settings


class OnlineSimClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.onlinesim_api_base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=10.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    def _auth_params(self) -> Dict[str, Any]:
        return {"apikey": self._settings.onlinesim_api_key}

    async def get_info(self) -> Dict[str, Any]:
        resp = await self._client.get("/api/getBalance.php", params=self._auth_params())
        resp.raise_for_status()
        return resp.json()


async def get_onlinesim_client(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[OnlineSimClient, None]:
    client = OnlineSimClient(settings=settings)
    try:
        yield client
    finally:
        await client.close()