"""The agent loop: LLM -> tool calls -> results -> LLM ... -> final answer."""


import json
import logging

from groq import Groq

from config import settings
from prompts import SYSTEM_PROMPT
from tools import TOOL_SCHEMAS, run_tool


log = logging.getLogger("agent")

# max_retries: the SDK retries 429 (rate limit) and 5xx errors with backoff
client = Groq(
    api_key=settings.groq_api_key.get_secret_value(),
    timeout=60,
    max_retries=3,
)

def run_agent(question: str) -> str:
    """Answer one question, calling tools as needed. Returns the final text."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    log.info("QUESTION: %s", question)

    for step in range(1, settings.max_steps + 1):
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=settings.temperature,
        )
        msg = response.choices[0].message
        # print(f"\n--- step {step} ---")
        # print(msg.model_dump_json(indent=2, exclude_none=True))

        # 1) No tool calls -> this is the final answer
        if not msg.tool_calls:
            log.info("step %d: FINAL ANSWER: %s", step, msg.content)
            return msg.content or ""

        # 2) Save the assistant's tool request in the history
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })

        # 3) Run each tool and add its result, linked by tool_call_id
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                result = "Error: arguments were not valid JSON. Send valid JSON and try again."
            else:
                result = run_tool(name, args)

            log.info("step %d: TOOL %s(%s) -> %s", step, name, tc.function.arguments, result[:500])
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    log.warning("Stopped after %d steps without a final answer", settings.max_steps)
    return f"Sorry, I couldn't finish within {settings.max_steps} steps."