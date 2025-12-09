from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import unhandled_exception_handler
from app.api.v1 import api_v1_router
from app.core.config import get_settings, Settings
from app.core.db import get_db_session
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    setup_logging()
    _ = get_settings()
    yield


app = FastAPI(
    title="Receiving SMS Service", 
    version="0.1.0", 
    lifespan=lifespan
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_v1_router)


app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/health", tags=["health"])
async def health_check(
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db_session)
):
    return {
        "status": "ok", 
        "settings": settings.app_env,
        "db_connected": db is not None,
    }
