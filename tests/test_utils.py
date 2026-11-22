import unittest

from calclab.utils import format_number


class TestFormatNumber(unittest.TestCase):
    def test_integers_and_whole_floats(self):
        self.assertEqual(format_number(5), "5")
        self.assertEqual(format_number(5.0), "5")

    def test_floats_are_trimmed(self):
        self.assertEqual(format_number(0.1 + 0.2), "0.3")
        self.assertEqual(format_number(2.5), "2.5")

    def test_huge_floats_use_exponent(self):
        self.assertEqual(format_number(1e20), "1e+20")


if __name__ == "__main__":
    unittest.main()
