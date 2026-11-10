"""One-off check: does Groq work with my key + model? Delete when done."""
import json

from groq import Groq

from config import settings

client = Groq(api_key=settings.groq_api_key.get_secret_value())

# --- Test 1: plain chat ---
resp = client.chat.completions.create(
    model=settings.model_name,
    messages=[{"role": "user", "content": "Say hi in 5 words."}],
    temperature=settings.temperature,
)
print("Test 1 reply:", resp.choices[0].message.content)
print("Tokens used:", resp.usage.total_tokens)

# --- Test 2: can this model call tools? ---
tools = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a math expression and return the result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "e.g. 4837 * 2961"}
            },
            "required": ["expression"],
        },
    },
}]

resp = client.chat.completions.create(
    model=settings.model_name,
    messages=[{"role": "user", "content": "What is 4837 * 2961? Use the calculator."}],
    tools=tools,
    tool_choice="auto",
    temperature=settings.temperature,
)

msg = resp.choices[0].message
if msg.tool_calls:
    call = msg.tool_calls[0]
    print("Test 2 PASSED, tool call:", call.function.name, json.loads(call.function.arguments))
else:
    print("Test 2 FAILED, no tool call. Model replied:", msg.content)



resp = client.