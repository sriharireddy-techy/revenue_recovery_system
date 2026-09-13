from backend.action_tools import execute_recovery_action

result = execute_recovery_action(
    action="CREATE_PAYMENT_LINK",
    payment_id="pay_test_auto_004",
    customer_id="cust_auto_004",
    amount=2499
)

print()
print("========== RECOVERY ACTION TEST ==========")
print()
print("Status:", result["status"])
print("Payment ID:", result["payment_id"])
print("Amount:", result["amount"])
print("Currency:", result["currency"])
print("Payment Link ID:", result["payment_link_id"])
print("Payment Link:", result["short_url"])
print("Reference ID:", result["reference_id"])