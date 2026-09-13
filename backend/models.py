from sqlalchemy import Column, Integer, String, Float, DateTime,Boolean
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

class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True)
    payment_id = Column(String, index=True)
    customer_id = Column(String, index=True)

    state = Column(String, default="FAILED")
    recommended_action = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    attempt_count = Column(Integer, default=0)
    last_result = Column(String, nullable=True)

    # Razorpay recovery payment details
    razorpay_payment_link_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    payment_link_url = Column(String, nullable=True)
    payment_link_reference_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, index=True)
    event_type = Column(String)
    description = Column(String)
    decision = Column(String, nullable=True)
    result = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    event_type = Column(String, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)