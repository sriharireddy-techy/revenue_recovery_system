from sqlalchemy.orm import Session

from backend.models import Payment, RecoveryCase
from backend.audit import add_audit_log


def process_payment_event(
    db: Session,
    event_type: str,
    payment_id: str
):
    payment = (
        db.query(Payment)
        .filter(Payment.payment_id == payment_id)
        .first()
    )

    if not payment:
        return {
            "status": "ignored",
            "reason": "Payment not found",
            "payment_id": payment_id
        }

    if event_type == "payment.failed":
        if payment.status != "captured":
            payment.status = "failed"

        result = "Payment marked as failed"

    elif event_type == "payment.authorized":
        payment.status = "authorized"

        result = "Payment authorized"

    elif event_type == "payment.captured":
        payment.status = "captured"

        result = "Payment captured successfully"

    else:
        return {
            "status": "ignored",
            "reason": "Unsupported event",
            "event_type": event_type
        }

    db.commit()
    db.refresh(payment)

    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.payment_id == payment_id)
        .first()
    )

    if case:
        if event_type == "payment.captured":
            case.state = "SUCCESS"
            case.last_result = "Payment captured"

        elif event_type == "payment.failed":
            if case.state not in ["SUCCESS", "CLOSED"]:
                case.state = "FAILED"
                case.last_result = "Payment failed"

        db.commit()
        db.refresh(case)

        add_audit_log(
            db=db,
            case_id=case.case_id,
            event_type="RAZORPAY_WEBHOOK",
            description=f"Received Razorpay event: {event_type}",
            decision=event_type,
            result=result
        )

    return {
        "status": "processed",
        "event_type": event_type,
        "payment_id": payment_id,
        "payment_status": payment.status,
        "recovery_case": case.case_id if case else None
    }