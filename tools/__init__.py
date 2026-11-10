"""Tool registry: the one place that lists every tool the agent can use."""


from tools import calculator


TOOLS = {
    "calculator": calculator.calculator,
}

# JSON schemas sent to the LLM
TOOL_SCHEMAS = [
    calculator.SCHEMA,
]


def run_tool(name:str, args:dict) -> str:
    """Run a tool by name. Never raises: errors come back as text for the LLM."""
    func = TOOLS.get(name)
    if func is None:
        return f"Error: unknown tool '{name}'. Available: {', '.join(TOOLS)}"
    try:
        return str(func(**args))
    except TypeError as e:  # wrong or missing arguments
        return f"Error: bad arguments for {name}: {e}"
    except Exception as e:  # any other tool crash
        return f"Error: {name} failed: {e}"