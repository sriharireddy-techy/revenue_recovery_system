from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.database import Base
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)

    payment_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)

    amount = Column(Float)

    status = Column(String)
    failure_reason = Column(String, nullable=True)

    attempt_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    