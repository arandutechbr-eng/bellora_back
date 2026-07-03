from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Message, ServiceRequest, User
from app.schemas.schemas import MessageCreate, MessageOut

router = APIRouter(prefix="/messages", tags=["Messages"])


def _assert_participant(request_id: int, user: User, db: Session) -> ServiceRequest:
    """Garante que o usuário é cliente ou profissional do pedido."""
    req = db.get(ServiceRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if user.id not in (req.client_id, req.professional_id) and user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado a este pedido")
    return req


@router.get("/request/{request_id}", response_model=list[MessageOut])
def list_messages(
    request_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _assert_participant(request_id, user, db)
    return db.query(Message).filter(Message.request_id == request_id).order_by(Message.created_at.asc()).all()


@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _assert_participant(data.request_id, user, db)
    msg = Message(sender_id=user.id, **data.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
