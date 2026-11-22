import unittest

from calclab.engine import evaluate, tokenize
from calclab.errors import EvalError, ParseError


class TestTokenizer(unittest.TestCase):
    def test_tokens(self):
        kinds = [t.kind for t in tokenize("2*(3+x)")]
        self.assertEqual(kinds, ["num", "op", "op", "num", "op", "name", "op"])

    def test_illegal_character_reports_position(self):
        with self.assertRaises(ParseError) as ctx:
            tokenize("2 + $")
        self.assertIn("position 5", str(ctx.exception))


class TestArithmetic(unittest.TestCase):
    def test_precedence_and_brackets(self):
        self.assertEqual(evaluate("2 + 3 * 4"), 14)
        self.assertEqual(evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(evaluate("10 - 4 - 3"), 3)          # left associative
        self.assertEqual(evaluate("2 ^ 3 ^ 2"), 512)         # right associative
        self.assertEqual(evaluate("2 ** 3"), 8)

    def test_unary_minus_binds_looser_than_power(self):
        self.assertEqual(evaluate("-2 ^ 2"), -4)
        self.assertEqual(evaluate("2 ^ -1"), 0.5)
        self.assertEqual(evaluate("--3"), 3)

    def test_decimals_modulo_and_division(self):
        self.assertAlmostEqual(evaluate("0.1 + 0.2"), 0.3)
        self.assertEqual(evaluate(".5 * 4"), 2.0)
        self.assertEqual(evaluate("17 % 5"), 2)
        self.assertEqual(evaluate("7 / 2"), 3.5)

    def test_abs_function(self):
        self.assertEqual(evaluate("abs(-7) + abs(2)"), 9)

    def test_large_integers_become_floats(self):
        self.assertIsInstance(evaluate("10 ^ 20"), float)
        self.assertEqual(evaluate("10 ^ 15"), 10**15)


class TestErrors(unittest.TestCase):
    def assertEvalError(self, text, fragment):
        with self.assertRaises(EvalError) as ctx:
            evaluate(text)
        self.assertIn(fragment, str(ctx.exception))

    def assertParseError(self, text, fragment):
        with self.assertRaises(ParseError) as ctx:
            evaluate(text)
        self.assertIn(fragment, str(ctx.exception))

    def test_division_by_zero(self):
        self.assertEvalError("1 / 0", "Division by zero")
        self.assertEvalError("5 % 0", "Division by zero")
        self.assertEvalError("0 ^ -1", "Division by zero")

    def test_unknown_names(self):
        self.assertEvalError("foo(1)", "Unknown function 'foo'")
        self.assertEvalError("x + 1", "Unknown name 'x'")

    def test_bad_syntax(self):
        self.assertParseError("", "Empty")
        self.assertParseError("2 +", "end of expression")
        self.assertParseError("(1 + 2", "Expected ')'")
        self.assertParseError("1 2", "Unexpected '2'")
        self.assertParseError("2 $ 3", "Unexpected character")

    def test_resource_limits(self):
        self.assertParseError("1+" * 300 + "1", "too long")
        self.assertParseError("(" * 240 + "1" + ")" * 240, "deeply nested")
        self.assertEvalError("2 ^ 100000", "Exponent is too large")
        self.assertEvalError("(0 - 8) ^ 0.5", "not a real number")

    def test_never_executes_code(self):
        self.assertParseError("__import__('os').system('echo hacked')", "Unexpected character")


if __name__ == "__main__":
    unittest.main()
