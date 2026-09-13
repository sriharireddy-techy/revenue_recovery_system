import os
import json
import hmac
import hashlib

import requests
from dotenv import load_dotenv

load_dotenv()

secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

payload = {
    "event": "payment.failed",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_test_auto_003",
                "status": "failed"
            }
        }
    }
}

body = json.dumps(payload, separators=(",", ":")).encode()

signature = hmac.new(
    secret.encode(),
    body,
    hashlib.sha256
).hexdigest()

event_id = "auto_case_test_003"

headers = {
    "X-Razorpay-Signature": signature,
    "x-razorpay-event-id": event_id,
    "Content-Type": "application/json"
}

response = requests.post(
    "http://127.0.0.1:8000/webhooks/razorpay",
    data=body,
    headers=headers
)

print()
print("========== WEBHOOK TEST ==========")
print()
print("Status:", response.status_code)
print("Response:", response.json())