import unittest

from calclab.display import format_result


class TestFormatResult(unittest.TestCase):
    def test_whole_numbers(self):
        self.assertEqual(format_result(5), "5")
        self.assertEqual(format_result(5.0), "5")
        self.assertEqual(format_result(0.0), "0")

    def test_floats_are_trimmed(self):
        self.assertEqual(format_result(0.1 + 0.2), "0.3")
        self.assertEqual(format_result(1234.5), "1234.5")

    def test_scientific_notation_for_extremes(self):
        self.assertEqual(format_result(1e20), "1.000000e+20")
        self.assertEqual(format_result(1e-7), "1.000000e-07")


if __name__ == "__main__":
    unittest.main()
