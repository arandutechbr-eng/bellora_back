from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Message, User
from app.schemas.schemas import MessageCreate, MessageOut

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/request/{request_id}", response_model=list[MessageOut])
def list_messages(request_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.request_id == request_id).order_by(Message.created_at.asc()).all()


@router.post("", response_model=MessageOut)
def create_message(data: MessageCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = Message(sender_id=user.id, **data.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
