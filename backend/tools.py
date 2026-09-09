from sqlalchemy.orm import Session
from backend.models import Payment

def get_payment_details(db: Session, payment_id: str):
    payment = (
        db.query(Payment)
        .filter(Payment.payment_id == payment_id)
        .first()
    )

    if not payment:
        return {
            "error": "Payment not found"
        }

    return {
        "payment_id": payment.payment_id,
        "customer_id": payment.customer_id,
        "amount": payment.amount,
        "status": payment.status,
        "failure_reason": payment.failure_reason,
        "attempt_count": payment.attempt_count
    }


def get_customer_history(db: Session, customer_id: str):
    payments = (
        db.query(Payment)
        .filter(Payment.customer_id == customer_id)
        .all()
    )

    return {
        "customer_id": customer_id,
        "total_payments": len(payments),
        "payments": [
            {
                "payment_id": payment.payment_id,
                "amount": payment.amount,
                "status": payment.status,
                "failure_reason": payment.failure_reason,
                "attempt_count": payment.attempt_count
            }
            for payment in payments
        ]
    }