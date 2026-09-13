import os
import json
import hmac
import hashlib

import requests
from dotenv import load_dotenv

load_dotenv()

secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

payload = {
    "event": "payment_link.paid",
    "payload": {
        "payment_link": {
            "entity": {
                "id": "plink_TbPYPRZaZBPDmU"
            }
        },
        "payment": {
            "entity": {
                "id": "pay_TbPbT90DoGNxXj"
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

headers = {
    "X-Razorpay-Signature": signature,
    "x-razorpay-event-id": "payment_link_test_001",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://127.0.0.1:8000/webhooks/razorpay",
    data=body,
    headers=headers
)

print()
print("========== PAYMENT LINK WEBHOOK TEST ==========")
print()
print("Status:", response.status_code)
print("Response:", response.json())