from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.constants.categories import CATEGORY_SLUGS, SLUG_TO_NAME
from app.db.session import get_db
from app.models.models import Category, Professional, User
from app.schemas.schemas import LoginInput, Token, UserCreate
from app.core.security import hash_password, verify_password, create_access_token
from app.utils.json_fields import dumps_json

router = APIRouter(prefix="/auth", tags=["Auth"])

DEFAULT_AVAILABILITY = {
    "monday": ["08:00", "09:00", "14:00"],
    "tuesday": ["08:00", "09:00", "14:00"],
    "wednesday": ["08:00", "14:00"],
    "thursday": ["08:00", "09:00", "14:00"],
    "friday": ["08:00", "14:00"],
    "saturday": ["09:00", "10:00"],
    "sunday": [],
}


def _resolve_category_id(db: Session, professional_type: str | None, category_id: int | None) -> int:
    if category_id:
        return category_id

    if professional_type and professional_type in CATEGORY_SLUGS:
        category_name = SLUG_TO_NAME[professional_type]
        category = db.query(Category).filter(Category.name.ilike(category_name)).first()
        if category:
            return category.id

    fallback = db.query(Category).first()
    if not fallback:
        raise HTTPException(status_code=500, detail="Nenhuma categoria cadastrada no sistema")
    return fallback.id


@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.email == payload.email).first()

    if user_exists:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")

    if payload.role == "professional" and not payload.professional_type and not payload.category_id:
        raise HTTPException(status_code=400, detail="Informe a categoria do profissional.")

    if payload.professional_type and payload.professional_type not in CATEGORY_SLUGS:
        raise HTTPException(status_code=400, detail="Categoria de profissional inválida.")

    if payload.cpf:
        cpf_clean = "".join(filter(str.isdigit, payload.cpf))
        existing_cpf = db.query(User).filter(User.cpf == cpf_clean).first()
        if existing_cpf:
            raise HTTPException(status_code=400, detail="CPF já cadastrado.")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        phone=payload.phone,
        cpf="".join(filter(str.isdigit, payload.cpf)) if payload.cpf else None,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    if payload.role == "professional":
        category_id = _resolve_category_id(db, payload.professional_type, payload.category_id)
        type_label = SLUG_TO_NAME.get(payload.professional_type or "", "Profissional")

        professional = Professional(
            user_id=user.id,
            category_id=category_id,
            professional_type=payload.professional_type,
            title=payload.title or f"{user.name} — {type_label}",
            description=payload.description or f"Profissional de {type_label.lower()} disponível na plataforma.",
            city=payload.city or "santos",
            state=payload.state or "sp",
            price_from=payload.price_from or 0,
            rating=5,
            reviews_count=0,
            whatsapp="",
            is_featured=False,
            image=None,
            latitude=None,
            longitude=None,
            job_specs=dumps_json(payload.job_specs or {}),
            availability=dumps_json(DEFAULT_AVAILABILITY),
        )

        db.add(professional)
        db.commit()
        db.refresh(professional)

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/login")
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }
