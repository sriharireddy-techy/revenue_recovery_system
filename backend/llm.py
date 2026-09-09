import os

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError


from backend.schemas import AIDecision


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def analyze_payment(
    payment: dict,
    customer_history: dict
) -> AIDecision:

    prompt = f"""
You are an AI payment recovery decision assistant for a fintech merchant system.

Analyze this failed payment using ONLY the provided context and strict financial policy logic.

PAYMENT:
{payment}

CUSTOMER HISTORY:
{customer_history}

Your job is to recommend the safest recovery action.

Allowed failure types:
- temporary_failure
- payment_method_problem
- unknown

Allowed actions:
- CREATE_PAYMENT_LINK
- UPDATE_PAYMENT_METHOD
- HUMAN_REVIEW
- STOP

BUSINESS LOGIC & DECISION MATRIX:
- IF failure_reason IS 'bank_technical_error' OR 'network_timeout':
  -> failure_type = 'temporary_failure'
  -> action = 'CREATE_PAYMENT_LINK' (Prompt user to retry via instant UPI/Netbanking link)

- IF failure_reason IS 'card_expired' OR 'invalid_cvv' OR 'insufficient_funds':
  -> failure_type = 'payment_method_problem'
  -> action = 'UPDATE_PAYMENT_METHOD' (Prompt user to update card details or select an alternative payment method)

- IF payment amount > 10000 OR attempt_count >= 3:
  -> failure_type = 'unknown'
  -> action = 'HUMAN_REVIEW' (High value transaction or safety boundary reached)

- IF customer has previously opted out (previous_opt_out == True):
  -> failure_type = 'unknown'
  -> action = 'STOP'

Rules:

1. Do not invent information.
2. If the situation is unclear, choose HUMAN_REVIEW.
3. Confidence must be between 0 and 1.
4. Do not execute any action.
5. Consider the payment amount, failure reason, attempt count, and customer history.
6. Give a short explanation for your decision.
"""
# Retry up to 3 times if Google returns a 503 spike
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AIDecision,
                }
            )
            return AIDecision.model_validate_json(response.text)
        except ServerError as e:
            if attempt == 2:
                raise e
            time.sleep(2)