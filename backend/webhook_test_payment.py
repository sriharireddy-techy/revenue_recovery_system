from backend.database import SessionLocal
from backend.models import Payment

db = SessionLocal()

payment = Payment(
    payment_id="pay_test_auto_003",
    customer_id="cust_auto_003",
    amount=2499,
    status="created",
    failure_reason="insufficient_funds",
    attempt_count=1
)

db.add(payment)
db.commit()

print("Test payment created:")
print("Payment ID:", payment.payment_id)
print("Customer ID:", payment.customer_id)
print("Amount:", payment.amount)

db.close()