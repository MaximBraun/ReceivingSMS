import logging
import uuid

from fastapi import Request

logger = logging.getLogger("app.request")


class RequestIdMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        scope["request_id"] = request_id  # можно использовать в логгере, если нужно

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"x-request-id", request_id.encode()))
            await send(message)

        logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "request_id": request_id,
            },
        )

        response = await self.app(scope, receive, send_wrapper)
        return response