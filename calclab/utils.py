"""Small helpers shared across the package."""


def format_number(value, group=False):
    """Format a number for display: no trailing '.0', at most 10 significant digits.

    With ``group=True`` a thousands separator is inserted (1,234,567).
    """
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        value = int(value)
    if isinstance(value, int):
        return f"{value:,}" if group else str(value)
    return f"{value:,.10g}" if group else f"{value:.10g}"
