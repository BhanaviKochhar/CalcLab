"""Command-line REPL: ``python -m calclab``."""
from . import __version__
from .engine import evaluate
from .errors import CalcError
from .utils import format_number


def main():
    print(f"CalcLab {__version__} - type an expression, or 'quit' to exit")
    while True:
        try:
            line = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in {"quit", "exit"}:
            break
        if not line:
            continue
        try:
            print(format_number(evaluate(line)))
        except CalcError as exc:
            print(f"Error: {exc}")
