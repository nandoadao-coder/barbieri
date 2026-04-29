from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.case import Case
from app.models.case_data import CaseData
from app.routers.auth import get_current_user
from app.schemas.case import CaseOut, CaseDetailOut, CaseStatusUpdate

router = APIRouter(prefix="/cases", tags=["cases"])


def _require_auth(authorization: str = Header(...), db: Session = Depends(get_db)):
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer" or not parts[1]:
        raise HTTPException(status_code=401, detail="Token inválido")
    return get_current_user(parts[1], db)


@router.get("/", response_model=list[CaseOut])
def list_cases(
    status: str | None = None,
    db: Session = Depends(get_db),
    _user=Depends(_require_auth),
):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    return query.order_by(Case.created_at.desc()).all()


@router.get("/{case_id}", response_model=CaseDetailOut)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    _user=Depends(_require_auth),
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")

    case_data = db.query(CaseData).filter(CaseData.case_id == case_id).first()
    collected_data = case_data.data if case_data else {}

    return CaseDetailOut(
        id=case.id,
        type=case.type,
        status=case.status,
        complexity=case.complexity,
        collected_data=collected_data,
        created_at=case.created_at,
    )


@router.patch("/{case_id}/status")
def update_case_status(
    case_id: int,
    body: CaseStatusUpdate,
    db: Session = Depends(get_db),
    _user=Depends(_require_auth),
):
    valid_statuses = ["pending_review", "approved", "delivered"]
    if body.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status inválido. Use: {valid_statuses}")

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")

    case.status = body.status
    db.add(case)
    db.commit()
    return {"status": "updated", "case_id": case_id, "new_status": body.status}
