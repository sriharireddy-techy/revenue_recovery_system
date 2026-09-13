from backend.database import SessionLocal
from backend.models import RecoveryCase

db = SessionLocal()

case = (
    db.query(RecoveryCase)
    .filter(RecoveryCase.case_id == "REC_E3A1BB97")
    .first()
)

if not case:
    print("Recovery case not found")
else:
    case.razorpay_payment_link_id = "plink_TbPYPRZaZBPDmU"
    case.razorpay_payment_id = "pay_TbPbT90DoGNxXj"
    case.payment_link_url = None
    case.payment_link_reference_id = None

    db.commit()
    db.refresh(case)

    print("Recovery payment connected successfully.")
    print("Case ID:", case.case_id)
    print("Payment Link ID:", case.razorpay_payment_link_id)
    print("Razorpay Payment ID:", case.razorpay_payment_id)

db.close()