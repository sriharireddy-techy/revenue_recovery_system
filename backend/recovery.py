def determine_action(amount, failure_reason, attempt_count):
    if attempt_count >= 2:
        return "HUMAN_REVIEW"

    if amount > 10000:
        return "HUMAN_REVIEW"

    if failure_reason == "insufficient_funds":
        return "CREATE_PAYMENT_LINK"

    if failure_reason == "expired_card":
        return "UPDATE_PAYMENT_METHOD"

    return "HUMAN_REVIEW"