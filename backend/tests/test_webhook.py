# tests/test_webhook.py
# Fixtures (setup_db, client) vêm do conftest.py — aplicados via @pytest.mark.usefixtures
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.usefixtures("setup_db")
def test_webhook_ignores_non_message_events(client):
    payload = {
        "event": "connection.update",
        "instance": "test",
        "data": {},
    }
    response = client.post("/webhook/uazapi", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}


@pytest.mark.usefixtures("setup_db")
def test_webhook_rejects_missing_fields(client):
    response = client.post("/webhook/uazapi", json={"event": "messages.upsert"})
    assert response.status_code == 422


@pytest.mark.usefixtures("setup_db")
@patch("app.routers.webhook.UazapiClient")
@patch("app.routers.webhook.ChatEngine")
def test_webhook_processes_message(mock_engine_cls, mock_uazapi_cls, client):
    mock_engine = MagicMock()
    mock_engine.process_message.return_value = ("Qual seu nome?", {})
    mock_engine.is_collection_complete.return_value = False
    mock_engine_cls.return_value = mock_engine

    mock_uazapi = MagicMock()
    mock_uazapi.send_text.return_value = True
    mock_uazapi_cls.return_value = mock_uazapi

    payload = {
        "event": "messages.upsert",
        "instance": "test",
        "data": {
            "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": False},
            "message": {"conversation": "Olá, quero dar entrada no divórcio"},
        },
    }
    response = client.post("/webhook/uazapi", json=payload)
    assert response.status_code == 200
    mock_uazapi.send_text.assert_called_once()
