# tests/test_uazapi.py
from unittest.mock import patch, MagicMock
from app.services.uazapi import UazapiClient


@patch("app.services.uazapi.httpx.post")
def test_send_text_message_success(mock_post):
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"status": "ok"})
    client = UazapiClient()
    result = client.send_text(phone="5511999999999", message="Olá!")
    assert result is True
    mock_post.assert_called_once()


@patch("app.services.uazapi.httpx.post")
def test_send_text_message_failure(mock_post):
    mock_post.return_value = MagicMock(status_code=500, json=lambda: {"error": "fail"})
    client = UazapiClient()
    result = client.send_text(phone="5511999999999", message="Olá!")
    assert result is False


@patch("app.services.uazapi.httpx.post")
def test_send_document_success(mock_post):
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"status": "ok"})
    client = UazapiClient()
    result = client.send_document(
        phone="5511999999999",
        file_url="https://example.com/peticao.pdf",
        filename="peticao.pdf",
    )
    assert result is True
