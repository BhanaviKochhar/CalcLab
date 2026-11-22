"""Tokenizer, recursive-descent parser and evaluator for arithmetic expressions.

Grammar (lowest to highest precedence)::

    expr    := term (('+' | '-') term)*
    term    := unary (('*' | '/' | '%') unary)*
    unary   := ('-' | '+') unary | power
    power   := primary (('^' | '**') unary)?
    primary := NUMBER | NAME '(' [expr (',' expr)*] ')' | NAME | '(' expr ')'

No call to ``eval`` is ever made, so untrusted input is safe to process.
"""
import math
import re
from dataclasses import dataclass

from .errors import EvalError, ParseError
from .functions import CONSTANTS, FUNCTIONS

MAX_LENGTH = 500
MAX_EXPONENT = 1000

_TOKEN_RE = re.compile(r"\s*(?:(\d+\.?\d*|\.\d+)|([A-Za-z_]\w*)|(\*\*|[-+*/^%(),]))")


@dataclass(frozen=True)
class Token:
    kind: str  # "num", "name" or "op"
    value: str
    pos: int


def tokenize(text):
    """Split *text* into tokens, raising ParseError on illegal characters."""
    tokens = []
    pos = 0
    while pos < len(text):
        if text[pos:].isspace():
            break
        match = _TOKEN_RE.match(text, pos)
        if not match:
            bad = len(text) - len(text[pos:].lstrip())
            raise ParseError(f"Unexpected character {text[bad]!r} at position {bad + 1}")
        number, name, op = match.groups()
        if number is not None:
            kind, value = "num", number
        elif name is not None:
            kind, value = "name", name
        else:
            kind, value = "op", op
        tokens.append(Token(kind, value, match.start(match.lastindex)))
        pos = match.end()
    return tokens


class Parser:
    """Recursive-descent parser that builds a small tuple-based syntax tree."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def parse(self):
        node = self._expr()
        extra = self._peek()
        if extra is not None:
            raise ParseError(f"Unexpected '{extra.value}' at position {extra.pos + 1}")
        return node

    def _peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def _accept(self, *ops):
        tok = self._peek()
        if tok is not None and tok.kind == "op" and tok.value in ops:
            self.index += 1
            return tok.value
        return None

    def _expect(self, op):
        if self._accept(op) is None:
            tok = self._peek()
            where = "end of expression" if tok is None else f"'{tok.value}' at position {tok.pos + 1}"
            raise ParseError(f"Expected '{op}' but found {where}")

    def _expr(self):
        node = self._term()
        while (op := self._accept("+", "-")):
            node = ("bin", op, node, self._term())
        return node

    def _term(self):
        node = self._unary()
        while (op := self._accept("*", "/", "%")):
            node = ("bin", op, node, self._unary())
        return node

    def _unary(self):
        op = self._accept("-", "+")
        if op == "-":
            return ("neg", self._unary())
        if op == "+":
            return self._unary()
        return self._power()

    def _power(self):
        base = self._primary()
        if self._accept("^", "**"):
            return ("bin", "^", base, self._unary())
        return base

    def _primary(self):
        tok = self._peek()
        if tok is None:
            raise ParseError("Unexpected end of expression")
        if tok.kind == "num":
            self.index += 1
            return ("num", float(tok.value) if "." in tok.value else int(tok.value))
        if tok.kind == "name":
            self.index += 1
            if self._accept("("):
                args = []
                if self._accept(")") is None:
                    args.append(self._expr())
                    while self._accept(","):
                        args.append(self._expr())
                    self._expect(")")
                return ("call", tok.value, args)
            return ("const", tok.value)
        if self._accept("("):
            node = self._expr()
            self._expect(")")
            return node
        raise ParseError(f"Unexpected '{tok.value}' at position {tok.pos + 1}")


def _call(func, name, values):
    try:
        return func(*values)
    except TypeError:
        raise EvalError(f"Invalid arguments for '{name}'")
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise EvalError(f"Math error in '{name}': {exc}")


def _binary(op, a, b):
    try:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return a / b
        if op == "%":
            return a % b
        if abs(b) > MAX_EXPONENT:
            raise EvalError("Exponent is too large")
        result = a ** b
    except ZeroDivisionError:
        raise EvalError("Division by zero")
    except OverflowError:
        raise EvalError("Result is too large")
    if isinstance(result, complex):
        raise EvalError("Result is not a real number")
    return result


def _eval(node, ctx):
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "const":
        name = node[1]
        if name in CONSTANTS:
            return CONSTANTS[name]
        raise EvalError(f"Unknown name '{name}'")
    if kind == "neg":
        return -_eval(node[1], ctx)
    if kind == "call":
        _, name, args = node
        func = FUNCTIONS.get(name)
        if func is None:
            raise EvalError(f"Unknown function '{name}'")
        values = [_eval(arg, ctx) for arg in args]
        return _call(func, name, values)
    _, op, left, right = node
    return _binary(op, _eval(left, ctx), _eval(right, ctx))


def _normalise(result):
    """Turn very large ints into floats and reject non-finite numbers."""
    try:
        if isinstance(result, int) and abs(result) > 10**15:
            result = float(result)
    except OverflowError:
        raise EvalError("Result is too large")
    if isinstance(result, float) and (math.isinf(result) or math.isnan(result)):
        raise EvalError("Result is not a finite number")
    return result


def evaluate(expression):
    """Parse and evaluate an arithmetic expression and return an int or float."""
    if not isinstance(expression, str) or not expression.strip():
        raise ParseError("Empty expression")
    if len(expression) > MAX_LENGTH:
        raise ParseError("Expression is too long")
    ctx = {}
    try:
        tree = Parser(tokenize(expression)).parse()
        result = _eval(tree, ctx)
    except RecursionError:
        raise ParseError("Expression is too deeply nested")
    return _normalise(result)
