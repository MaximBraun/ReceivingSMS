import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

logger = logging.getLogger("app.errors")


async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = request.headers.get("x-request-id") or getattr(request.state, "request_id", None)

    logger.exception(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )