from fastapi import Request, HTTPException, status, Form
from twilio.request_validator import RequestValidator

from app.core.config import Settings, get_settings


async def validate_twilio_signature(
    request: Request,
    form_data: dict,
    settings: Settings,
) -> None:
    """
    Валидирует подпись Twilio webhook через X-Twilio-Signature.
    
    Twilio использует HMAC-SHA1 для подписи запроса.
    """
    validator = RequestValidator(settings.twilio_auth_token)
    
    # Получаем подпись из заголовка
    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Twilio-Signature header",
        )
    
    # Получаем URL запроса (без query параметров для валидации)
    url = str(request.url).split('?')[0]
    
    # Валидируем подпись
    is_valid = validator.validate(url, form_data, signature)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Twilio signature",
        )

