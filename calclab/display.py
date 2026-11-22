"""Result formatting shared by the API and the CLI."""

def format_result(value, group=False):
    """Format a number for display.

    Whole numbers lose their trailing ``.0``; other floats keep at most 10 significant
    digits and switch to scientific notation for very large or very small magnitudes.
    With ``group=True`` a thousands separator is inserted (1,234,567).
    """
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        value = int(value)
    if isinstance(value, int):
        return f"{value:,}" if group else str(value)
    if value != 0 and (abs(value) >= 1e15 or abs(value) < 1e-6):
        return f"{value:.6e}"
    return f"{value:,.10g}" if group else f"{value:.10g}"