import uuid


def create_payment_link(payment_id: str, amount: float):

    link_id = "plink_" + uuid.uuid4().hex[:8]

    return {
        "status": "created",
        "payment_id": payment_id,
        "amount": amount,
        "payment_link_id": link_id,
        "message": "Payment link created in simulation mode"
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