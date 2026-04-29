from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

# Status: collecting -> pending_review -> approved -> delivered
CASE_STATUSES = ["collecting", "pending_review", "approved", "delivered"]
CASE_TYPES = ["divorce"]


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), default="divorce")
    status: Mapped[str] = mapped_column(String(50), default="collecting")
    complexity: Mapped[str | None] = mapped_column(String(20))  # simple | complex
    client_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clients.id"))
    lawyer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
