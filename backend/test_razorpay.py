from backend.action_tools import create_payment_link


result = create_payment_link(
    payment_id="pay_test_123",
    amount=2499
)

print()
print("========== RAZORPAY TEST ==========")
print()

print("Status:", result["status"])
print("Payment ID:", result["payment_id"])
print("Amount:", result["amount"])
print("Currency:", result["currency"])
print("Payment Link ID:", result["payment_link_id"])
print("Payment Link:", result["short_url"])
print("Reference ID:", result["reference_id"])