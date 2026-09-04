ALLOWED_TRANSITIONS = {
    "FAILED": [
        "ANALYZING",
        "RECOVERING",
        "HUMAN_REVIEW"
    ],

    "ANALYZING": [
        "RECOVERY_PLANNED"
    ],

    "RECOVERY_PLANNED": [
        "ACTION_PENDING",
        "HUMAN_REVIEW"
    ],

    "ACTION_PENDING": [
        "RECOVERING"
    ],

    "RECOVERING": [
        "SUCCESS",
        "FAILED",
        "HUMAN_REVIEW"
    ],

    "SUCCESS": [
        "CLOSED"
    ],

    "HUMAN_REVIEW": [
        "RECOVERING",
        "CLOSED"
    ],

    "CLOSED": []
}


def can_transition(current_state, new_state):
    allowed = ALLOWED_TRANSITIONS.get(
        current_state,
        []
    )

    return new_state in allowed