from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_professional
from app.db.session import get_db
from app.models.models import Professional, Service, User
from app.schemas.schemas import ServiceCreate, ServiceOut, ServiceUpdate

router = APIRouter(prefix="/services", tags=["Services"])


def _get_owned_professional(user: User, db: Session) -> Professional:
    professional = db.query(Professional).filter(Professional.user_id == user.id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado")
    return professional


@router.get("/professional/{professional_id}", response_model=list[ServiceOut])
def list_professional_services(professional_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Service)
        .filter(Service.professional_id == professional_id)
        .order_by(Service.price.asc())
        .all()
    )


@router.get("/me", response_model=list[ServiceOut])
def list_my_services(user: User = Depends(require_professional), db: Session = Depends(get_db)):
    professional = _get_owned_professional(user, db)
    return db.query(Service).filter(Service.professional_id == professional.id).all()


@router.post("", response_model=ServiceOut)
def create_service(
    payload: ServiceCreate,
    user: User = Depends(require_professional),
    db: Session = Depends(get_db),
):
    professional = _get_owned_professional(user, db)
    service = Service(
        professional_id=professional.id,
        title=payload.title,
        description=payload.description,
        duration=payload.duration,
        price=payload.price,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    user: User = Depends(require_professional),
    db: Session = Depends(get_db),
):
    professional = _get_owned_professional(user, db)
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.professional_id == professional.id)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    user: User = Depends(require_professional),
    db: Session = Depends(get_db),
):
    professional = _get_owned_professional(user, db)
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.professional_id == professional.id)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    db.delete(service)
    db.commit()
    return {"ok": True}
