from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def _column_names(inspector, table: str) -> set[str]:
    return {col["name"] for col in inspector.get_columns(table)}


def _bool_default(engine: Engine) -> str:
    return "FALSE" if engine.dialect.name == "postgresql" else "0"


def run_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    bool_default = _bool_default(engine)

    if "users" in inspector.get_table_names():
        columns = _column_names(inspector, "users")
        with engine.begin() as conn:
            if "phone" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
            if "cpf" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN cpf VARCHAR(14)"))

    if "professionals" in inspector.get_table_names():
        columns = _column_names(inspector, "professionals")
        with engine.begin() as conn:
            if "professional_type" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN professional_type VARCHAR(20)"))
            if "job_specs" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN job_specs TEXT"))
            if "availability" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN availability TEXT"))
            if "biography" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN biography TEXT"))
            if "salon_address" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN salon_address TEXT"))
            if "salon_street" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN salon_street VARCHAR(200)"))
            if "salon_number" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN salon_number VARCHAR(30)"))
            if "salon_complement" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN salon_complement VARCHAR(120)"))
            if "salon_zipcode" not in columns:
                conn.execute(text("ALTER TABLE professionals ADD COLUMN salon_zipcode VARCHAR(12)"))

    # services e appointments são criadas pelo SQLAlchemy (Base.metadata.create_all)
    # antes de run_migrations ser chamado — não precisamos de CREATE TABLE aqui.
    # Blocos CREATE TABLE com sintaxe SQLite (AUTOINCREMENT, DATETIME) foram removidos
    # para não quebrar no PostgreSQL de produção.

    if "appointments" in inspector.get_table_names():
        columns = _column_names(inspector, "appointments")
        with engine.begin() as conn:
            if "total_amount" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN total_amount REAL DEFAULT 0"))
            if "deposit_amount" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN deposit_amount REAL DEFAULT 0"))
            if "deposit_paid" not in columns:
                conn.execute(
                    text(f"ALTER TABLE appointments ADD COLUMN deposit_paid BOOLEAN DEFAULT {bool_default}")
                )
            if "payment_status" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN payment_status VARCHAR(30) DEFAULT 'pending'"))
            if "stripe_checkout_session_id" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN stripe_checkout_session_id VARCHAR(255)"))
            if "stripe_payment_intent_id" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN stripe_payment_intent_id VARCHAR(255)"))
            if "batch_id" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN batch_id VARCHAR(64)"))
            if "payment_mode" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN payment_mode VARCHAR(20) DEFAULT 'deposit'"))
            if "amount_due" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN amount_due REAL DEFAULT 0"))
            if "service_id" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN service_id INTEGER REFERENCES services(id)"))
            if "location_type" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN location_type VARCHAR(20)"))
            if "service_address" not in columns:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN service_address TEXT"))

    if "reviews" in inspector.get_table_names():
        columns = _column_names(inspector, "reviews")
        with engine.begin() as conn:
            if "appointment_id" not in columns:
                conn.execute(text("ALTER TABLE reviews ADD COLUMN appointment_id INTEGER REFERENCES appointments(id)"))
