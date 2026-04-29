from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cases.id"))
    client_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clients.id"))
    channel: Mapped[str] = mapped_column(String(20))  # whatsapp | web
    channel_id: Mapped[str | None] = mapped_column(String(100))  # phone number or session token
    history: Mapped[list] = mapped_column(JSONB, default=list)  # [{role, content}]
    current_step: Mapped[str | None] = mapped_column(String(100))  # qual dado está coletando
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
