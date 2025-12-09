from fastapi import APIRouter

from app.api.v1 import twilio, sms

api_v1_router = APIRouter()
api_v1_router.include_router(sms.router)
api_v1_router.include_router(twilio.router)