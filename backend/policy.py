ALLOWED_ACTIONS = {
    "CREATE_PAYMENT_LINK",
    "UPDATE_PAYMENT_METHOD",
    "HUMAN_REVIEW",
    "STOP"
}


def validate_decision(
    action,
    confidence,
    amount,
    attempt_count,
    payment_status,
    recovery_state=None
):

    # ---------------------------------------------------------
    # STOP: Payment is already successful
    # ---------------------------------------------------------
    if payment_status in ["captured", "authorized"]:
        return "STOP"

    # ---------------------------------------------------------
    # STOP: Recovery was already completed
    # ---------------------------------------------------------
    if recovery_state in ["SUCCESS", "CLOSED"]:
        return "STOP"

    # ---------------------------------------------------------
    # SAFETY: Unknown or invalid AI action
    # ---------------------------------------------------------
    if action not in ALLOWED_ACTIONS:
        return "HUMAN_REVIEW"

    # ---------------------------------------------------------
    # SAFETY: Missing or low confidence
    # ---------------------------------------------------------
    if confidence is None or confidence < 0.75:
        return "HUMAN_REVIEW"

    # ---------------------------------------------------------
    # SAFETY: High-value payment
    # ---------------------------------------------------------
    if amount > 10000:
        return "HUMAN_REVIEW"

    # ---------------------------------------------------------
    # SAFETY: Too many attempts
    # ---------------------------------------------------------
    if attempt_count >= 2:
        return "HUMAN_REVIEW"

    return action