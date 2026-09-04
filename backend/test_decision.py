from backend.llm import analyze_payment
from backend.policy import validate_decision


amount = 25000
failure_reason = "insufficient_funds"
attempt_count = 1
payment_status = "failed"


decision = analyze_payment(
    amount=amount,
    failure_reason=failure_reason,
    attempt_count=attempt_count
)


final_action = validate_decision(
    action=decision.action,
    confidence=decision.confidence,
    amount=amount,
    attempt_count=attempt_count,
    payment_status=payment_status
)


print("----- AI DECISION -----")
print("Failure type:", decision.failure_type)
print("Action:", decision.action)
print("Confidence:", decision.confidence)
print("Reason:", decision.reason)

print("\n----- POLICY DECISION -----")
print("Final action:", final_action)