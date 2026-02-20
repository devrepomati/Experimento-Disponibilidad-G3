from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String)
    reserve_id = Column(String)
    username = Column(String)
    final_price = Column(Float)
    status = Column(String)
    pay_id = Column(String)
    pay_value = Column(Float)
    should_fail = Column(String) 
    created_at = Column(DateTime, default=datetime.utcnow)