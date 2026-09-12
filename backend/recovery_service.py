from sqlalchemy.orm import Session
from backend.action_tools import execute_recovery_action

from backend.models import RecoveryCase
from backend.agent import execute_tool
from backend.llm import analyze_payment
from backend.policy import validate_decision
from backend.audit import add_audit_log


def run_recovery_analysis(
    db: Session,
    case_id: str
):

    # 1. Find recovery case
    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.case_id == case_id)
        .first()
    )

    if not case:
        raise ValueError("Recovery case not found")

    # 2. Get payment information
    payment = execute_tool(
        "get_payment_details",
        {
            "payment_id": case.payment_id
        }
    )

    if "error" in payment:
        raise ValueError(payment["error"])

    # 3. Get customer history
    customer_history = execute_tool(
        "get_customer_history",
        {
            "customer_id": case.customer_id
        }
    )

    # 4. Ask Gemini for decision
    decision = analyze_payment(
        payment,
        customer_history
    )

    # 5. Apply deterministic policy
    final_action = validate_decision(
        action=decision.action,
        confidence=decision.confidence,
        amount=payment["amount"],
        attempt_count=payment["attempt_count"],
        payment_status=payment["status"]
    )
    action_result = None

    if final_action in [
        "CREATE_PAYMENT_LINK",
        "UPDATE_PAYMENT_METHOD"
    ]:

        action_result = execute_recovery_action(
            action=final_action,
            payment_id=payment["payment_id"],
            customer_id=payment["customer_id"],
            amount=payment["amount"]
        )
    

    # 6. Save AI decision
    case.recommended_action = decision.action
    case.confidence = decision.confidence

    # 7. Save final policy decision
    if final_action == "HUMAN_REVIEW":
        case.state = "HUMAN_REVIEW"

    elif final_action == "STOP":
        case.state = "CLOSED"

    else:
        case.state = "ACTION_PENDING"
    case.last_result = final_action

    db.commit()
    db.refresh(case)

    # 8. Audit AI decision
    add_audit_log(
        db=db,
        case_id=case.case_id,
        event_type="AI_DECISION",
        description=decision.reason,
        decision=decision.action,
        result=final_action
    )

    return {
        "case_id": case.case_id,
        "payment_id": case.payment_id,
        "ai_action": decision.action,
        "confidence": decision.confidence,
        "reason": decision.reason,
        "final_action": final_action,
        "state": case.state,
        "action_result": action_result
    }