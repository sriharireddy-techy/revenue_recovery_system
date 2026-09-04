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
    payment_status
):

    if payment_status == "captured":
        return "STOP"

    if action not in ALLOWED_ACTIONS:
        return "HUMAN_REVIEW"

    if confidence < 0.75:
        return "HUMAN_REVIEW"

    if amount > 10000:
        return "HUMAN_REVIEW"

    if attempt_count >= 2:
        return "HUMAN_REVIEW"

    return action