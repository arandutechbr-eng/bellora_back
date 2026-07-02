from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Professional, Review, User
from app.schemas.schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/professional/{professional_id}", response_model=list[ReviewOut])
def list_reviews(professional_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.professional_id == professional_id).order_by(Review.created_at.desc()).all()


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("client", "admin"):
        raise HTTPException(status_code=403, detail="Apenas clientes podem criar avaliações")

    review = Review(
        professional_id=data.professional_id,
        client_name=current_user.name,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    prof = db.get(Professional, data.professional_id)
    if prof:
        total = prof.reviews_count + 1
        prof.rating = round(((prof.rating * prof.reviews_count) + data.rating) / total, 2)
        prof.reviews_count = total
    db.commit()
    db.refresh(review)
    return review
