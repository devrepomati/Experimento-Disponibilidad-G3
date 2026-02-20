from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from payments.domain.models import Base, Payment

DATABASE_URL = "sqlite:///payments.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def add_payment(payment_data):
    session = SessionLocal()
    try:
        payment = Payment(**payment_data)
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment
    finally:
        session.close()

def get_all_payments():
    session = SessionLocal()
    try:
        return session.query(Payment).all()
    finally:
        session.close()