import json

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.models import Category, Message, Professional, Review, Service, ServiceRequest, User

DEFAULT_AVAILABILITY = json.dumps({
    "monday": ["08:00", "09:00", "14:00"],
    "tuesday": ["08:00", "09:00", "14:00"],
    "wednesday": ["08:00", "14:00"],
    "thursday": ["08:00", "09:00", "14:00"],
    "friday": ["08:00", "14:00"],
    "saturday": ["09:00", "10:00"],
    "sunday": [],
})

BEAUTY_SPECS = json.dumps({
    "especialidade": "Coloração e tratamentos",
    "experiencia_anos": 5,
    "atendimento_domicilio": False,
    "atendimento_salao": True,
    "aceita_cartao": True,
})

NAIL_SPECS = json.dumps({
    "especialidade": "Nail art e alongamento",
    "experiencia_anos": 4,
    "atendimento_domicilio": True,
    "atendimento_salao": True,
    "aceita_cartao": True,
})


def ensure_default_availability():
    """Preenche agenda padrão para profissionais sem horários (cadastros antigos)."""
    db = SessionLocal()
    try:
        professionals = db.query(Professional).all()
        updated = 0
        for professional in professionals:
            weekly = json.loads(professional.availability) if professional.availability else {}
            has_slots = any(weekly.get(day) for day in weekly if weekly.get(day))
            if not has_slots:
                professional.availability = DEFAULT_AVAILABILITY
                updated += 1
        if updated:
            db.commit()
    finally:
        db.close()


def ensure_extra_categories():
    """Garante que todas as categorias Bellora existam."""
    from app.constants.categories import BEAUTY_CATEGORIES

    db = SessionLocal()
    try:
        for slug, name, description in BEAUTY_CATEGORIES:
            exists = db.query(Category).filter(Category.name == name).first()
            if not exists:
                db.add(Category(name=name, icon=slug, description=description))
        db.commit()
    finally:
        db.close()


def seed_database():
    from app.constants.categories import BEAUTY_CATEGORIES

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first():
            return

        client = User(
            name="Ana Cliente",
            email="cliente@bellora.com",
            password_hash=hash_password("123456"),
            role="client",
        )
        pro_cabelo = User(
            name="Juliana Mendes",
            email="cabelo@bellora.com",
            password_hash=hash_password("123456"),
            role="professional",
        )
        pro_unhas = User(
            name="Camila Rocha",
            email="unhas@bellora.com",
            password_hash=hash_password("123456"),
            role="professional",
        )
        db.add_all([client, pro_cabelo, pro_unhas])
        db.flush()

        cats = [
            Category(name=name, icon=slug, description=desc)
            for slug, name, desc in BEAUTY_CATEGORIES
        ]
        db.add_all(cats)
        db.flush()

        cat_map = {c.icon: c for c in cats}

        profs = [
            Professional(
                user_id=pro_cabelo.id,
                category_id=cat_map["cabelo"].id,
                title="Colorista e cabeleireira",
                description="Especialista em coloração, mechas e tratamentos capilares com produtos premium.",
                city="Santos",
                state="SP",
                price_from=120,
                rating=4.9,
                reviews_count=87,
                whatsapp="5513977777777",
                is_featured=True,
                image="https://images.unsplash.com/photo-1560066984-138dadb4c035",
                professional_type="cabelo",
                biography="Mais de 8 anos transformando visuais com técnica e cuidado.",
                job_specs=BEAUTY_SPECS,
                availability=DEFAULT_AVAILABILITY,
            ),
            Professional(
                user_id=pro_unhas.id,
                category_id=cat_map["unhas"].id,
                title="Nail designer",
                description="Alongamento em gel, nail art criativa e manicure spa.",
                city="São Vicente",
                state="SP",
                price_from=80,
                rating=4.8,
                reviews_count=64,
                whatsapp="5513966666666",
                is_featured=True,
                image="https://images.unsplash.com/photo-1604654894610-df63bc536371",
                professional_type="unhas",
                biography="Apaixonada por unhas impecáveis e design personalizado.",
                job_specs=NAIL_SPECS,
                availability=DEFAULT_AVAILABILITY,
            ),
        ]
        db.add_all(profs)
        db.flush()

        services = [
            Service(
                professional_id=profs[0].id,
                title="Corte feminino",
                description="Corte, lavagem e finalização.",
                duration=60,
                price=90,
            ),
            Service(
                professional_id=profs[0].id,
                title="Coloração completa",
                description="Coloração com produtos profissionais.",
                duration=120,
                price=180,
            ),
            Service(
                professional_id=profs[1].id,
                title="Manicure spa",
                description="Cutilagem, esmaltação e hidratação.",
                duration=45,
                price=55,
            ),
            Service(
                professional_id=profs[1].id,
                title="Alongamento em gel",
                description="Alongamento com acabamento natural.",
                duration=90,
                price=150,
            ),
        ]
        db.add_all(services)
        db.flush()

        reviews = [
            Review(
                professional_id=profs[0].id,
                client_name="Marina",
                rating=5,
                comment="Melhor coloração que já fiz! Atendimento impecável.",
            ),
            Review(
                professional_id=profs[1].id,
                client_name="Fernanda",
                rating=5,
                comment="Unhas perfeitas e duradouras. Super recomendo!",
            ),
        ]
        db.add_all(reviews)
        db.flush()

        req = ServiceRequest(
            client_id=client.id,
            professional_id=profs[0].id,
            category_id=cat_map["cabelo"].id,
            title="Coloração e corte",
            description="Preciso de coloração mechas e corte nas pontas.",
            location="Santos - SP",
            status="in_progress",
            budget=200,
        )
        db.add(req)
        db.flush()
        db.add_all([
            Message(request_id=req.id, sender_id=client.id, content="Olá, você tem horário na quinta?"),
            Message(request_id=req.id, sender_id=pro_cabelo.id, content="Tenho sim! Às 14h funciona para você?"),
        ])
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
    print("Banco criado e populado com sucesso.")
