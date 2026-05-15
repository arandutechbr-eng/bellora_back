from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.models import Professional, User
from app.schemas.schemas import ProfessionalCreate, ProfessionalOut, ProfessionalUpdate
from app.api.deps import require_professional

router = APIRouter(prefix="/professionals", tags=["Professionals"])


@router.get("", response_model=list[ProfessionalOut])
def list_professionals(
    category_id: int | None = None,
    city: str | None = None,
    min_rating: float | None = Query(default=None, ge=1, le=5),
    max_price: float | None = None,
    featured: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(Professional).options(joinedload(Professional.user), joinedload(Professional.category))
    if category_id:
        query = query.filter(Professional.category_id == category_id)
    if city:
        query = query.filter(Professional.city.ilike(f"%{city}%"))
    if min_rating:
        query = query.filter(Professional.rating >= min_rating)
    if max_price:
        query = query.filter(Professional.price_from <= max_price)
    if featured is not None:
        query = query.filter(Professional.is_featured == featured)
    return query.offset((page - 1) * limit).limit(limit).all()


@router.get("/{professional_id}", response_model=ProfessionalOut)
def get_professional(professional_id: int, db: Session = Depends(get_db)):
    return db.query(Professional).options(joinedload(Professional.user), joinedload(Professional.category)).filter(Professional.id == professional_id).first()


@router.post("", response_model=ProfessionalOut)
def create_professional(data: ProfessionalCreate, user: User = Depends(require_professional), db: Session = Depends(get_db)):
    professional = Professional(user_id=user.id, **data.model_dump())
    db.add(professional)
    db.commit()
    db.refresh(professional)
    return professional


@router.put("/{professional_id}", response_model=ProfessionalOut)
def update_professional(
    professional_id: int,
    data: ProfessionalUpdate,
    db: Session = Depends(get_db),
):
    professional = (
        db.query(Professional)
        .options(joinedload(Professional.user), joinedload(Professional.category))
        .filter(Professional.id == professional_id)
        .first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(professional, key, value)

    db.commit()
    db.refresh(professional)
    return professional
