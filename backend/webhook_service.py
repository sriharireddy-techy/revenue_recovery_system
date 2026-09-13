from sqlalchemy.orm import Session

from backend.models import Payment, RecoveryCase
from backend.audit import add_audit_log


def process_payment_event(
    db: Session,
    event_type: str,
    payment_id: str,
    payment_link_id: str | None = None
):
    # ---------------------------------------------------------
    # PAYMENT LINK PAID
    # ---------------------------------------------------------
    if event_type == "payment_link.paid":

        if not payment_link_id:
            return {
                "status": "ignored",
                "reason": "Payment Link ID not found"
            }

        case = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.razorpay_payment_link_id
                == payment_link_id
            )
            .first()
        )

        if not case:
            return {
                "status": "ignored",
                "reason": "Recovery case not found for Payment Link",
                "payment_link_id": payment_link_id
            }

        # Store the actual Razorpay payment ID
        case.razorpay_payment_id = payment_id

        # Recovery succeeded
        case.state = "SUCCESS"
        case.last_result = "Recovery payment completed"

        db.commit()
        db.refresh(case)

        add_audit_log(
            db=db,
            case_id=case.case_id,
            event_type="RAZORPAY_WEBHOOK",
            description=(
                "Recovery Payment Link was paid successfully"
            ),
            decision="payment_link.paid",
            result=(
                f"Recovery successful. "
                f"Payment Link: {payment_link_id}, "
                f"Payment: {payment_id}"
            )
        )

        return {
            "status": "processed",
            "event_type": event_type,
            "payment_link_id": payment_link_id,
            "razorpay_payment_id": payment_id,
            "recovery_case": case.case_id,
            "state": case.state
        }

    # ---------------------------------------------------------
    # NORMAL PAYMENT EVENTS
    # ---------------------------------------------------------
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
        .filter(
            RecoveryCase.payment_id == payment_id
        )
        .first()
    )

    if case:

        if event_type == "payment.captured":

            # Don't overwrite a completed recovery incorrectly
            if case.state not in ["SUCCESS", "CLOSED"]:
                case.state = "SUCCESS"
                case.last_result = "Payment captured"

        elif event_type == "payment.failed":

            # Ignore stale failure events
            if case.state not in ["SUCCESS", "CLOSED"]:
                case.state = "FAILED"
                case.last_result = "Payment failed"

        db.commit()
        db.refresh(case)

        add_audit_log(
            db=db,
            case_id=case.case_id,
            event_type="RAZORPAY_WEBHOOK",
            description=(
                f"Received Razorpay event: {event_type}"
            ),
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