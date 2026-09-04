import os

from dotenv import load_dotenv
from google import genai

from backend.schemas import AIDecision


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_payment(
    amount: float,
    failure_reason: str,
    attempt_count: int
) -> AIDecision:

    prompt = f"""
You are an AI payment recovery decision assistant.

Analyze the following failed payment.

Payment amount: ₹{amount}
Failure reason: {failure_reason}
Previous attempts: {attempt_count}

Your job is to classify the failure and recommend the safest
possible recovery action.

Failure types:
- temporary_failure
- payment_method_problem
- unknown

Allowed actions:
- CREATE_PAYMENT_LINK
- UPDATE_PAYMENT_METHOD
- HUMAN_REVIEW
- STOP

Rules:
- Do not invent payment information.
- If the situation is unclear, choose HUMAN_REVIEW.
- Confidence must be between 0 and 1.
- Keep the explanation short.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AIDecision,
        }
    )

    return AIDecision.model_validate_json(
        response.text
    )