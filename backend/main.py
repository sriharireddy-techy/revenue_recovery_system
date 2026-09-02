from fastapi import FastAPI,Depends
from pydantic import BaseModel
from backend.database import engine, Base
from backend.recovery import determine_action
from backend.database import SessionLocal
from backend import models
from sqlalchemy.orm import Session
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
    action=determine_action(payment.amount,payment.failure_reason,payment.attempt_count)
    new_payment=models.Payment(
        payment_id=payment.payment_id,
        customer_id=payment.customer_id,
        amount=payment.amount,
        status="failed",
        failure_reason=payment.failure_reason,
        attempt_count=payment.attempt_count
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return {
        "message": "Payment failure received",
        "status": "saved",
        "payment_id": payment.payment_id,
        "recommended_action": action
    }
@app.get("/payment")
def get_payment(db: Session=Depends(get_db)):
    payments=db.query(models.Payment).all()
    # db.commit()
    return payments

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