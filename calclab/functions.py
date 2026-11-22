"""Function and constant registry used by the evaluator."""
import math


def _factorial(x):
    if x != int(x) or x < 0:
        raise ValueError("needs a non-negative whole number")
    if x > 500:
        raise ValueError("argument is too large")
    return math.factorial(int(x))


def _tan(x):
    result = math.tan(x)
    if abs(result) > 1e12:
        raise ValueError("tangent is undefined for this angle")
    return result


FUNCTIONS = {
    "abs": abs,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": _tan,
    "ln": lambda x: math.log(x),
    "log": math.log10,
    "fact": _factorial,
}

# Functions whose argument is an angle (converted to radians in degree mode).
ANGLE_FUNCTIONS = {"sin", "cos", "tan"}

CONSTANTS = {"pi": math.pi, "e": math.e}
