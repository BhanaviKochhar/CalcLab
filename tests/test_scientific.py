import math
import unittest

from calclab.api import create_app
from calclab.engine import evaluate
from calclab.errors import EvalError


class TestFunctionsAndConstants(unittest.TestCase):
    def test_basic_functions(self):
        self.assertEqual(evaluate("sqrt(16)"), 4)
        self.assertEqual(evaluate("log(1000)"), 3)
        self.assertAlmostEqual(evaluate("ln(e)"), 1)
        self.assertEqual(evaluate("fact(5)"), 120)

    def test_constants(self):
        self.assertAlmostEqual(evaluate("pi"), math.pi)
        self.assertAlmostEqual(evaluate("2 * pi"), 2 * math.pi)

    def test_domain_errors_become_calc_errors(self):
        for text in ("sqrt(0 - 1)", "ln(0)", "fact(2.5)", "fact(0 - 1)", "fact(1000)"):
            with self.subTest(text=text):
                with self.assertRaises(EvalError):
                    evaluate(text)

    def test_wrong_argument_count(self):
        with self.assertRaises(EvalError):
            evaluate("sqrt(1, 2)")


class TestAngleModes(unittest.TestCase):
    def test_radians_is_the_default(self):
        self.assertEqual(evaluate("sin(0)"), 0)
        self.assertEqual(evaluate("sin(pi / 2)"), 1.0)

    def test_degrees(self):
        self.assertEqual(evaluate("sin(90)", angle_mode="deg"), 1.0)
        self.assertEqual(evaluate("cos(180)", angle_mode="deg"), -1.0)
        self.assertEqual(evaluate("sin(180)", angle_mode="deg"), 0.0)
        self.assertEqual(evaluate("tan(45)", angle_mode="deg"), 1.0)

    def test_tangent_undefined(self):
        with self.assertRaises(EvalError):
            evaluate("tan(90)", angle_mode="deg")
        with self.assertRaises(EvalError):
            evaluate("tan(pi / 2)")

    def test_invalid_mode(self):
        with self.assertRaises(EvalError):
            evaluate("1 + 1", angle_mode="grad")


class TestScientificApi(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_angle_mode_round_trip(self):
        res = self.client.post("/api/evaluate", json={"expression": "sin(90)", "angle_mode": "deg"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["result"], 1.0)
        self.assertEqual(data["angle_mode"], "deg")

    def test_invalid_angle_mode_is_400(self):
        res = self.client.post("/api/evaluate", json={"expression": "1", "angle_mode": "x"})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
