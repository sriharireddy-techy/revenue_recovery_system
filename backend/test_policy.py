from backend.policy import validate_decision


tests = [
    (
        "Captured payment",
        validate_decision(
            "CREATE_PAYMENT_LINK",
            0.95,
            2499,
            1,
            "captured"
        ),
        "STOP"
    ),
    (
        "High amount",
        validate_decision(
            "CREATE_PAYMENT_LINK",
            0.95,
            15000,
            1,
            "failed"
        ),
        "HUMAN_REVIEW"
    ),
    (
        "Low confidence",
        validate_decision(
            "CREATE_PAYMENT_LINK",
            0.60,
            2499,
            1,
            "failed"
        ),
        "HUMAN_REVIEW"
    ),
    (
        "Too many attempts",
        validate_decision(
            "CREATE_PAYMENT_LINK",
            0.95,
            2499,
            2,
            "failed"
        ),
        "HUMAN_REVIEW"
    ),
    (
        "Successful recovery",
        validate_decision(
            "CREATE_PAYMENT_LINK",
            0.95,
            2499,
            1,
            "failed",
            "SUCCESS"
        ),
        "STOP"
    ),
    (
        "Valid recovery",
        validate_decision(
            "CREATE_PAYMENT_LINK",
            0.95,
            2499,
            1,
            "failed"
        ),
        "CREATE_PAYMENT_LINK"
    )
]


print()
print("========== POLICY TEST ==========")
print()

passed = 0

for name, result, expected in tests:

    if result == expected:
        print("PASS:", name)
        passed += 1
    else:
        print("FAIL:", name)
        print("Expected:", expected)
        print("Got:", result)

print()
print(f"{passed}/{len(tests)} tests passed")