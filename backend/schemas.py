from typing import Literal

from pydantic import BaseModel


class AIDecision(BaseModel):

    failure_type: Literal[
        "temporary_failure",
        "payment_method_problem",
        "unknown"
    ]

    action: Literal[
        "CREATE_PAYMENT_LINK",
        "UPDATE_PAYMENT_METHOD",
        "HUMAN_REVIEW",
        "STOP"
    ]

    confidence: float

    reason: str