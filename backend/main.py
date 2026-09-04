from fastapi import FastAPI,Depends
from pydantic import BaseModel
from backend.database import engine, Base,SessionLocal
from backend.recovery import determine_action
from backend.models import AuditLog
from sqlalchemy.orm import Session
from backend import models
from backend.audit import add_audit_log
from backend.case_service import generate_case_id
from backend.audit import add_audit_log
from backend.case_service import generate_case_id
from backend.state_machine import can_transition

    
Base.metadata.create_all(bind=engine)
def get_db():
    db=SessionLocal()
    try:
        yield db        
    finally:
        db.close()
app = FastAPI(title="RecoverAI")


class PaymentFailure(BaseModel):
    payment_id: str
    customer_id: str
    amount: float
    failure_reason: str
    attempt_count: int


@app.get("/")
def home():
    return {
        "message": "RecoverAI is running"
    }


@app.post("/payment/failed")
def payment_failed(payment: PaymentFailure,db: Session=Depends(get_db)):
     # Check whether payment already exists
    existing_payment = (
        db.query(models.Payment).filter(models.Payment.payment_id == payment.payment_id).first())

    if existing_payment:
        existing_payment.status = "failed"
        existing_payment.failure_reason = payment.failure_reason
        existing_payment.attempt_count = payment.attempt_count
    else:
        existing_payment = models.Payment(
            payment_id=payment.payment_id,
            customer_id=payment.customer_id,
            amount=payment.amount,
            status="failed",
            failure_reason=payment.failure_reason,
            attempt_count=payment.attempt_count
        )

        db.add(existing_payment)
    db.commit()
    # Create recovery case
    case_id = generate_case_id()

    action = determine_action(
        payment.amount,
        payment.failure_reason,
        payment.attempt_count
    )

    case = models.RecoveryCase(
        case_id=case_id,
        payment_id=payment.payment_id,
        customer_id=payment.customer_id,
        state="RECOVERY_PLANNED",
        recommended_action=action,
        attempt_count=payment.attempt_count
    )

    db.add(case)
    db.commit()

    # Record audit event
    add_audit_log(
        db=db,
        case_id=case_id,
        event_type="PAYMENT_FAILED",
        description="Payment failure received",
        decision=action
    )
    return {
       "payment_id": payment.payment_id,
        "case_id": case_id,
        "state": case.state,
        "recommended_action": action
    }

@app.get("/payment")
def get_payment(db: Session=Depends(get_db)):
    payments=db.query(models.Payment).all()
    # db.commit()
    return payments
@app.get("/recovery/cases")
def get_recovery_cases(
    db: Session = Depends(get_db)
):
    return db.query(models.RecoveryCase).all()

@app.get("/payments/{payment_id}")
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):

    payment = (
        db.query(models.Payment)
        .filter(models.Payment.payment_id == payment_id)
        .first()
    )

    if not payment:
        return {
            "error": "Payment not found"
        }

    return payment
@app.get("/recovery/cases/{case_id}")
def get_recovery_case(
    case_id: str,
    db: Session = Depends(get_db)
):

    case = (
        db.query(models.RecoveryCase)
        .filter(
            models.RecoveryCase.case_id == case_id
        )
        .first()
    )

    if not case:
        return {
            "error": "Recovery case not found"
        }

    return case

@app.get("/audit/{case_id}")
def get_audit_logs(
    case_id: str,
    db: Session = Depends(get_db)
):

    logs = (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.case_id == case_id
        )
        .order_by(models.AuditLog.created_at)
        .all()
    )

    return logs