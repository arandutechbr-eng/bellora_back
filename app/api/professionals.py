from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
import httpx

from app.api.deps import get_current_user, require_professional
from app.db.session import get_db
from app.models.models import Professional, User
from app.schemas.schemas import ProfessionalCreate, ProfessionalOut, ProfessionalUpdate
from app.services.professional_helpers import build_professional_out
from app.utils.json_fields import dumps_json

router = APIRouter(prefix="/professionals", tags=["Professionals"])


def _compose_salon_address(
    street: str | None,
    number: str | None,
    complement: str | None,
    zipcode: str | None = None,
) -> str | None:
    parts = [
        (street or "").strip(),
        f"nº {(number or '').strip()}" if (number or "").strip() else "",
        (complement or "").strip(),
        f"CEP {(zipcode or '').strip()}" if (zipcode or "").strip() else "",
    ]
    composed = ", ".join(part for part in parts if part)
    return composed or None


def _geocode_salon(professional: Professional) -> None:
    """Busca lat/lng via Nominatim (OpenStreetMap). Falha silenciosa se não achar."""
    query_parts = [
        professional.salon_street or "",
        professional.salon_number or "",
        professional.city or "",
        professional.state or "",
        professional.salon_zipcode or "",
        "Brasil",
    ]
    query = ", ".join(part.strip() for part in query_parts if part and str(part).strip())
    if len(query) < 8:
        return

    try:
        response = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1, "countrycodes": "br"},
            headers={"User-Agent": "BelloraApp/1.0 (contato@bellora.com.br)"},
            timeout=10.0,
        )
        if response.status_code != 200:
            return
        results = response.json()
        if not results:
            return
        professional.latitude = float(results[0]["lat"])
        professional.longitude = float(results[0]["lon"])
    except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError):
        # Não bloqueia o save se o geocode falhar
        return


def _apply_update(professional: Professional, data: ProfessionalUpdate) -> None:
    payload = data.model_dump(exclude_none=True)
    if "job_specs" in payload:
        payload["job_specs"] = dumps_json(payload["job_specs"])
    if "availability" in payload:
        payload["availability"] = dumps_json(payload["availability"])
    for key, value in payload.items():
        setattr(professional, key, value)

    address_keys = ("salon_street", "salon_number", "salon_complement", "salon_zipcode", "city", "state")
    if any(key in payload for key in address_keys):
        professional.salon_address = _compose_salon_address(
            professional.salon_street,
            professional.salon_number,
            professional.salon_complement,
            professional.salon_zipcode,
        )
        _geocode_salon(professional)


@router.get("", response_model=list[ProfessionalOut])
def list_professionals(
    category_id: int | None = None,
    professional_type: str | None = None,
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
    if professional_type:
        query = query.filter(Professional.professional_type == professional_type)
    if city:
        query = query.filter(Professional.city.ilike(f"%{city}%"))
    if min_rating is not None:
        query = query.filter(Professional.rating >= min_rating)
    if max_price is not None:
        query = query.filter(Professional.price_from <= max_price)
    if featured is not None:
        query = query.filter(Professional.is_featured.is_(featured))

    professionals = (
        query.order_by(Professional.is_featured.desc(), Professional.rating.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return [build_professional_out(item) for item in professionals]


@router.get("/me", response_model=ProfessionalOut)
def get_my_professional(user: User = Depends(require_professional), db: Session = Depends(get_db)):
    professional = (
        db.query(Professional)
        .options(joinedload(Professional.user), joinedload(Professional.category))
        .filter(Professional.user_id == user.id)
        .first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado")
    return build_professional_out(professional)


@router.get("/{professional_id}", response_model=ProfessionalOut)
def get_professional(professional_id: int, db: Session = Depends(get_db)):
    professional = (
        db.query(Professional)
        .options(joinedload(Professional.user), joinedload(Professional.category))
        .filter(Professional.id == professional_id)
        .first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    return build_professional_out(professional)


@router.post("", response_model=ProfessionalOut)
def create_professional(
    data: ProfessionalCreate,
    user: User = Depends(require_professional),
    db: Session = Depends(get_db),
):
    existing = db.query(Professional).filter(Professional.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Você já possui um perfil profissional")

    payload = data.model_dump()
    professional = Professional(user_id=user.id, **payload)
    professional.salon_address = _compose_salon_address(
        professional.salon_street,
        professional.salon_number,
        professional.salon_complement,
        professional.salon_zipcode,
    )
    _geocode_salon(professional)
    db.add(professional)
    db.commit()
    db.refresh(professional)
    return build_professional_out(professional)


@router.put("/{professional_id}", response_model=ProfessionalOut)
def update_professional(
    professional_id: int,
    data: ProfessionalUpdate,
    user: User = Depends(require_professional),
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
    if professional.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Sem permissão")

    _apply_update(professional, data)
    db.commit()
    db.refresh(professional)
    return build_professional_out(professional)
