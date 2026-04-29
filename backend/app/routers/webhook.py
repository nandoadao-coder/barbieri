from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import UazapiWebhookPayload
from app.services.chat_engine import ChatEngine
from app.services.uazapi import UazapiClient
from app.models.client import Client
from app.models.case import Case
from app.models.case_data import CaseData
from app.models.chat_session import ChatSession
from app.services.case_classifier import classify_case

router = APIRouter(prefix="/webhook", tags=["webhook"])


def _get_or_create_session(db: Session, phone: str) -> tuple[ChatSession, Client, Case]:
    """Busca ou cria sessão, cliente e caso para um número de telefone."""
    session = db.query(ChatSession).filter(
        ChatSession.channel == "whatsapp",
        ChatSession.channel_id == phone,
        ChatSession.case_id.isnot(None),
    ).order_by(ChatSession.created_at.desc()).first()

    if session:
        case = db.query(Case).filter(Case.id == session.case_id).first()
        client = db.query(Client).filter(Client.id == session.client_id).first()
        return session, client, case

    # Criar novo cliente, caso e sessão
    client = Client(phone=phone, channel="whatsapp")
    db.add(client)
    db.flush()

    case = Case(type="divorce", status="collecting", client_id=client.id)
    db.add(case)
    db.flush()

    case_data = CaseData(case_id=case.id, data={})
    db.add(case_data)
    db.flush()

    session = ChatSession(
        case_id=case.id,
        client_id=client.id,
        channel="whatsapp",
        channel_id=phone,
        history=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    db.refresh(case)
    db.refresh(client)
    return session, client, case


@router.post("/uazapi")
def uazapi_webhook(payload: UazapiWebhookPayload, db: Session = Depends(get_db)):
    # Ignora eventos que não são mensagens
    if payload.event != "messages.upsert":
        return {"status": "ignored"}

    data = payload.data
    key = data.get("key", {})

    # Ignora mensagens enviadas pelo próprio bot
    if key.get("fromMe"):
        return {"status": "ignored"}

    remote_jid = key.get("remoteJid", "")
    phone = remote_jid.replace("@s.whatsapp.net", "").replace("@c.us", "")

    message_content = data.get("message", {})
    user_text = (
        message_content.get("conversation")
        or message_content.get("extendedTextMessage", {}).get("text")
        or ""
    )

    if not user_text:
        return {"status": "ignored"}

    session, client, case = _get_or_create_session(db, phone)

    # Buscar dados já coletados
    case_data_obj = db.query(CaseData).filter(CaseData.case_id == case.id).first()
    collected_data = case_data_obj.data if case_data_obj else {}

    # Processar com o chat engine
    engine = ChatEngine()
    response_text, updated_data = engine.process_message(
        user_message=user_text,
        history=session.history,
        collected_data=collected_data,
    )

    # Atualizar histórico e dados
    new_history = session.history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response_text},
    ]
    session.history = new_history
    db.add(session)

    if case_data_obj:
        case_data_obj.data = updated_data
        db.add(case_data_obj)

    # Verificar se coleta completou
    if engine.is_collection_complete(updated_data):
        complexity = classify_case(updated_data)
        case.status = "pending_review"
        case.complexity = complexity
        db.add(case)

    db.commit()

    # Enviar resposta via WhatsApp
    uazapi = UazapiClient()
    uazapi.send_text(phone=phone, message=response_text)

    return {"status": "processed"}
