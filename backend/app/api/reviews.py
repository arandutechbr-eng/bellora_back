from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Professional, Review
from app.schemas.schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/professional/{professional_id}", response_model=list[ReviewOut])
def list_reviews(professional_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.professional_id == professional_id).order_by(Review.created_at.desc()).all()


@router.post("", response_model=ReviewOut)
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):
    review = Review(**data.model_dump())
    db.add(review)
    prof = db.get(Professional, data.professional_id)
    if prof:
        total = prof.reviews_count + 1
        prof.rating = round(((prof.rating * prof.reviews_count) + data.rating) / total, 2)
        prof.reviews_count = total
    db.commit()
    db.refresh(review)
    return review
