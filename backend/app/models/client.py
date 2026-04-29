from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    channel: Mapped[str] = mapped_column(String(20), default="whatsapp")  # whatsapp | web
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
