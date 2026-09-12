from backend.llm import analyze_payment
from backend.policy import validate_decision

# Test inputs
amount = 900
failure_reason = "insufficient_funds"
attempt_count = 1
payment_status = "failed"

# Package into dict payloads for analyze_payment(payment, customer_history)
payment = {
    "amount": amount,
    "failure_reason": failure_reason,
    "attempt_count": attempt_count,
    "status": payment_status
}

customer_history = {
    "previous_opt_out": False,
    "total_purchases": 1
}

# Run AI Analysis
decision = analyze_payment(
    payment=payment,
    customer_history=customer_history
)

# Run Policy Validation using decision.recommended_action
final_action = validate_decision(
    action=decision.action,    
    confidence=decision.confidence,
    amount=amount,
    attempt_count=attempt_count,
    payment_status=payment_status,
)

print("----- AI DECISION -----")
print("Failure type:", decision.failure_type)
print("Action:", decision.action) 
print("Confidence:", decision.confidence)
   

print("\n----- POLICY DECISION -----")
print("Final action:", final_action)