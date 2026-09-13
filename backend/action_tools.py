import os
import razorpay
from dotenv import load_dotenv
import uuid

load_dotenv()
razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))
import os
import uuid

import razorpay
from dotenv import load_dotenv

load_dotenv()


razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)


def create_payment_link(payment_id: str, amount: float):

    reference_id = "REC_" + uuid.uuid4().hex[:8].upper()
    amount_paise = int(round(amount * 100))
    data = {
        "amount": amount_paise,
        "currency": "INR",
        "accept_partial": False,
        "reference_id": reference_id,
        "description": f"Recovery payment for {payment_id}"
    }

    payment_link = razorpay_client.payment_link.create(data)

    return {
        "status": "created",
        "payment_id": payment_id,
        "amount": amount,
        "currency": "INR",
        "payment_link_id": payment_link["id"],
        "short_url": payment_link["short_url"],
        "reference_id": reference_id
    }


def update_payment_method(customer_id: str):

    return {
        "status": "pending",
        "customer_id": customer_id,
        "message": "Customer payment method update requested"
    }


def execute_recovery_action(
    action: str,
    payment_id: str,
    customer_id: str,
    amount: float
):

    if action == "CREATE_PAYMENT_LINK":

        return create_payment_link(
            payment_id,
            amount
        )

    if action == "UPDATE_PAYMENT_METHOD":

        return update_payment_method(
            customer_id
        )

    if action == "STOP":

        return {
            "status": "stopped",
            "message": "Recovery action stopped"
        }

    if action == "HUMAN_REVIEW":

        return {
            "status": "escalated",
            "message": "Recovery requires human review"
        }

    return {
        "status": "error",
        "message": "Unknown recovery action"
    }