import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services.chat_engine import ChatEngine
from app.services.case_classifier import classify_case
from app.models.client import Client
from app.models.case import Case
from app.models.case_data import CaseData
from app.models.chat_session import ChatSession

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_or_create_web_session(db: Session, session_token: str) -> tuple[ChatSession, Client, Case]:
    session = db.query(ChatSession).filter(
        ChatSession.channel == "web",
        ChatSession.channel_id == session_token,
    ).first()

    if session:
        case = db.query(Case).filter(Case.id == session.case_id).first()
        client = db.query(Client).filter(Client.id == session.client_id).first()
        return session, client, case

    client = Client(channel="web")
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
        channel="web",
        channel_id=session_token,
        history=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    db.refresh(case)
    db.refresh(client)
    return session, client, case


@router.post("/session")
def create_session():
    """Gera um token de sessão para o portal web."""
    return {"session_token": str(uuid.uuid4())}


@router.post("/message", response_model=ChatMessageResponse)
def send_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    session, client, case = _get_or_create_web_session(db, request.session_token)

    case_data_obj = db.query(CaseData).filter(CaseData.case_id == case.id).first()
    collected_data = case_data_obj.data if case_data_obj else {}

    engine = ChatEngine()
    response_text, updated_data = engine.process_message(
        user_message=request.message,
        history=session.history,
        collected_data=collected_data,
    )

    new_history = session.history + [
        {"role": "user", "content": request.message},
        {"role": "assistant", "content": response_text},
    ]
    session.history = new_history
    db.add(session)

    if case_data_obj:
        case_data_obj.data = updated_data
        db.add(case_data_obj)

    collection_complete = engine.is_collection_complete(updated_data)
    if collection_complete:
        complexity = classify_case(updated_data)
        case.status = "pending_review"
        case.complexity = complexity
        db.add(case)

    db.commit()

    return ChatMessageResponse(
        response=response_text,
        collection_complete=collection_complete,
        case_id=case.id if collection_complete else None,
    )
