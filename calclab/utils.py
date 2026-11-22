"""Small helpers shared across the package."""


def format_number(value):
    """Format a number for display: no trailing '.0', at most 10 significant digits."""
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)
