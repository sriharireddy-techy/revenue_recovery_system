import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.database import SessionLocal
from backend.tools import (
    get_payment_details,
    get_customer_history
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


payment_function = types.FunctionDeclaration(
    name="get_payment_details",
    description="Get details about a payment using its payment ID.",
    parameters={
        "type": "object",
        "properties": {
            "payment_id": {
                "type": "string",
                "description": "The payment ID"
            }
        },
        "required": ["payment_id"]
    }
)


customer_function = types.FunctionDeclaration(
    name="get_customer_history",
    description="Get previous payment history for a customer.",
    parameters={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer ID"
            }
        },
        "required": ["customer_id"]
    }
)


tools = types.Tool(
    function_declarations=[
        payment_function,
        customer_function
    ]
)
config = types.GenerateContentConfig(
    tools=[tools],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    )
)
def execute_tool(name, arguments):

    db = SessionLocal()

    try:

        if name == "get_payment_details":

            return get_payment_details(
                db,
                arguments["payment_id"]
            )

        if name == "get_customer_history":

            return get_customer_history(
                db,
                arguments["customer_id"]
            )

        return {
            "error": f"Unknown tool: {name}"
        }

    finally:
        db.close()
        
         
def generate_with_retry(contents):

    for attempt in range(3):

        try:
            return client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config=config
            )

        except Exception as e:

            if "503" not in str(e):
                raise

            print(
                f"Gemini temporarily unavailable. "
                f"Retry {attempt + 1}/3..."
            )

            time.sleep(3)

    raise RuntimeError(
        "Gemini remained unavailable after 3 attempts."
    )

def ask_agent(payment_id: str):

    prompt = f"""
You are an AI payment recovery agent.

Investigate this payment:

Payment ID: {payment_id}

Use the available tools to investigate the payment.

Your process:

1. Get the payment details.
2. Identify the customer.
3. Get the customer's payment history if useful.
4. Analyze the situation.
5. Give a final explanation.

Do not invent information.

Do not perform any payment action.
You are currently in investigation mode only.
"""

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt)
            ]
        )
    ]

    # Keep asking Gemini until it gives a final text response
    while True:

        response = generate_with_retry(contents)

        # Gemini has finished reasoning
        if not response.function_calls:

            return response

        # Add Gemini's function-call response
        contents.append(
            response.candidates[0].content
        )

        # Execute every requested function
        for function_call in response.function_calls:

            print()
            print(
                f"Agent requested tool: {function_call.name}"
            )

            print(
                f"Arguments: {function_call.args}"
            )

            result = execute_tool(
                function_call.name,
                function_call.args
            )

            print(
                f"Tool result: {result}"
            )

            # Send tool result back to Gemini
            function_response_part = (
                types.Part.from_function_response(
                    name=function_call.name,
                    response={
                        "result": result
                    }
                )
            )

            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        function_response_part
                    ]
                )
            )
    # Ask Gemini to continue using the tool results
    final_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents,
        config=config
    )

    return final_response