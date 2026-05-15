from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.models import Category, Message, Professional, Review, ServiceRequest, User


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first():
            return

        client = User(name="Anderson Cliente", email="cliente@zola.com", password_hash=hash_password("123456"), role="client")
        pro_user = User(name="Carlos Eletricista", email="profissional@zola.com", password_hash=hash_password("123456"), role="professional")
        db.add_all([client, pro_user])
        db.flush()

        cats = [
            Category(name="Eletricista", icon="FaBolt", description="Instalações, reparos e manutenção elétrica"),
            Category(name="Encanador", icon="FaWater", description="Vazamentos, torneiras, caixas e tubulações"),
            Category(name="Diarista", icon="FaBroom", description="Limpeza residencial e comercial"),
            Category(name="Mecânico", icon="FaCar", description="Serviços automotivos locais"),
            Category(name="Pintor", icon="FaPaintRoller", description="Pintura residencial e comercial"),
            Category(name="Técnico de informática", icon="FaLaptopCode", description="Computadores, redes e suporte técnico"),
        ]
        db.add_all(cats)
        db.flush()

        profs = [
            Professional(user_id=pro_user.id, category_id=cats[0].id, title="Eletricista residencial 24h", description="Faço instalação de tomadas, quadros, chuveiros e manutenção preventiva.", city="Santos", state="SP", price_from=120, rating=4.9, reviews_count=38, whatsapp="5513999999999", is_featured=True, image="https://images.unsplash.com/photo-1621905251189-08b45d6a269e", latitude=-23.9608, longitude=-46.3336),
            Professional(user_id=pro_user.id, category_id=cats[1].id, title="Encanador para vazamentos", description="Atendimento rápido para vazamentos, sifões, registros e tubulação.", city="São Vicente", state="SP", price_from=95, rating=4.7, reviews_count=22, whatsapp="5513988888888", is_featured=True, image="https://images.unsplash.com/photo-1607472586893-edb57bdc0e39"),
            Professional(user_id=pro_user.id, category_id=cats[2].id, title="Diarista caprichosa", description="Limpeza pesada, pós-obra e organização de ambientes.", city="Praia Grande", state="SP", price_from=160, rating=4.8, reviews_count=51, whatsapp="5513977777777", is_featured=False, image="https://images.unsplash.com/photo-1581578731548-c64695cc6952"),
        ]
        db.add_all(profs)
        db.flush()

        reviews = [
            Review(professional_id=profs[0].id, client_name="Mariana", rating=5, comment="Atendimento rápido e muito profissional."),
            Review(professional_id=profs[0].id, client_name="Roberto", rating=5, comment="Resolveu meu problema no quadro de energia."),
            Review(professional_id=profs[1].id, client_name="Fernanda", rating=4, comment="Bom serviço e preço justo."),
        ]
        db.add_all(reviews)
        db.flush()

        req = ServiceRequest(client_id=client.id, professional_id=profs[0].id, category_id=cats[0].id, title="Instalar chuveiro", description="Preciso instalar um chuveiro novo no banheiro.", location="Santos - SP", status="in_progress", budget=150)
        db.add(req)
        db.flush()
        db.add_all([
            Message(request_id=req.id, sender_id=client.id, content="Olá, você consegue atender hoje?"),
            Message(request_id=req.id, sender_id=pro_user.id, content="Consigo sim. Pode ser depois das 14h?"),
        ])
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
    print("Banco criado e populado com sucesso.")
