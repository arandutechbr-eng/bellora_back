from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import ServiceRequest, User
from app.schemas.schemas import RequestCreate, RequestOut

router = APIRouter(prefix="/requests", tags=["Service Requests"])


@router.get("/me", response_model=list[RequestOut])
def my_requests(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "professional" and user.professional_profile:
        return db.query(ServiceRequest).filter(ServiceRequest.professional_id == user.professional_profile.id).order_by(ServiceRequest.created_at.desc()).all()
    return db.query(ServiceRequest).filter(ServiceRequest.client_id == user.id).order_by(ServiceRequest.created_at.desc()).all()


@router.post("", response_model=RequestOut)
def create_request(data: RequestCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    req = ServiceRequest(client_id=user.id, **data.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req
