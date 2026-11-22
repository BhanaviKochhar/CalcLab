"""Exceptions raised by the calculator. All of them are safe to show to users."""


class CalcError(Exception):
    """Base class for every calculator error."""


class ParseError(CalcError):
    """The expression is not syntactically valid."""


class EvalError(CalcError):
    """The expression is valid but cannot be evaluated (e.g. division by zero)."""
