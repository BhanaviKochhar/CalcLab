"""Result formatting shared by the API and the CLI."""


def format_result(value):
    """Format a number for display.

    Whole numbers lose their trailing ``.0``; other floats keep at most 10 significant
    digits and switch to scientific notation for very large or very small magnitudes.
    """
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    if isinstance(value, float) and value != 0 and (abs(value) >= 1e15 or abs(value) < 1e-6):
        return f"{value:.6e}"
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)
