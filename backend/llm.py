import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from your environment or .env file!")

client = genai.Client(api_key=api_key)

def ask_llm(prompt: str):
    # Create a single-use chat session to satisfy the SDK architecture
    chat = client.chats.create(model="gemini-3.6-flash")
    
    # Send the message through the chat session to stop the AFC warning
    response = chat.send_message(prompt)
    
    return response.text
