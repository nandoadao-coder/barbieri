from pydantic import BaseModel
from typing import Any


class UazapiWebhookPayload(BaseModel):
    """Payload recebido do Uazapi quando chega uma mensagem."""
    event: str
    instance: str
    data: dict[str, Any]


class ChatMessageRequest(BaseModel):
    """Requisição do portal web para enviar mensagem."""
    session_token: str
    message: str


class ChatMessageResponse(BaseModel):
    response: str
    collection_complete: bool = False
    case_id: int | None = None
