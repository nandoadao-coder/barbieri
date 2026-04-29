from datetime import datetime
from pydantic import BaseModel
from typing import Any


class CaseOut(BaseModel):
    id: int
    type: str
    status: str
    complexity: str | None
    client_id: int | None
    lawyer_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseDetailOut(BaseModel):
    id: int
    type: str
    status: str
    complexity: str | None
    collected_data: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseStatusUpdate(BaseModel):
    status: str  # pending_review | approved | delivered
