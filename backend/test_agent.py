from backend.agent import ask_agent
response = ask_agent("pay_test_123")

print()
print("================================")
print("       FINAL AGENT RESPONSE")
print("================================")
print()

print(response.text)