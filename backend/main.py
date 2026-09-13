from fastapi import FastAPI,Depends
from pydantic import BaseModel
from backend.database import engine, Base,SessionLocal
from backend.recovery import determine_action
from backend.models import AuditLog,Payment,RecoveryCase, WebhookEvent
from sqlalchemy.orm import Session
from backend import models
from backend.audit import add_audit_log
from backend.case_service import generate_case_id
from backend.audit import add_audit_log
from backend.case_service import generate_case_id
from backend.state_machine import can_transition
from backend.recovery_service import run_recovery_analysis
from fastapi import Depends, HTTPException,Request,BackgroundTasks
from sqlalchemy.orm import Session
import os,hmac,hashlib,json
from dotenv import load_dotenv
from backend.webhook_service import process_payment_event
load_dotenv()
    
Base.metadata.create_all(bind=engine)
def get_db():
    db=SessionLocal()
    try:
        yield db        
    finally:
        db.close()
app = FastAPI(title="RecoverAI")


class PaymentFailure(BaseModel):
    payment_id: str
    customer_id: str
    amount: float
    failure_reason: str
    attempt_count: int


@app.get("/")
def home():
    return {
        "message": "RecoverAI is running"
    }


@app.post("/payment/failed")
def payment_failed(payment: PaymentFailure,db: Session=Depends(get_db)):
     # Check whether payment already exists
    existing_payment = (
        db.query(models.Payment).filter(models.Payment.payment_id == payment.payment_id).first())

    if existing_payment:
        existing_payment.status = "failed"
        existing_payment.failure_reason = payment.failure_reason
        existing_payment.attempt_count = payment.attempt_count
    else:
        existing_payment = models.Payment(
            payment_id=payment.payment_id,
            customer_id=payment.customer_id,
            amount=payment.amount,
            status="failed",
            failure_reason=payment.failure_reason,
            attempt_count=payment.attempt_count
        )

        db.add(existing_payment)
    db.commit()
    # Create recovery case
    case_id = generate_case_id()

    action = determine_action(
        payment.amount,
        payment.failure_reason,
        payment.attempt_count
    )

    case = models.RecoveryCase(
        case_id=case_id,
        payment_id=payment.payment_id,
        customer_id=payment.customer_id,
        state="RECOVERY_PLANNED",
        recommended_action=action,
        attempt_count=payment.attempt_count
    )

    db.add(case)
    db.commit()

    # Record audit event
    add_audit_log(
        db=db,
        case_id=case_id,
        event_type="PAYMENT_FAILED",
        description="Payment failure received",
        decision=action
    )
    return {
       "payment_id": payment.payment_id,
        "case_id": case_id,
        "state": case.state,
        "recommended_action": action
    }

@app.get("/payment")
def get_payment(db: Session=Depends(get_db)):
    payments=db.query(models.Payment).all()
    # db.commit()
    return payments
@app.get("/recovery/cases")
def get_recovery_cases(
    db: Session = Depends(get_db)
):
    return db.query(models.RecoveryCase).all()

@app.get("/payments/{payment_id}")
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):

    payment = (
        db.query(models.Payment)
        .filter(models.Payment.payment_id == payment_id)
        .first()
    )

    if not payment:
        return {
            "error": "Payment not found"
        }

    return payment
@app.get("/recovery/cases/{case_id}")
def get_recovery_case(
    case_id: str,
    db: Session = Depends(get_db)
):

    case = (
        db.query(models.RecoveryCase)
        .filter(
            models.RecoveryCase.case_id == case_id
        )
        .first()
    )

    if not case:
        return {
            "error": "Recovery case not found"
        }

    return case

@app.get("/audit/{case_id}")
def get_audit_logs(
    case_id: str,
    db: Session = Depends(get_db)
):

    logs = (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.case_id == case_id
        )
        .order_by(models.AuditLog.created_at)
        .all()
    )

    return logs


@app.post("/recovery/{case_id}/analyze")
def analyze_recovery_case(
    case_id: str,
    db: Session = Depends(get_db)
):

    try:

        result = run_recovery_analysis(
            db=db,
            case_id=case_id
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
def automatic_recovery_analysis(case_id: str):
    db = SessionLocal()

    try:
        from backend.recovery_service import run_recovery_analysis

        result = run_recovery_analysis(
            db=db,
            case_id=case_id
        )

        print()
        print("========== AUTOMATIC RECOVERY ==========")
        print("Case ID:", case_id)
        print("AI Action:", result["ai_action"])
        print("Confidence:", result["confidence"])
        print("Final Action:", result["final_action"])
        print("State:", result["state"])

    except Exception as e:
        print()
        print("========== AUTOMATIC RECOVERY ERROR ==========")
        print("Case ID:", case_id)
        print("Error:", str(e))

    finally:
        db.close()
        
        
        
@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    body = await request.body()

    signature = request.headers.get("X-Razorpay-Signature")

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay webhook signature"
        )

    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="Webhook secret is not configured"
        )

    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature"
        )
    event_id = request.headers.get("x-razorpay-event-id")
    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay event ID"
        )

    existing_event = (
        db.query(WebhookEvent)
        .filter(WebhookEvent.event_id == event_id)
        .first()
    )

    if existing_event:
        return {
            "status": "already_processed",
            "event_id": event_id
        }
    data = json.loads(body.decode("utf-8"))

    event_type = data.get("event")

    webhook_event = WebhookEvent(
        event_id=event_id,
        event_type=event_type,
        processed=True
    )

    db.add(webhook_event)
    db.commit()
    payment_data = (
        data.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    payload = data.get("payload", {})

    payment_data = (
        payload
        .get("payment", {})
        .get("entity", {})
    )

    payment_id = payment_data.get("id")

    payment_link_data = (
        payload
        .get("payment_link", {})
        .get("entity", {})
    )

    payment_link_id = payment_link_data.get("id")


    if event_type == "payment_link.paid":

        if not payment_id:
            return {
                "status": "ignored",
                "reason": "Payment ID not found"
            }

        if not payment_link_id:
            return {
                "status": "ignored",
                "reason": "Payment Link ID not found"
            }

    else:

        if not payment_id:
            return {
                "status": "ignored",
                "reason": "Payment ID not found"
            }


    result = process_payment_event(
        db=db,
        event_type=event_type,
        payment_id=payment_id,
        payment_link_id=payment_link_id,
        payment_data=payment_data
    )

    # Automatically start AI recovery for newly created
    # recovery cases from payment.failed
    if (
        event_type == "payment.failed"
        and result.get("recovery_case")
    ):
        background_tasks.add_task(
            automatic_recovery_analysis,
            result["recovery_case"]
        )

    return result
        # print()
        # print("========== RAZORPAY WEBHOOK ==========")
        # print()
        # print("Valid webhook received")
        # print("Body:", body.decode("utf-8"))

        # return {
        #     "status": "received",
        #     "event_id": event_id,
        #     "event_type": event_type
        # }