import pytest

from app.core.config import get_settings


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_webhook_creates_sms(client):
    settings = get_settings()

    payload = {
        "user_id": "u1",
        "country_code": "7",
        "number": "+70000000000",
        "sender": "BANK",
        "message": "Your code 1234",
        "time_start": "2025-01-01T12:00:00Z",
        "time_left": "300",
        "operation_id": "op-1",
        "webhook_type": "receiving_sms",
        "code": "sms-test-1",
    }

    resp = await client.post(
        f"/api/v1/webhooks/onlinesim/new-sms?token={settings.webhook_secret}",
        json=payload,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["provider_message_id"] == "sms-test-1"
    assert data["to_number"] == "+70000000000"
    assert data["from_number"] == "BANK"

    # список
    list_resp = await client.get("/api/v1/sms?limit=10")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(i["provider_message_id"] == "sms-test-1" for i in list_data["items"])