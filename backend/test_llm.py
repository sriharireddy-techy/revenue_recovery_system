from backend.llm import ask_llm
result = ask_llm(
    "Explain what a failed payment means in one sentence."
)

print(result)