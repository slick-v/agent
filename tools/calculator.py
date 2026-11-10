# THE TOOL

import ast
import math
import operator

# ALLOWED OPERATORS: + - * / // % ** and unary -x / +x

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}
# Allowed functions and constants
_FUNCS = {
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "abs": abs, "round": round, "min": min, "max": max,
}
_CONSTS = {"pi": math.pi, "e": math.e}

MAX_EXPR_LEN = 200
MAX_EXPONENT = 1000  # stops things like 9**9**9 from freezing the program

def _eval(node):
    # Numbers
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    # Constants like pi
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    # a + b, a * b, ...
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError("exponent too large")
        return _BIN_OPS[type(node.op)](left, right)
    # -x
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    # sqrt(x), round(x, 2), ...
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCS and not node.keywords):
        return _FUNCS[node.func.id](*[_eval(arg) for arg in node.args])
    raise ValueError(f"'{ast.unparse(node)}' is not allowed (numbers, operators and listed functions only)")


def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result as text."""
    expression = expression.strip().replace("^", "**")
    if len(expression) > MAX_EXPR_LEN:
        return f"Error: expression longer than {MAX_EXPR_LEN} characters"
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval(tree.body)
    except ZeroDivisionError:
        return "Error: division by zero"
    except (SyntaxError, ValueError, TypeError, OverflowError) as e:
        return f"Error: {e}"
    # 12.0 -> "12", keep real decimals
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return str(result)


SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "Evaluate a math expression exactly. Use for multi-digit or multi-step "
            "arithmetic, percentages, powers and roots. Supports + - * / // % ** "
            "and sqrt, log, log10, sin, cos, tan, abs, round, min, max, pi, e."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression, e.g. '4837 * 2961' or '0.185 * 73420'",
                }
            },
            "required": ["expression"],
        },
    },
}
