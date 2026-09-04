from backend.llm import analyze_payment


decision = analyze_payment(
    amount=2499,
    failure_reason="unknown",
    attempt_count=1
)

print("Failure type:", decision.failure_type)
print("Action:", decision.action)
print("Confidence:", decision.confidence)
print("Reason:", decision.reason)