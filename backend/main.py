from fastapi import FastAPI
from pydantic import BaseModel
from backend.recovery import determine_action
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
def payment_failed(payment: PaymentFailure):
    action=determine_action(payment.amount,payment.failure_reason,payment.attempt_count)
    
    return {
        "message": "Payment failure received",
        "payment_id": payment.payment_id,
        "recommended_action": action
    }