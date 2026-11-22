"""Function and constant registry used by the evaluator."""


def _average(*values):
    if not values:
        raise ValueError("needs at least one value")
    return sum(values) / len(values)


FUNCTIONS = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "avg": _average,
}

CONSTANTS = {}
